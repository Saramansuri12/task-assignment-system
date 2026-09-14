import os
import pandas as pd

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.employee import Employee


DATA_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )
    ),
    "data"
)


def load_employees(
    db: Session,
    csv_path: str
):
    print("Loading employee data...")

    df = pd.read_csv(csv_path)

    print(f"Rows found: {len(df)}")
    print("Columns:")
    print(df.columns.tolist())

    for _, row in df.iterrows():

        employee_id = row.get("employee_id")

        if pd.isna(employee_id):
            continue

        existing = (
            db.query(Employee)
            .filter(
                Employee.employee_id == int(employee_id)
            )
            .first()
        )

        if existing:
            continue

        employee = Employee(
            employee_id=int(employee_id),

            name=(
                None
                if pd.isna(row.get("name"))
                else str(row.get("name"))
            ),

            role=(
                None
                if pd.isna(row.get("role"))
                else str(row.get("role"))
            ),

            seniority=(
                None
                if pd.isna(row.get("seniority"))
                else str(row.get("seniority"))
            ),

            years_experience=(
                None
                if pd.isna(row.get("years_experience"))
                else float(row.get("years_experience"))
            ),

            performance_score=(
                None
                if pd.isna(row.get("performance_score"))
                else float(row.get("performance_score"))
            ),

            current_workload_pct=(
                None
                if pd.isna(row.get("current_workload_pct"))
                else float(row.get("current_workload_pct"))
            ),

            availability_pct=(
                None
                if pd.isna(row.get("availability_pct"))
                else float(row.get("availability_pct"))
            ),

            available_from=(
                None
                if pd.isna(row.get("available_from"))
                else str(row.get("available_from"))
            ),

            critical_project_experience=(
                None
                if pd.isna(
                    row.get("critical_project_experience")
                )
                else int(
                    row.get(
                        "critical_project_experience"
                    )
                )
            )
        )

        db.add(employee)

    db.commit()

    print("Employee data loaded successfully.")


def main():

    db = SessionLocal()

    try:

        csv_path = os.path.join(
            DATA_DIR,
            "employees.csv"
        )

        if not os.path.exists(csv_path):
            print(
                f"CSV file not found: {csv_path}"
            )
            return

        load_employees(
            db,
            csv_path
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()