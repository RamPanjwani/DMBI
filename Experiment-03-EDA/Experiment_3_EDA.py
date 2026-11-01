"""DMBI Experiment 3: EDA on the real Uber NCR booking dataset.
Input: ncr_ride_bookings.csv (same folder, or supply --csv PATH).
Outputs: exp3_outputs/ (summary, statistics, correlation matrix, five charts).
"""
from pathlib import Path
import argparse

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Save plots without blocking the terminal.
import matplotlib.pyplot as plt
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument("--csv", default="ncr_ride_bookings.csv")
args = parser.parse_args()
input_path = Path(args.csv)
if not input_path.exists():
    input_path = Path(__file__).resolve().parent / args.csv
if not input_path.is_file():
    raise FileNotFoundError(f"Dataset not found: {args.csv}")

out = Path(__file__).resolve().parent / "exp3_outputs"
out.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid")

df = pd.read_csv(input_path, low_memory=False)
df.columns = df.columns.str.strip()
print("EXPERIMENT 3 - EXPLORATORY DATA ANALYSIS")
print("Original dataset shape:", df.shape)
print("\nFirst five rows:")
print(df[["Booking Status", "Vehicle Type", "Booking Value",
          "Ride Distance", "Avg VTAT", "Avg CTAT"]].head().to_string(index=False))
print("\nMissing values:")
print(df.isna().sum().sort_values(ascending=False).to_string())

# Count ALL booking statuses, including cancellations.
status_counts = df["Booking Status"].value_counts()
status_counts.rename("count").to_csv(out / "booking_status_counts.csv")

# Ride fares, distances and ratings are meaningful for completed rides.
completed = df[df["Booking Status"] == "Completed"].copy()
num_cols = [
    "Ride Distance", "Booking Value", "Avg VTAT", "Avg CTAT",
    "Driver Ratings", "Customer Rating"
]
completed[num_cols] = completed[num_cols].apply(pd.to_numeric, errors="coerce")

stats = pd.DataFrame({
    "Count": completed[num_cols].count(),
    "Mean": completed[num_cols].mean(),
    "Median": completed[num_cols].median(),
    "Mode": completed[num_cols].mode().iloc[0],
    "Standard Deviation": completed[num_cols].std(),
    "Variance": completed[num_cols].var(),
    "Min": completed[num_cols].min(),
    "Max": completed[num_cols].max(),
    "Range": completed[num_cols].max() - completed[num_cols].min(),
    "IQR": completed[num_cols].quantile(.75) - completed[num_cols].quantile(.25),
})
corr = completed[num_cols].corr(method="pearson")
stats.round(4).to_csv(out / "eda_statistics.csv")
corr.round(4).to_csv(out / "eda_correlations.csv")
print("\nBooking status counts:\n", status_counts.to_string())
print("\nCompleted rides:", len(completed))
print("\nStatistics (completed rides):\n", stats.round(3).to_string())
print("\nPearson correlation (completed rides):\n", corr.round(3).to_string())
print("\nModes: Vehicle Type =", completed["Vehicle Type"].mode().iloc[0],
      "; Payment Method =", completed["Payment Method"].mode().iloc[0])

# 1. Status distribution (all bookings).
plt.figure(figsize=(10, 5))
sns.barplot(x=status_counts.index, y=status_counts.values, color="steelblue")
plt.xticks(rotation=18, ha="right")
plt.ylabel("Number of bookings")
plt.title("Uber Booking Status Distribution (All Bookings)")
plt.tight_layout()
plt.savefig(out / "01_booking_status_bar.png", dpi=160)
plt.close()

# 2. Histogram (completed rides).
plt.figure(figsize=(9, 5))
sns.histplot(completed["Ride Distance"].dropna(), bins=30, kde=True, color="steelblue")
plt.xlabel("Ride distance")
plt.title("Ride Distance Distribution (Completed Bookings)")
plt.tight_layout()
plt.savefig(out / "02_distance_histogram.png", dpi=160)
plt.close()

# 3. Boxplot of booking value by vehicle type.
plt.figure(figsize=(11, 5))
sns.boxplot(data=completed, x="Vehicle Type", y="Booking Value",
            showfliers=False, color="lightblue")
plt.xticks(rotation=25, ha="right")
plt.title("Booking Value by Vehicle Type (Completed Bookings)")
plt.tight_layout()
plt.savefig(out / "03_value_boxplot.png", dpi=160)
plt.close()

# 4. Pearson correlation heatmap.
plt.figure(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            vmin=-1, vmax=1, square=True)
plt.title("Pearson Correlation (Completed Bookings)")
plt.tight_layout()
plt.savefig(out / "04_correlation_heatmap.png", dpi=160)
plt.close()

# 5. Scatterplot: sample for readability; stats above use every completed ride.
sample = completed.sample(n=min(4000, len(completed)), random_state=42)
plt.figure(figsize=(9, 5))
sns.scatterplot(data=sample, x="Ride Distance", y="Booking Value",
                hue="Vehicle Type", alpha=.55, s=20)
plt.title("Ride Distance vs Booking Value (Sample of Completed Bookings)")
plt.tight_layout()
plt.savefig(out / "05_distance_vs_value_scatter.png", dpi=160)
plt.close()

summary = [
    "EXPERIMENT 3 - EDA RESULTS",
    f"Dataset: {input_path.name}",
    f"All booking records: {len(df)}",
    f"Completed ride records used for numeric EDA: {len(completed)}",
    "Counts by booking status:", status_counts.to_string(),
    "Statistics for completed rides:", stats.round(3).to_string(),
    "Pearson correlation:", corr.round(3).to_string(),
    "Important: These are actual recorded observations, not synthesized values.",
]
(out / "eda_summary.txt").write_text("\n\n".join(summary), encoding="utf-8")
print("\nSaved 5 charts, 3 CSV tables, and summary to:", out.resolve())
