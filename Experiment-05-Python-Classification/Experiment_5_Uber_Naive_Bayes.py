"""Experiment 5: Naive Bayes (library and student-defined algorithm).

Run: python Experiment_5_Uber_Naive_Bayes.py
Requires: pandas, numpy, scikit-learn, matplotlib
Input: uber_weka_classification.csv in the same folder (or --csv PATH).
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.naive_bayes import CategoricalNB
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    ConfusionMatrixDisplay,
)

FEATURES = ['Vehicle Type', 'Pickup Location', 'Drop Location']
TARGET = 'Booking Status'


def custom_categorical_naive_bayes(X_train, y_train, X_test, alpha=1.0):
    """Calculate categorical NB predictions without a prebuilt classifier.

    Feature values must be nonnegative integer category codes.
    Laplace smoothing is applied to the categorical likelihood tables.
    """
    classes, y_codes = np.unique(y_train, return_inverse=True)
    n = len(y_train)
    n_classes = len(classes)
    class_counts = np.bincount(y_codes, minlength=n_classes)
    log_prior = np.log(class_counts / n)
    likelihood_tables = []

    for col in range(X_train.shape[1]):
        # Code 0 is reserved for categories unseen in the training data.
        count_of_values = int(max(X_train[:, col].max(), X_test[:, col].max())) + 1
        table = np.empty((n_classes, count_of_values), dtype=float)
        for class_index in range(n_classes):
            vals = X_train[y_codes == class_index, col]
            counts = np.bincount(vals, minlength=count_of_values)
            table[class_index] = np.log(
                (counts + alpha) /
                (class_counts[class_index] + alpha * count_of_values)
            )
        likelihood_tables.append(table)

    scores = np.tile(log_prior, (len(X_test), 1))
    for col, table in enumerate(likelihood_tables):
        scores += table[:, X_test[:, col]].T
    return classes[np.argmax(scores, axis=1)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default='uber_weka_classification.csv')
    parser.add_argument('--output', default='exp5_outputs')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        csv_path = Path(__file__).resolve().parent / args.csv
    if not csv_path.is_file():
        raise FileNotFoundError(
            'Place uber_weka_classification.csv beside this script, or pass --csv FILE'
        )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path, usecols=FEATURES + [TARGET])
    df = df.dropna(subset=[TARGET]).copy()
    for col in FEATURES:
        df[col] = df[col].fillna('Unknown').astype(str)
    df[TARGET] = df[TARGET].astype(str)
    print(f'Dataset: {csv_path.name}; records: {len(df)}')
    print('Classes:', df[TARGET].value_counts().to_dict())

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        df[FEATURES], df[TARGET], test_size=0.20, random_state=42,
        stratify=df[TARGET]
    )

    # Fit the encoder only on the training set to avoid leakage.
    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    X_train = encoder.fit_transform(X_train_raw).astype(int) + 1
    X_test = encoder.transform(X_test_raw).astype(int) + 1

    # Method 1: inbuilt classifier.
    library_model = CategoricalNB(alpha=1.0)
    library_model.fit(X_train, y_train)
    predictions_library = library_model.predict(X_test)

    # Method 2: student-defined classifier.
    predictions_custom = custom_categorical_naive_bayes(
        X_train, y_train.to_numpy(), X_test
    )

    report_lines = [
        f'Training samples: {len(X_train)}',
        f'Testing samples: {len(X_test)}',
    ]
    for title, predictions, filename in [
        ('Library CategoricalNB', predictions_library, 'library_confusion_matrix.png'),
        ('Student-defined Categorical Naive Bayes', predictions_custom, 'custom_confusion_matrix.png'),
    ]:
        acc = accuracy_score(y_test, predictions)
        report = classification_report(y_test, predictions, zero_division=0)
        print(f'\n=== {title} ===')
        print(f'Accuracy: {acc:.4%}')
        print(report)
        report_lines.extend([f'\n=== {title} ===', f'Accuracy: {acc:.4%}', report])
        labels = sorted(y_test.unique().tolist())
        cm = confusion_matrix(y_test, predictions, labels=labels)
        fig, ax = plt.subplots(figsize=(10, 8))
        ConfusionMatrixDisplay(cm, display_labels=labels).plot(
            ax=ax, xticks_rotation=35, values_format='d', colorbar=False
        )
        ax.set_title(title + ' - Confusion Matrix')
        fig.tight_layout()
        fig.savefig(output_dir / filename, dpi=180)
        plt.close(fig)

    agree = np.mean(predictions_library == predictions_custom)
    report_lines.append(f'Prediction agreement: {agree:.2%}')
    print(f'\nPrediction agreement: {agree:.2%}')
    (output_dir / 'results.txt').write_text('\n'.join(report_lines), encoding='utf-8')
    print(f'\nSaved report and 2 confusion matrices to: {output_dir.resolve()}')


if __name__ == '__main__':
    main()
