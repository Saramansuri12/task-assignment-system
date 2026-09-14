from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from feature_config import FEATURES, TARGET


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed"

TRAIN_PATH = DATA_DIR / "train_data.csv"
TEST_PATH = DATA_DIR / "test_data.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_processed_data():

    train_df = pd.read_csv(TRAIN_PATH)

    test_df = pd.read_csv(TEST_PATH)

    print("Train shape:", train_df.shape)
    print("Test shape:", test_df.shape)

    return train_df, test_df


# --------------------------------------------------
# IDENTIFY FEATURE TYPES
# --------------------------------------------------

def get_feature_types(X):

    numerical_features = X.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    categorical_features = X.select_dtypes(
    include=["object", "string", "bool", "category"]
).columns.tolist()

    return numerical_features, categorical_features


# --------------------------------------------------
# BUILD PREPROCESSOR
# --------------------------------------------------

def build_preprocessor(
    numerical_features,
    categorical_features
):

    # Numerical preprocessing
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

    # Categorical preprocessing
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

    # Combine both
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
# PREPARE X AND Y
# --------------------------------------------------

def prepare_xy(df):

    X = df[FEATURES].copy()

    y = df[TARGET].copy()

    return X, y


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    # Load data
    train_df, test_df = load_processed_data()

    # Prepare X and y
    X_train, y_train = prepare_xy(
        train_df
    )

    X_test, y_test = prepare_xy(
        test_df
    )

    # Identify feature types
    numerical_features, categorical_features = (
        get_feature_types(X_train)
    )

    print("\nNumerical Features:")
    print(numerical_features)

    print("\nCategorical Features:")
    print(categorical_features)

    # Build preprocessing pipeline
    preprocessor = build_preprocessor(
        numerical_features,
        categorical_features
    )

    # Fit ONLY on training data
    X_train_processed = (
        preprocessor.fit_transform(
            X_train
        )
    )

    # Transform test data
    X_test_processed = (
        preprocessor.transform(
            X_test
        )
    )

    print("\nPreprocessing completed successfully!")

    print(
        "Processed train shape:",
        X_train_processed.shape
    )

    print(
        "Processed test shape:",
        X_test_processed.shape
    )