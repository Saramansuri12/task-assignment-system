from pathlib import Path
import pandas as pd

from feature_config import FEATURES, TARGET


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "raw"

ASSIGNMENTS_PATH = DATA_DIR / "task_assignments.csv"
TASKS_PATH = DATA_DIR / "projects_tasks.csv"

PROCESSED_DIR = BASE_DIR / "data" / "processed"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data():

    print("Loading datasets...\n")

    assignments = pd.read_csv(ASSIGNMENTS_PATH)

    tasks = pd.read_csv(TASKS_PATH)

    print("Assignments shape:", assignments.shape)
    print("Tasks shape:", tasks.shape)

    return assignments, tasks


# --------------------------------------------------
# MERGE TASK DATE
# --------------------------------------------------

def merge_task_dates(assignments, tasks):

    print("\nMerging task dates...")

    # Check important columns
    print("Assignment columns contain task_id:",
          "task_id" in assignments.columns)

    print("Task columns contain task_id:",
          "task_id" in tasks.columns)

    # Keep only task ID and date
    task_dates = tasks[
        [
            "task_id",
            "task_start_date",
            "task_due_date"
        ]
    ].copy()

    # Merge date information
    dataset = assignments.merge(
        task_dates,
        on="task_id",
        how="left"
    )

    # Convert to datetime
    dataset["task_start_date"] = pd.to_datetime(
        dataset["task_start_date"],
        errors="coerce"
    )

    dataset["task_due_date"] = pd.to_datetime(
        dataset["task_due_date"],
        errors="coerce"
    )

    print("Dataset shape after merge:",
          dataset.shape)

    print(
        "Missing task_start_date:",
        dataset["task_start_date"].isna().sum()
    )

    return dataset


# --------------------------------------------------
# SELECT ML FEATURES
# --------------------------------------------------

def prepare_dataset(dataset):

    available_features = [
        column
        for column in FEATURES
        if column in dataset.columns
    ]

    dataset = dataset[
        available_features
        + [TARGET, "task_start_date"]
    ].copy()

    print("\nFinal ML dataset shape:",
          dataset.shape)

    return dataset


# --------------------------------------------------
# TIME-BASED SPLIT
# --------------------------------------------------

def create_time_split(dataset):

    # Remove rows without dates
    dataset = dataset.dropna(
        subset=["task_start_date"]
    )

    # Sort chronologically
    dataset = dataset.sort_values(
        "task_start_date"
    )

    # Use oldest 80% for training
    # Use newest 20% for testing

    split_index = int(
        len(dataset) * 0.80
    )

    train_df = dataset.iloc[
        :split_index
    ].copy()

    test_df = dataset.iloc[
        split_index:
    ].copy()

    print("\n-----------------------------")
    print("TIME-BASED SPLIT")
    print("-----------------------------")

    print(
        "Train shape:",
        train_df.shape
    )

    print(
        "Test shape:",
        test_df.shape
    )

    print("\nTraining period:")

    print(
        train_df["task_start_date"].min(),
        "to",
        train_df["task_start_date"].max()
    )

    print("\nTesting period:")

    print(
        test_df["task_start_date"].min(),
        "to",
        test_df["task_start_date"].max()
    )

    return train_df, test_df


# --------------------------------------------------
# SAVE PROCESSED DATA
# --------------------------------------------------

def save_processed_data(train_df, test_df):

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    train_path = (
        PROCESSED_DIR
        / "train_data.csv"
    )

    test_path = (
        PROCESSED_DIR
        / "test_data.csv"
    )

    train_df.to_csv(
        train_path,
        index=False
    )

    test_df.to_csv(
        test_path,
        index=False
    )

    print("\nProcessed files saved!")

    print(
        "Train:",
        train_path
    )

    print(
        "Test:",
        test_path
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    # 1. Load data
    assignments, tasks = load_data()

    # 2. Merge task dates
    dataset = merge_task_dates(
        assignments,
        tasks
    )

    # 3. Select ML features
    dataset = prepare_dataset(
        dataset
    )

    # 4. Create time-based split
    train_df, test_df = create_time_split(
        dataset
    )

    # 5. Save data
    save_processed_data(
        train_df,
        test_df
    )

    print("\nData preparation completed successfully!")