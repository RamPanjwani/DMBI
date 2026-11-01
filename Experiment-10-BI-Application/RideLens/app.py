from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from src.config import DEFAULT_DATASET, DATE, STATUS, VEHICLE, PICKUP, DROP
from src.data.load import read_csv
from src.data.filters import apply_filters
from src.analytics.metrics import overview_metrics, grouped_counts, safe_rate
from src.analytics.clustering import run_kmeans
from src.analytics.association import run_apriori
from src.analytics.insights import generate_insights
from src.ui.charts import bar, line, COLORS
from src.ui.exports import safe_csv

st.set_page_config(page_title="RideLens", page_icon="◈", layout="wide")
st.markdown("""<style>.block-container{padding-top:1.6rem}.rl-title{font-size:2.2rem;font-weight:750;color:#172033}.rl-sub{color:#526075;margin-top:-.7rem}.stMetric{background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:10px}</style>""",unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading local bookings…")
def load_default(path: str): return read_csv(path)
@st.cache_data(show_spinner="Reading uploaded CSV…")
def load_upload(contents: bytes):
    import io
    return read_csv(io.BytesIO(contents))

def dataframe_download(frame, label, name):
    st.download_button(label, safe_csv(frame), file_name=name, mime="text/csv")

def empty(): st.info("No bookings match these filters. Adjust your selection or reset filters.")

def sidebar(frame):
    st.sidebar.title("RideLens")
    st.sidebar.caption("Local ride operations intelligence")
    dates=frame[DATE].dropna()
    if dates.empty: return frame
    default=(dates.min().date(),dates.max().date())
    dr=st.sidebar.date_input("Date range",value=default,min_value=default[0],max_value=default[1])
    if not isinstance(dr,tuple) or len(dr)!=2: dr=default
    options=lambda c: sorted(frame[c].dropna().unique().tolist())
    vehicle=st.sidebar.multiselect("Vehicle type",options(VEHICLE))
    statuses=st.sidebar.multiselect("Booking status",options(STATUS))
    pickups=st.sidebar.multiselect("Pickup location",options(PICKUP))
    drops=st.sidebar.multiselect("Drop location",options(DROP))
    st.sidebar.caption("Descriptive pages use these filters. Mining uses them only when enabled.")
    return apply_filters(frame,*dr,vehicle,statuses,pickups,drops)

def metric_cols(m):
    a,b,c,d=st.columns(4)
    a.metric("Booking records",f"{m['total']:,}")
    b.metric("Completed",f"{m['completed']:,}",None if m['completion_rate'] is None else f"{m['completion_rate']:.1%} of visible")
    c.metric("Cancellation outcomes",f"{m['cancelled']:,}",None if m['cancellation_rate'] is None else f"{m['cancellation_rate']:.1%} of visible")
    d.metric("Recorded completed value","—" if m['completed_value'] is None else f"{m['completed_value']:,.0f}","Completed rows only")

def overview(data):
    m=overview_metrics(data); metric_cols(m)
    if data.empty: return empty()
    left,right=st.columns(2)
    status=grouped_counts(data,STATUS)
    left.plotly_chart(bar(status,"Bookings",STATUS,"Booking status distribution","h"),use_container_width=True)
    daily=data.groupby(DATE).size().rename("Bookings").reset_index()
    right.plotly_chart(line(daily,DATE,"Bookings","Bookings over time"),use_container_width=True)
    st.caption("All metrics use visible booking records. Recorded value excludes non-completed rows and missing values; it is not confirmed revenue.")
    dataframe_download(status,"Download status summary","ridelens_status_summary.csv")

def bookings(data):
    if data.empty: return empty()
    a,b=st.columns(2)
    a.plotly_chart(bar(grouped_counts(data,VEHICLE),VEHICLE,"Bookings","Bookings by vehicle type"),use_container_width=True)
    b.plotly_chart(bar(grouped_counts(data,PICKUP,12),"Bookings",PICKUP,"Top pickup locations","h"),use_container_width=True)
    c,d=st.columns(2)
    c.plotly_chart(bar(grouped_counts(data,DROP,12),"Bookings",DROP,"Top drop locations","h"),use_container_width=True)
    table=data.groupby([VEHICLE,STATUS]).size().rename("Bookings").reset_index()
    d.plotly_chart(bar(table,VEHICLE,"Bookings","Vehicle/status comparison",STATUS),use_container_width=True)
    dataframe_download(table,"Download vehicle-status table","ridelens_vehicle_status.csv")

def values(data):
    rides=data[data[STATUS].eq("Completed")].copy()
    if rides.empty: return st.info("No completed rides in the visible selection; value analysis is unavailable.")
    for c in ["Booking Value","Ride Distance","Avg VTAT","Avg CTAT"]: rides[c]=pd.to_numeric(rides.get(c),errors="coerce")
    a,b,c=st.columns(3); a.metric("Average recorded value",f"{rides['Booking Value'].mean():,.2f}" if rides['Booking Value'].notna().any() else "—"); b.metric("Mean ride distance",f"{rides['Ride Distance'].mean():.2f}" if rides['Ride Distance'].notna().any() else "—"); c.metric("Value observations",f"{rides['Booking Value'].notna().sum():,}")
    x,y=st.columns(2)
    x.plotly_chart(px.histogram(rides,x="Booking Value",nbins=35,title="Completed booking value distribution",color_discrete_sequence=COLORS).update_layout(template="plotly_white"),use_container_width=True)
    y.plotly_chart(px.scatter(rides.sample(min(10000,len(rides)),random_state=42),x="Ride Distance",y="Booking Value",color=VEHICLE,title="Distance versus recorded value",opacity=.45,color_discrete_sequence=COLORS).update_layout(template="plotly_white"),use_container_width=True)
    dataframe_download(rides[[VEHICLE,"Booking Value","Ride Distance","Avg VTAT","Avg CTAT"]],"Download completed-rides analysis","ridelens_completed_value.csv")

def cancellations(data):
    if data.empty: return empty()
    cancel=data[data[STATUS].isin(["Cancelled by Driver","Cancelled by Customer","No Driver Found"])]
    st.caption(f"Cancellation rates below use all visible booking records as denominators (n={len(data):,}).")
    rate=data.groupby(VEHICLE).apply(lambda g: pd.Series({"Bookings":len(g),"Cancellation outcomes":g[STATUS].isin(["Cancelled by Driver","Cancelled by Customer","No Driver Found"]).sum()}),include_groups=False).reset_index()
    rate["Cancellation rate"]=rate["Cancellation outcomes"]/rate["Bookings"]
    a,b=st.columns(2); a.plotly_chart(bar(rate,VEHICLE,"Cancellation rate","Cancellation rate by vehicle"),use_container_width=True)
    reason_cols=[("Reason for cancelling by Customer","Customer cancellation reasons"),("Driver Cancellation Reason","Driver cancellation reasons"),("Incomplete Rides Reason","Incomplete ride reasons")]
    b.write("#### Outcome mix"); b.dataframe(grouped_counts(cancel,STATUS),hide_index=True,use_container_width=True)
    for col,title in reason_cols:
        if col in data and data[col].notna().any(): st.plotly_chart(bar(grouped_counts(data[data[col].notna()],col,12),"Bookings",col,title,"h"),use_container_width=True)
    dataframe_download(rate,"Download cancellation rates","ridelens_cancellation_rates.csv")

def clustering(data):
    use=st.toggle("Apply current filters to clustering",False,key="cluster_filter"); source=data if use else st.session_state.full_data
    k=st.slider("Number of clusters",2,6,3)
    if st.button("Run K-Means",type="primary"):
        try: st.session_state.cluster_result=run_kmeans(source,k)
        except ValueError as e: st.error(str(e)); return
    r=st.session_state.get("cluster_result")
    if not r: return st.info("K-Means runs only on completed rides with valid arrival times, value, and distance. Choose settings and run it.")
    a,b,c,d=st.columns(4); a.metric("Eligible completed rides",f"{r['sample_size']:,}"); b.metric("Inertia",f"{r['inertia']:,.0f}"); c.metric("Silhouette",f"{r['silhouette']:.3f}" if r['silhouette'] is not None else "—"); d.metric("Davies–Bouldin",f"{r['davies_bouldin']:.3f}")
    if r['silhouette'] is not None and r['silhouette'] < .25: st.warning("The silhouette score indicates weak separation. Treat these as exploratory profiles, not natural or ranked groups.")
    plot=r['data'].sample(min(8000,len(r['data'])),random_state=42)
    st.plotly_chart(px.scatter(plot,x="Ride Distance",y="Booking Value",color="Cluster",hover_data=["Avg VTAT","Avg CTAT"],title="Exploratory projection: distance versus value",color_discrete_sequence=COLORS).update_layout(template="plotly_white"),use_container_width=True)
    st.dataframe(r['profile'],hide_index=True,use_container_width=True); dataframe_download(r['profile'],"Download cluster profiles","ridelens_cluster_profiles.csv")

def associations(data):
    use=st.toggle("Apply current filters to association mining",False,key="assoc_filter"); source=data if use else st.session_state.full_data
    a,b,c=st.columns(3); support=a.slider("Minimum support",.005,.10,.02,.005); confidence=b.slider("Minimum confidence",.10,.90,.30,.05); lift=c.slider("Minimum display lift",1.0,3.0,1.0,.05)
    if st.button("Run Apriori",type="primary"):
        try: st.session_state.assoc_result=run_apriori(source,support,confidence,lift)
        except ValueError as e: st.error(str(e)); return
    result=st.session_state.get("assoc_result")
    if not result: return st.info("Apriori mines categorical co-occurrence from booking records. It does not establish causation.")
    items,rules,n=result; st.caption(f"Analyzed {n:,} booking transactions (deterministic sample when input exceeds 50,000).")
    st.write("#### Frequent itemsets"); st.dataframe(items.assign(itemsets=items['itemsets'].map(lambda s:" • ".join(sorted(s)))) if not items.empty else items,hide_index=True,use_container_width=True)
    st.write("#### Association rules")
    if rules.empty: st.info("No rules meet these thresholds. Lower support or confidence cautiously."); return
    show=rules[["antecedents","consequents","support","confidence","lift"]]; st.dataframe(show,hide_index=True,use_container_width=True)
    st.plotly_chart(px.scatter(show,x="support",y="confidence",size="lift",color="lift",hover_data=["antecedents","consequents"],title="Rule support and confidence").update_layout(template="plotly_white"),use_container_width=True)
    st.caption("Lift close to 1 indicates little association beyond base rates; association is not causation."); dataframe_download(show,"Download association rules","ridelens_association_rules.csv")

def insights(data):
    for t in generate_insights(data): st.info(t)
    st.markdown("""### Methods and boundaries
RideLens is a local, descriptive educational application using a supplied historical Uber-themed NCR dataset. One CSV row is retained as one record because Booking IDs repeat. Date, vehicle, status, pickup, and drop filters affect descriptive pages. Mining uses the full dataset unless explicitly toggled. No identifiers are shown or exported by default, no data is sent externally, and neither clustering nor rules prove causes or make predictions.""")

try:
    upload=st.sidebar.file_uploader("Use a compatible CSV instead",type="csv")
    frame, report = load_upload(upload.getvalue()) if upload else load_default(str(DEFAULT_DATASET))
except ValueError as exc:
    st.error(f"Dataset validation failed: {exc}"); st.stop()
except FileNotFoundError:
    st.error("Default dataset was not found. Place ncr_ride_bookings.csv in data/raw or upload a compatible CSV."); st.stop()
st.session_state.full_data=frame
filtered=sidebar(frame)
st.markdown("<div class='rl-title'>RideLens</div><div class='rl-sub'>Ride operations intelligence • historical local data • no external services</div>",unsafe_allow_html=True)
st.caption(f"Source: {'uploaded CSV' if upload else 'built-in NCR CSV'} · {len(frame):,} rows · {frame[DATE].min().date() if frame[DATE].notna().any() else 'unknown'} to {frame[DATE].max().date() if frame[DATE].notna().any() else 'unknown'} · visible: {len(filtered):,}")
for warning in report.warnings: st.warning(warning)
page=st.radio("Navigate",["Overview","Booking analytics","Value & operations","Cancellations","K-Means clustering","Apriori rules","Insights & methods"],horizontal=True,label_visibility="collapsed")
{"Overview":overview,"Booking analytics":bookings,"Value & operations":values,"Cancellations":cancellations,"K-Means clustering":clustering,"Apriori rules":associations,"Insights & methods":insights}[page](filtered)
