"""DMBI Experiment 2: Data preprocessing using the original Uber NCR CSV.
Input: ncr_ride_bookings.csv (same folder, or supply --csv PATH).
Outputs: exp2_outputs/ (processed data, missing-value report and summary).
"""
from pathlib import Path
import argparse

import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

parser = argparse.ArgumentParser()
parser.add_argument("--csv", default="ncr_ride_bookings.csv")
args = parser.parse_args()
input_path = Path(args.csv)
if not input_path.exists():
    input_path = Path(__file__).resolve().parent / args.csv
if not input_path.is_file():
    raise FileNotFoundError(f"Dataset not found: {args.csv}")

out = Path(__file__).resolve().parent / "exp2_outputs"
out.mkdir(exist_ok=True)

df = pd.read_csv(input_path, low_memory=False)
df.columns = df.columns.str.strip()
print("EXPERIMENT 2 - DATA PREPROCESSING")
print("Dataset:", input_path.name)
print("Original shape:", df.shape)
print("\nMissing values in original dataset:")
missing_before = df.isna().sum().sort_values(ascending=False)
print(missing_before.to_string())
missing_before.rename("missing_count").to_csv(out / "missing_values_original.csv")

duplicates = int(df.duplicated().sum())
df = df.drop_duplicates().reset_index(drop=True)
print("\nExact duplicate rows removed:", duplicates)

numeric_cols = ["Avg VTAT", "Avg CTAT", "Booking Value", "Ride Distance"]
cat_cols = ["Vehicle Type", "Payment Method", "Booking Status"]
required = numeric_cols + cat_cols
not_found = [c for c in required if c not in df.columns]
if not_found:
    raise ValueError(f"Missing expected columns: {not_found}")

clean = df[required].copy()
for col in cat_cols:
    clean[col] = clean[col].astype("string").str.strip()
    clean[col] = clean[col].replace("", pd.NA).fillna("Unknown")

# Missing numeric values often reflect non-completed rides.
# Retain missingness flags before median imputation for a modelling example.
imputation = {}
for col in numeric_cols:
    clean[col] = pd.to_numeric(clean[col], errors="coerce")
    clean[col + "_was_missing"] = clean[col].isna().astype("int8")
    median = clean[col].median()
    if pd.isna(median):
        raise ValueError(f"Column has no observed numeric values: {col}")
    imputation[col] = float(median)
    clean[col] = clean[col].fillna(median)

# Encode nominal categories without introducing an artificial ordering.
features = pd.get_dummies(
    clean, columns=["Vehicle Type", "Payment Method"], dtype="int8"
)
# Encode booking status as a separate label, NOT an input feature.
label_encoder = LabelEncoder()
features["Booking_Status_Code"] = label_encoder.fit_transform(
    clean["Booking Status"]
)
features = features.drop(columns=["Booking Status"])

# Scale numerical measurements; preserve indicator and one-hot columns.
scaler = StandardScaler()
features[numeric_cols] = scaler.fit_transform(features[numeric_cols])

features.to_csv(out / "uber_preprocessed_features.csv", index=False)
clean.to_csv(out / "uber_cleaned_unscaled.csv", index=False)
features.head(10).to_csv(out / "first_10_preprocessed_rows.csv", index=False)

report = [
    "EXPERIMENT 2 - DATA PREPROCESSING RESULTS",
    f"Input: {input_path.name}",
    f"Original records: {len(df) + duplicates}",
    f"Exact duplicates removed: {duplicates}",
    f"Final records: {len(df)}",
    f"Features in processed CSV: {features.shape[1]}",
    "Numeric missingness flags are preserved before imputation.",
    "Numeric medians used for imputation:",
]
report.extend(f"  {k}: {v:.4f}" for k, v in imputation.items())
report.append("Status labels: " + repr(dict(zip(
    label_encoder.classes_.tolist(), range(len(label_encoder.classes_))
))))
report.append("Note: Imputed fares/distances for non-completed bookings are modelling placeholders, not real charges or distances.")
(out / "summary.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
print("\nFirst five processed records:")
print(features[["Avg VTAT", "Avg CTAT", "Booking Value",
                "Ride Distance", "Avg VTAT_was_missing",
                "Booking Value_was_missing", "Booking_Status_Code"]].head().to_string(index=False))
print("\nOutput folder:", out.resolve())
