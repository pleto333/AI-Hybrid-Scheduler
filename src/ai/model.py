import csv
import os
import pickle
import sys
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.simple_model import SimpleCentroidClassifier
from common.config import DATA_PATH, FEATURES, LABEL, MODEL_PATH


def load_training_data():
    if not os.path.exists(DATA_PATH):
        print(f">>> Data file not found: {DATA_PATH}")
        print(">>> Run src/main.py first to collect workload data.")
        return [], []

    rows = []
    labels = []
    with open(DATA_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row or row.get("scenario") == "scenario":
                continue

            try:
                features = [float(row[name]) for name in FEATURES]
                label = int(float(row[LABEL]))
            except (KeyError, TypeError, ValueError):
                continue

            rows.append(features)
            labels.append(label)

    return rows, labels


def train_model():
    print(">>> Loading training data...")
    rows, labels = load_training_data()
    if not rows:
        print(">>> Error: no valid training rows found.")
        return

    counts = Counter(labels)
    print(f">>> Training rows: {len(rows)}")
    print(f">>> Label distribution: {dict(sorted(counts.items()))}")

    print(">>> Training AI model (SimpleCentroidClassifier)...")
    model = SimpleCentroidClassifier().fit(rows, labels)

    with open(MODEL_PATH, "wb") as file:
        pickle.dump(model, file)

    print(">>> Model training complete.")
    print(f">>> Saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
