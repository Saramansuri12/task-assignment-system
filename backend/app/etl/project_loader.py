import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.project import Project
from app.etl.csv_reader import load_csv


DATASET = "task_assignments.csv"


def get_value(row, *columns):
    """
    Return the first available non-null value
    from the supplied column names.
    """

    for column in columns:
        if column in row.index:
            value = row[column]

            if pd.notna(value):
                return value

    return None


def load_projects():

    print("=" * 80)
    print("LOADING PROJECT DATA")
    print("=" * 80)

    df = load_csv(DATASET)

    if "project_id" not in df.columns:
        raise ValueError(
            "project_id column not found in projects_tasks.csv"
        )

    # One project can contain multiple tasks.
    # Keep one representative row per project.
    project_df = df.drop_duplicates(
        subset=["project_id"]
    )

    print(f"Projects found: {len(project_df)}")

    db: Session = SessionLocal()

    inserted = 0
    updated = 0

    try:

        for _, row in project_df.iterrows():

            project_id = str(row["project_id"])

            existing = (
                db.query(Project)
                .filter(Project.project_id == project_id)
                .first()
            )

            values = {
                "project_name": get_value(
                    row,
                    "project_name",
                    "project_title",
                    "name"
                ),

                "project_domain": get_value(
                    row,
                    "project_domain",
                    "domain"
                ),

                "project_type": get_value(
                    row,
                    "project_type",
                    "project_category"
                ),

                "project_complexity": get_value(
                    row,
                    "project_complexity",
                    "complexity"
                ),

                "project_criticality": get_value(
                    row,
                    "project_criticality",
                    "criticality"
                ),

                "priority": get_value(
                    row,
                    "priority"
                )
            }

            if existing:

                for key, value in values.items():
                    if value is not None:
                        setattr(existing, key, value)

                updated += 1

            else:

                project = Project(
                    project_id=project_id,
                    **values
                )

                db.add(project)

                inserted += 1

        db.commit()

        print(f"Projects inserted: {inserted}")
        print(f"Projects updated: {updated}")

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()

    print("PROJECT LOADING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    load_projects()