import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.employee import Employee
from app.etl.csv_reader import load_csv, clean_dataframe


FILE_NAME = "employee_derived_attributes.csv"


def load_employees(db: Session):

    print("\nLoading employees...")

    df = load_csv(FILE_NAME)

    df = clean_dataframe(df)

    print("Columns detected:")
    print(df.columns.tolist())

    required_columns = [
        "employee_id"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required employee columns missing: {missing}"
        )

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():

        employee_id = row.get("employee_id")

        if pd.isna(employee_id):
            skipped += 1
            continue

        employee_id = str(
            employee_id
        ).strip()

        employee = (
            db.query(Employee)
            .filter(
                Employee.employee_id == employee_id
            )
            .first()
        )

        data = {}

        field_sources = {
            "role": "job_title",
            "years_experience": "years_at_company",
            "performance_score": "performance_score",
            "current_workload_pct": "baseline_load",
            "availability_pct": "capacity_week",
            "critical_project_experience": "critical_project_experience",
        }

        for field, source in field_sources.items():

            if source not in df.columns:
                continue

            value = row[source]

            if pd.isna(value):
                value = None

            if field == "current_workload_pct" and value is not None:
                value = float(value) * 100

            data[field] = value

        if employee is None:

            employee = Employee(
                employee_id=employee_id,
                **data
            )

            db.add(employee)

            inserted += 1

        else:

            for field, value in data.items():

                setattr(
                    employee,
                    field,
                    value
                )

            updated += 1

    db.commit()

    print("\nEmployee loading complete.")

    print(f"Inserted : {inserted:,}")
    print(f"Updated  : {updated:,}")
    print(f"Skipped  : {skipped:,}")

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }


def main():

    db = SessionLocal()

    try:

        load_employees(db)

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()