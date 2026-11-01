from __future__ import annotations
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
from src.config import STATUS, COMPLETED, CLUSTER_FEATURES

def eligible_rides(frame: pd.DataFrame) -> pd.DataFrame:
    x = frame.loc[frame[STATUS].eq(COMPLETED), CLUSTER_FEATURES].copy()
    for c in CLUSTER_FEATURES: x[c] = pd.to_numeric(x[c], errors="coerce")
    return x.dropna()

def run_kmeans(frame: pd.DataFrame, k: int=3, max_rows: int=30000) -> dict:
    x = eligible_rides(frame)
    if not 2 <= k <= 6: raise ValueError("Choose between 2 and 6 clusters.")
    if len(x) < max(20, k + 2): raise ValueError(f"Need at least {max(20,k+2)} complete completed rides; found {len(x)}.")
    if len(x) > max_rows: x = x.sample(max_rows, random_state=42)
    scaled = StandardScaler().fit_transform(x)
    if np.unique(scaled, axis=0).shape[0] < k: raise ValueError("Not enough distinct numeric records for this cluster count.")
    model = KMeans(n_clusters=k, random_state=42, n_init=10).fit(scaled)
    labels = model.labels_
    profile = x.assign(Cluster=[f"Cluster {i+1}" for i in labels]).groupby("Cluster").agg(["mean", "count"])
    profile.columns = [" ".join(c).strip() for c in profile.columns]; profile = profile.reset_index()
    sil = float(silhouette_score(scaled, labels, sample_size=min(10000,len(x)), random_state=42)) if len(x)>k else None
    return {"data":x.assign(Cluster=[f"Cluster {i+1}" for i in labels]), "profile":profile, "inertia":float(model.inertia_), "silhouette":sil, "davies_bouldin":float(davies_bouldin_score(scaled,labels)), "sample_size":len(x), "sampled": len(eligible_rides(frame)) > len(x)}
