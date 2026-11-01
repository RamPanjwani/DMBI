"""DMBI Experiment 9: Association Rule Mining using Python (Apriori).
Input: uber_weka_classification.csv (prepared in Experiments 4 and 5).
Each booking is treated as one transaction of four categorical attributes.
Run: python Experiment_9_Uber_Apriori.py
"""
from pathlib import Path
import argparse
import textwrap
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mlxtend.frequent_patterns import apriori, association_rules
FEATURES = ["Vehicle Type", "Pickup Location", "Drop Location", "Booking Status"]
def readable(items):
    """Convert an itemset to stable, readable text for CSV and console output."""
    return " ; ".join(sorted(items))
def main():
    parser = argparse.ArgumentParser(description="Apriori on Uber booking transactions")
    parser.add_argument("--csv", default="uber_weka_classification.csv")
    parser.add_argument("--output", default="exp9_outputs")
    parser.add_argument("--min-support", type=float, default=0.02)
    parser.add_argument("--min-confidence", type=float, default=0.30)
    parser.add_argument("--min-lift", type=float, default=1.0)
    args = parser.parse_args()
    if not (0 < args.min_support <= 1 and 0 < args.min_confidence <= 1):
        parser.error("Support and confidence must be in (0, 1].")
    if args.min_lift < 0:
        parser.error("Minimum lift must be nonnegative.")
    csv_path = Path(args.csv)
    if not csv_path.is_file():
        csv_path = Path(__file__).resolve().parent / args.csv
    if not csv_path.is_file():
        raise FileNotFoundError(
            "Place uber_weka_classification.csv beside this script, "
            "or supply --csv PATH."
        )
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(csv_path, usecols=FEATURES, low_memory=False)
    if data.empty:
        raise ValueError("The input CSV contains no booking records.")
    for feature in FEATURES:
        data[feature] = data[feature].fillna("Unknown").astype(str).str.strip()
        data.loc[data[feature] == "", feature] = "Unknown"
    # Each row is one booking/transaction. One-hot columns represent items.
    transactions = pd.get_dummies(data, prefix_sep="=", dtype=bool)
    frequent = apriori(
        transactions, min_support=args.min_support,
        use_colnames=True, max_len=3
    ).sort_values("support", ascending=False).reset_index(drop=True)
    frequent_export = frequent.copy()
    frequent_export["itemsets"] = frequent_export["itemsets"].map(readable)
    frequent_export.to_csv(output_dir / "frequent_itemsets.csv", index=False)
    if frequent.empty or not any(frequent["itemsets"].map(len) >= 2):
        rules = pd.DataFrame()
    else:
        rules = association_rules(
            frequent, metric="confidence", min_threshold=args.min_confidence
        )
        rules = rules[rules["lift"] >= args.min_lift].copy()
        rules = rules.sort_values(
            ["lift", "confidence", "support"], ascending=False
        ).reset_index(drop=True)
    columns = ["antecedents", "consequents", "support", "confidence", "lift"]
    if rules.empty:
        export_rules = pd.DataFrame(columns=columns)
        booking_rules = export_rules.copy()
    else:
        booking_rules = rules[
            rules["consequents"].map(
                lambda items: len(items) == 1 and
                next(iter(items)).startswith("Booking Status=")
            ) & ~rules["antecedents"].map(
                lambda items: any(x.startswith("Booking Status=") for x in items)
            )
        ].copy()
        export_rules = rules[columns].copy()
        export_rules["antecedents"] = export_rules["antecedents"].map(readable)
        export_rules["consequents"] = export_rules["consequents"].map(readable)
        booking_rules = booking_rules[columns].copy()
        booking_rules["antecedents"] = booking_rules["antecedents"].map(readable)
        booking_rules["consequents"] = booking_rules["consequents"].map(readable)
    export_rules.to_csv(output_dir / "association_rules.csv", index=False)
    booking_rules.to_csv(output_dir / "booking_status_rules.csv", index=False)
    summary = [
        "EXPERIMENT 9 - PYTHON APRIORI",
        f"Input file: {csv_path}",
        f"Transactions (bookings): {len(data)}",
        f"Distinct item columns: {transactions.shape[1]}",
        f"Minimum support: {args.min_support:.3f}",
        f"Minimum confidence: {args.min_confidence:.3f}",
        f"Minimum lift: {args.min_lift:.3f}",
        f"Frequent itemsets: {len(frequent)}",
        f"Association rules: {len(export_rules)}",
        f"Booking-status consequent rules: {len(booking_rules)}",
        "\nTOP FREQUENT ITEMSETS:",
        frequent_export.head(10).to_string(index=False),
        "\nTOP ASSOCIATION RULES:",
        export_rules.head(10).to_string(index=False),
    ]
    report = "\n".join(summary)
    print(report)
    (output_dir / "summary.txt").write_text(report + "\n", encoding="utf-8")
    # Visualization 1: most common single items in all bookings.
    singles = frequent[frequent["itemsets"].map(len) == 1].head(10)
    if not singles.empty:
        labels = [textwrap.fill(readable(s), 29) for s in singles["itemsets"]]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(labels[::-1], singles["support"].to_numpy()[::-1])
        ax.set_xlabel("Support (share of bookings)")
        ax.set_title("Top Frequent Booking Attributes")
        fig.tight_layout()
        fig.savefig(output_dir / "top_frequent_items.png", dpi=180)
        plt.close(fig)
    # Visualization 2: association-rule support vs confidence, colored by lift.
    if not rules.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        sc = ax.scatter(rules["support"], rules["confidence"],
                        c=rules["lift"], cmap="viridis", alpha=0.75)
        fig.colorbar(sc, ax=ax, label="Lift")
        ax.set_xlabel("Support")
        ax.set_ylabel("Confidence")
        ax.set_title("Apriori Association Rules: Support vs Confidence")
        fig.tight_layout()
        fig.savefig(output_dir / "rules_scatter.png", dpi=180)
        plt.close(fig)
    print(f"\nSaved files in: {output_dir.resolve()}")
    if rules.empty:
        print("No rules satisfy these thresholds; try a lower --min-support.")
if __name__ == "__main__":
    main()