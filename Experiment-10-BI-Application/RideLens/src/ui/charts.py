import plotly.express as px
COLORS=["#1D4ED8","#14B8A6","#F59E0B","#EF4444","#8B5CF6","#64748B"]
def bar(data,x,y,title,orientation=None):
    return px.bar(data,x=x,y=y,orientation=orientation,title=title,color_discrete_sequence=COLORS).update_layout(template="plotly_white",margin=dict(l=10,r=10,t=45,b=10),legend_title_text="")
def line(data,x,y,title,color=None):
    return px.line(data,x=x,y=y,color=color,title=title,markers=True,color_discrete_sequence=COLORS).update_layout(template="plotly_white",margin=dict(l=10,r=10,t=45,b=10))
