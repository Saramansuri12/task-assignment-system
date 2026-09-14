import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.task import Task
from app.db.models.project import Project
from app.etl.csv_reader import load_csv, clean_dataframe


DATASET = "task_assignments.csv"


def get_value(row, *columns):
    """
    Return the first available non-empty column value.
    """

    for column in columns:

        if column in row.index:

            value = row[column]

            if pd.notna(value):
                return value

    return None


def to_string(value):

    if value is None or pd.isna(value):
        return None

    return str(value).strip()


def to_float(value):

    if value is None or pd.isna(value):
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_int(value):

    if value is None or pd.isna(value):
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def to_date(value):

    if value is None or pd.isna(value):
        return None

    try:
        return pd.to_datetime(value).date()
    except (ValueError, TypeError):
        return None


def load_tasks():

    print()
    print("=" * 80)
    print("TASK DATA LOADER")
    print("=" * 80)

    # ---------------------------------------------------------
    # Read dataset
    # ---------------------------------------------------------

    df = load_csv(DATASET)

    df = clean_dataframe(df)

    print(f"Dataset rows: {len(df):,}")
    print()
    print("Detected columns:")
    print(df.columns.tolist())

    # ---------------------------------------------------------
    # Validate required columns
    # ---------------------------------------------------------

    required_columns = [
        "task_id",
        "project_id"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Required task columns are missing: "
            + ", ".join(missing_columns)
        )

    # ---------------------------------------------------------
    # Remove duplicate task records
    # ---------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(
        subset=["task_id"]
    )

    after = len(df)

    print()
    print(
        f"Duplicate task rows removed: "
        f"{before - after:,}"
    )

    # ---------------------------------------------------------
    # Database connection
    # ---------------------------------------------------------

    db: Session = SessionLocal()

    inserted = 0
    updated = 0
    skipped = 0

    try:

        for _, row in df.iterrows():

            task_id = to_string(
                row["task_id"]
            )

            project_id = to_string(
                row["project_id"]
            )

            # -------------------------------------------------
            # Basic validation
            # -------------------------------------------------

            if not task_id or not project_id:

                skipped += 1
                continue

            # -------------------------------------------------
            # Project must already exist
            # -------------------------------------------------

            project = (
                db.query(Project)
                .filter(
                    Project.project_id == project_id
                )
                .first()
            )

            if project is None:

                print(
                    f"Skipping task {task_id}: "
                    f"project {project_id} not found."
                )

                skipped += 1
                continue

            # -------------------------------------------------
            # Prepare task data
            # -------------------------------------------------

            task_data = {

                "project_id": project_id,

                "task_title": to_string(
                    get_value(
                        row,
                        "task_title",
                        "task_name",
                        "title"
                    )
                ),

                "task_description": to_string(
                    get_value(
                        row,
                        "task_description",
                        "description"
                    )
                ),

                "project_complexity": to_string(
                    get_value(
                        row,
                        "project_complexity",
                        "complexity"
                    )
                ),

                "project_criticality": to_string(
                    get_value(
                        row,
                        "project_criticality",
                        "criticality"
                    )
                ),

                "role_required": to_string(
                    get_value(
                        row,
                        "role_required",
                        "required_role"
                    )
                ),

                "team_size_required": to_int(
                    get_value(
                        row,
                        "team_size_required",
                        "team_size"
                    )
                ),

                "estimated_hours": to_float(
                    get_value(
                        row,
                        "estimated_hours",
                        "task_estimated_hours"
                    )
                ),

                "deadline_days": to_int(
                    get_value(
                        row,
                        "deadline_days"
                    )
                ),

                "priority": to_string(
                    get_value(
                        row,
                        "priority"
                    )
                ),

                "required_experience_years": to_float(
                    get_value(
                        row,
                        "required_experience_years",
                        "experience_required"
                    )
                ),

                "task_start_date": to_date(
                    get_value(
                        row,
                        "task_start_date",
                        "start_date"
                    )
                ),

                "task_due_date": to_date(
                    get_value(
                        row,
                        "task_due_date",
                        "due_date",
                        "deadline"
                    )
                ),

                "assigned_count": to_int(
                    get_value(
                        row,
                        "assigned_count"
                    )
                )
            }

            # -------------------------------------------------
            # Check whether task already exists
            # -------------------------------------------------

            existing_task = (
                db.query(Task)
                .filter(
                    Task.task_id == task_id
                )
                .first()
            )

            if existing_task:

                # Update existing record
                for field, value in task_data.items():

                    setattr(
                        existing_task,
                        field,
                        value
                    )

                updated += 1

            else:

                # Create new task
                task = Task(
                    task_id=task_id,
                    **task_data
                )

                db.add(task)

                inserted += 1

            # -------------------------------------------------
            # Batch commit
            # -------------------------------------------------

            processed = inserted + updated

            if processed > 0 and processed % 1000 == 0:

                db.commit()

                print(
                    f"Processed "
                    f"{processed:,}/"
                    f"{len(df):,} tasks"
                )

        # Final commit
        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("TASK LOADING COMPLETE")
    print("=" * 80)

    print(
        f"Inserted : {inserted:,}"
    )

    print(
        f"Updated  : {updated:,}"
    )

    print(
        f"Skipped  : {skipped:,}"
    )

    print("=" * 80)


if __name__ == "__main__":
    load_tasks()