from typing import List

import pandas as pd

from app.etl.validate_dataset import (
    validate_dataset,
)


def load_csv(
    file_name: str
) -> pd.DataFrame:

    return validate_dataset(
        file_name
    )


def require_columns(
    df: pd.DataFrame,
    required_columns: List[str]
):
    """
    Verify that required columns exist.
    """

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )


def clean_column_names(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Standardize column names.

    Example:
        Employee ID
        employee-id
        employee_id

    becomes:
        employee_id
    """

    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(
            " ",
            "_"
        )
        .str.replace(
            "-",
            "_"
        )
    )

    return df


def remove_completely_empty_rows(
    df: pd.DataFrame
) -> pd.DataFrame:

    return df.dropna(
        how="all"
    ).reset_index(
        drop=True
    )


def clean_dataframe(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = clean_column_names(df)

    df = remove_completely_empty_rows(df)

    return df