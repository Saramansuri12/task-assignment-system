from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
)


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    BASE_DIR.parent.parent
    / "data"
)

MODEL_DIR = BASE_DIR / "model"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# CONFIG
# =========================================================

DATA_FILE = (
    DATA_DIR
    / "assignment_training.csv"
)

MODEL_FILE = (
    MODEL_DIR
    / "assignment_model.pkl"
)


FEATURES = [
    "skill_match",
    "experience_match",
    "availability",
    "reliability",
]

TARGET = "success"


# =========================================================
# TRAIN
# =========================================================

def train():

    print("=" * 70)
    print("ASSIGNMENT ML MODEL TRAINING")
    print("=" * 70)

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Training data not found:\n"
            f"{DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    print(
        f"Loaded {len(df):,} training rows"
    )

    missing = [
        column
        for column in FEATURES + [TARGET]
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns: "
            + ", ".join(missing)
        )

    df = df.dropna(
        subset=FEATURES + [TARGET]
    )

    X = df[FEATURES]

    y = df[TARGET]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )
    )

    print(
        f"Training rows: {len(X_train):,}"
    )

    print(
        f"Testing rows: {len(X_test):,}"
    )

    model = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_test
    )

    probabilities = (
        model.predict_proba(X_test)[:, 1]
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    auc = roc_auc_score(
        y_test,
        probabilities,
    )

    print()
    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"ROC-AUC  : {auc:.4f}"
    )

    joblib.dump(
        model,
        MODEL_FILE,
    )

    print()
    print(
        f"Model saved to:"
    )

    print(
        MODEL_FILE
    )

    print("=" * 70)


if __name__ == "__main__":
    train()