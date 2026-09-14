import os
import pandas as pd


PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        ".."
    )
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "data"
)


def read_csv(file_name: str) -> pd.DataFrame:
    """
    Read a CSV file from the project's data directory.
    """

    file_path = os.path.join(
        DATA_DIR,
        file_name
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    try:
        df = pd.read_csv(
            file_path,
            low_memory=False
        )

    except Exception as exc:
        raise RuntimeError(
            f"Unable to read {file_name}: {exc}"
        )

    return df


def check_empty_dataset(
    df: pd.DataFrame,
    file_name: str
):
    """
    Make sure the CSV actually contains records.
    """

    if df.empty:
        raise ValueError(
            f"{file_name} contains no records."
        )


def check_duplicate_rows(
    df: pd.DataFrame,
    file_name: str
):
    """
    Report duplicate rows.
    """

    duplicates = df.duplicated().sum()

    if duplicates > 0:
        print(
            f"WARNING: {file_name} has "
            f"{duplicates:,} duplicate rows."
        )


def inspect_missing_values(
    df: pd.DataFrame,
    file_name: str
):
    """
    Display columns containing missing values.
    """

    missing = df.isna().sum()

    missing = missing[
        missing > 0
    ]

    if not missing.empty:

        print(
            f"\nMissing values in {file_name}:"
        )

        for column, count in missing.items():

            percentage = (
                count / len(df)
            ) * 100

            print(
                f"  {column}: "
                f"{count:,} "
                f"({percentage:.2f}%)"
            )


def validate_dataset(
    file_name: str
):
    """
    Read and perform basic validation.
    """

    print(
        f"\nValidating: {file_name}"
    )

    df = read_csv(file_name)

    check_empty_dataset(
        df,
        file_name
    )

    check_duplicate_rows(
        df,
        file_name
    )

    inspect_missing_values(
        df,
        file_name
    )

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    return df