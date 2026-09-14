from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

TRAIN_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "train_data.csv"
)

TEST_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "test_data.csv"
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

TARGET = "project_success"

FEATURES = [
    "project_domain",
    "project_type",
    "project_complexity",
    "project_criticality",
    "role_required",
    "team_size_required",
    "estimated_hours",
    "deadline_days",
    "priority",
    "skill_match_pct",
    "critical_skill_match_pct",
    "skill_level_match_pct",
    "experience_match_pct",
    "domain_match",
    "role_match",
    "critical_project_experience",
    "performance_score",
    "current_workload_pct",
    "availability_pct",
    "reliability_score",
    "collaboration_score"
]


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data():

    train_df = pd.read_csv(TRAIN_PATH)

    test_df = pd.read_csv(TEST_PATH)

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    return X_train, X_test, y_train, y_test


# --------------------------------------------------
# BUILD PREPROCESSOR
# --------------------------------------------------

def build_preprocessor(X_train):

    numerical_features = X_train.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    categorical_features = X_train.select_dtypes(
        include=["object", "string", "bool", "category"]
    ).columns.tolist()


    numerical_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                )
            ),
            (
                "scaler",
                StandardScaler()
            )
        ]
    )


    categorical_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                )
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            )
        ]
    )


    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_transformer,
                numerical_features
            ),
            (
                "categorical",
                categorical_transformer,
                categorical_features
            )
        ]
    )

    return preprocessor


# --------------------------------------------------
# BUILD MODEL PIPELINE
# --------------------------------------------------

def build_model(preprocessor):

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    return pipeline


# --------------------------------------------------
# EVALUATE MODEL
# --------------------------------------------------

def evaluate_model(
    model,
    X_test,
    y_test
):

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]


    print("\n" + "=" * 50)
    print("MODEL PERFORMANCE")
    print("=" * 50)

    print(
        "Accuracy:",
        round(
            accuracy_score(
                y_test,
                predictions
            ),
            4
        )
    )

    print(
        "Precision:",
        round(
            precision_score(
                y_test,
                predictions
            ),
            4
        )
    )

    print(
        "Recall:",
        round(
            recall_score(
                y_test,
                predictions
            ),
            4
        )
    )

    print(
        "F1 Score:",
        round(
            f1_score(
                y_test,
                predictions
            ),
            4
        )
    )

    print(
        "ROC-AUC:",
        round(
            roc_auc_score(
                y_test,
                probabilities
            ),
            4
        )
    )


    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions
        )
    )


    print(
        "Confusion Matrix:"
    )

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("Loading data...")

    X_train, X_test, y_train, y_test = (
        load_data()
    )

    print(
        "Training samples:",
        len(X_train)
    )

    print(
        "Testing samples:",
        len(X_test)
    )


    print("\nBuilding preprocessing pipeline...")

    preprocessor = build_preprocessor(
        X_train
    )


    print(
        "Training Logistic Regression..."
    )

    model = build_model(
        preprocessor
    )

    model.fit(
        X_train,
        y_train
    )


    print(
        "Model training completed!"
    )


    evaluate_model(
        model,
        X_test,
        y_test
    )