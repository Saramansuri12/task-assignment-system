import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.employee import Employee
from app.db.models.skill import Skill
from app.db.models.employee_skills import EmployeeSkill
from app.etl.csv_reader import load_csv, clean_dataframe


FILE_NAME = "employee_skill_profiles.csv"

# Number of records inserted into DB at a time
BATCH_SIZE = 5000


def load_employee_skills(db: Session):

    print("\nLoading employee skill profiles...")

    # ---------------------------------------------------------
    # 1. LOAD CSV
    # ---------------------------------------------------------

    df = load_csv(FILE_NAME)
    df = clean_dataframe(df)

    print("\nColumns detected:")
    print(df.columns.tolist())

    # ---------------------------------------------------------
    # 2. VALIDATE REQUIRED COLUMNS
    # ---------------------------------------------------------

    if "employee_id" not in df.columns:
        raise ValueError("employee_id column not found.")

    if "skill_id" not in df.columns:
        raise ValueError("skill_id column not found.")

    # ---------------------------------------------------------
    # 3. LOAD EMPLOYEES ONCE
    # ---------------------------------------------------------

    print("\nLoading employees from database...")

    employees = db.query(Employee).all()

    employee_map = {
        str(employee.employee_id).strip(): employee
        for employee in employees
    }

    print(f"Employees loaded: {len(employee_map):,}")

    # ---------------------------------------------------------
    # 4. LOAD SKILLS ONCE
    # ---------------------------------------------------------

    print("\nLoading skills from database...")

    skills = db.query(Skill).all()

    skill_map = {
        str(skill.skill_id).strip(): skill
        for skill in skills
    }

    print(f"Skills loaded: {len(skill_map):,}")

    # ---------------------------------------------------------
    # 5. LOAD EXISTING EMPLOYEE-SKILL RELATIONSHIPS
    # ---------------------------------------------------------

    print("\nLoading existing employee-skill relationships...")

    existing_relationships = db.query(EmployeeSkill).all()

    relationship_map = {
        (
            str(relationship.employee_id).strip(),
            str(relationship.skill_id).strip()
        ): relationship
        for relationship in existing_relationships
    }

    print(
        f"Existing relationships: "
        f"{len(relationship_map):,}"
    )

    # ---------------------------------------------------------
    # 6. COUNTERS
    # ---------------------------------------------------------

    inserted = 0
    updated = 0
    skipped = 0

    batch = []

    # ---------------------------------------------------------
    # 7. PROCESS CSV
    # ---------------------------------------------------------

    print("\nProcessing employee skill profiles...")

    for index, row in df.iterrows():

        employee_id = row["employee_id"]
        skill_id = row["skill_id"]

        # ---------------------------------------------
        # Skip missing IDs
        # ---------------------------------------------

        if pd.isna(employee_id) or pd.isna(skill_id):
            skipped += 1
            continue

        employee_id = str(employee_id).strip()
        skill_id = str(skill_id).strip()

        # ---------------------------------------------
        # Check employee exists
        # ---------------------------------------------

        if employee_id not in employee_map:
            skipped += 1
            continue

        # ---------------------------------------------
        # Check skill exists
        # ---------------------------------------------

        if skill_id not in skill_map:
            skipped += 1
            continue

        # ---------------------------------------------
        # Get skill level if available
        # ---------------------------------------------

        skill_level = None

        if "skill_level" in df.columns:

            value = row["skill_level"]

            if not pd.isna(value):
                try:
                    skill_level = float(value)
                except (ValueError, TypeError):
                    skill_level = None

        # ---------------------------------------------
        # Relationship key
        # ---------------------------------------------

        relationship_key = (
            employee_id,
            skill_id
        )

        # ---------------------------------------------
        # Check existing relationship
        # ---------------------------------------------

        relationship = relationship_map.get(
            relationship_key
        )

        if relationship is None:

            # -----------------------------------------
            # Create new relationship
            # -----------------------------------------

            relationship = EmployeeSkill(
                employee_id=employee_id,
                skill_id=skill_id,
                skill_level=skill_level
            )

            batch.append(relationship)

            # Add to memory map so duplicate CSV rows
            # don't create duplicate relationships
            relationship_map[relationship_key] = relationship

            inserted += 1

        else:

            # -----------------------------------------
            # Update existing relationship
            # -----------------------------------------

            relationship.skill_level = skill_level

            updated += 1

        # ---------------------------------------------
        # Insert batch
        # ---------------------------------------------

        if len(batch) >= BATCH_SIZE:

            db.add_all(batch)
            db.flush()

            batch.clear()

            print(
                f"Processed: {index + 1:,} / "
                f"{len(df):,}"
            )

    # ---------------------------------------------------------
    # 8. INSERT REMAINING RECORDS
    # ---------------------------------------------------------

    if batch:

        db.add_all(batch)
        db.flush()

    # ---------------------------------------------------------
    # 9. COMMIT
    # ---------------------------------------------------------

    print("\nCommitting changes to database...")

    db.commit()

    # ---------------------------------------------------------
    # 10. RESULTS
    # ---------------------------------------------------------

    print("\nEmployee skill loading complete.")

    print(f"Inserted : {inserted:,}")
    print(f"Updated  : {updated:,}")
    print(f"Skipped  : {skipped:,}")

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped
    }


def main():

    db = SessionLocal()

    try:

        load_employee_skills(db)

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()