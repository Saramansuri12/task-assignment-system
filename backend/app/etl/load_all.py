import pandas as pd

from sqlalchemy import text

from app.db.database import SessionLocal


def load_training_data():

    db = SessionLocal()

    try:

        query = text(
            """
            SELECT
                assignment_id,
                project_complexity,
                project_criticality,
                team_size_required,
                estimated_hours,
                deadline_days,
                priority,

                skill_match_pct,
                critical_skill_match_pct,
                skill_level_match_pct,
                experience_match_pct,

                domain_match,
                role_match,

                critical_project_experience,

                performance_score,
                current_workload_pct,
                availability_pct,

                reliability_score,
                collaboration_score,

                completion_time_hours,
                delay_days,
                quality_score,
                manager_rating,

                project_success

            FROM assignments
            WHERE project_success IS NOT NULL
            """
        )

        result = db.execute(query)

        rows = result.fetchall()

        columns = result.keys()

        df = pd.DataFrame(
            rows,
            columns=columns
        )

        return df

    finally:

        db.close()


def prepare_features(df: pd.DataFrame):

    df = df.copy()

    categorical_columns = [
        "project_complexity",
        "project_criticality",
        "priority",
    ]

    for column in categorical_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .fillna("unknown")
                .astype(str)
            )

    boolean_columns = [
        "domain_match",
        "role_match",
    ]

    for column in boolean_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .fillna(False)
                .astype(int)
            )

    numeric_columns = [
        "team_size_required",
        "estimated_hours",
        "deadline_days",

        "skill_match_pct",
        "critical_skill_match_pct",
        "skill_level_match_pct",
        "experience_match_pct",

        "critical_project_experience",

        "performance_score",
        "current_workload_pct",
        "availability_pct",

        "reliability_score",
        "collaboration_score",

        "completion_time_hours",
        "delay_days",
        "quality_score",
        "manager_rating",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            df[column] = df[column].fillna(
                df[column].median()
            )

    return df


def build_training_dataset():

    print("Loading historical assignment data...")

    df = load_training_data()

    if df.empty:

        raise ValueError(
            "No historical assignment data found."
        )

    print(
        f"Historical records: {len(df):,}"
    )

    df = prepare_features(df)

    print(
        f"Training rows ready: {len(df):,}"
    )

    return df