from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score

path = Path("uber_completed_clustering_5000.csv")
features = ["Avg VTAT", "Avg CTAT", "Booking Value", "Ride Distance"]
df = pd.read_csv(path)[features].dropna().copy()
scaler = StandardScaler()
X = scaler.fit_transform(df)

inertias = []
for k in range(1, 11):
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    model.fit(X)
    inertias.append(model.inertia_)
plt.plot(range(1, 11), inertias, marker="o")
plt.xlabel("Number of clusters (k)")
plt.ylabel("Inertia")
plt.title("Elbow Method - Completed Rides")
plt.show()

model = KMeans(n_clusters=3, random_state=42, n_init=10)
labels = model.fit_predict(X)
df["Cluster"] = labels
print("Cluster counts:", df["Cluster"].value_counts().sort_index())
print("Inertia:", model.inertia_)
print("Silhouette:", silhouette_score(X, labels))
print("Davies-Bouldin:", davies_bouldin_score(X, labels))
print("Cluster means:\n", df.groupby("Cluster")[features].mean())

plt.scatter(df["Ride Distance"], df["Booking Value"], c=labels, s=6)
plt.xlabel("Ride Distance")
plt.ylabel("Booking Value")
plt.title("K-Means Clusters - Uber Completed Rides")
plt.show()