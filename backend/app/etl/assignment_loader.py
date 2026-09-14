import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.assignment import Assignment
from app.db.models.employee import Employee
from app.db.models.task import Task
from app.db.models.project import Project
from app.etl.csv_reader import load_csv


DATASET = "task_assignments.csv"
BATCH_SIZE = 1000


def value(row, column):
    if column not in row.index:
        return None

    result = row[column]

    if pd.isna(result):
        return None

    return result


def to_string(row, column):
    result = value(row, column)

    if result is None:
        return None

    return str(result).strip()


def to_float(row, column):
    result = value(row, column)

    if result is None:
        return None

    try:
        return float(result)
    except (ValueError, TypeError):
        return None


def to_int(row, column):
    result = value(row, column)

    if result is None:
        return None

    try:
        return int(float(result))
    except (ValueError, TypeError):
        return None


def to_bool(row, column):
    result = value(row, column)

    if result is None:
        return None

    if isinstance(result, bool):
        return result

    value_string = str(result).strip().lower()

    if value_string in {"1", "true", "yes"}:
        return True

    if value_string in {"0", "false", "no"}:
        return False

    return None


def to_date(row, column):
    result = value(row, column)

    if result is None:
        return None

    try:
        return pd.to_datetime(result).date()
    except Exception:
        return None


def load_assignments():

    print("=" * 80)
    print("LOADING HISTORICAL ASSIGNMENTS")
    print("=" * 80)

    # ---------------------------------------------------------
    # LOAD CSV
    # ---------------------------------------------------------

    df = load_csv(DATASET)

    required_columns = [
        "assignment_id",
        "project_id",
        "task_id",
        "employee_id",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing assignment columns: {missing}"
        )

    print(
        f"Assignment records found: {len(df):,}"
    )

    db: Session = SessionLocal()

    inserted = 0
    updated = 0
    skipped = 0

    try:

        # ---------------------------------------------------------
        # LOAD EMPLOYEE IDS ONCE
        # ---------------------------------------------------------

        print("\nLoading employee IDs from database...")

        employee_ids = {
            str(employee_id).strip()
            for (employee_id,) in db.query(
                Employee.employee_id
            ).all()
            if employee_id is not None
        }

        print(
            f"Employees loaded: {len(employee_ids):,}"
        )

        # ---------------------------------------------------------
        # LOAD TASK IDS ONCE
        # ---------------------------------------------------------

        print("\nLoading task IDs from database...")

        task_ids = {
            str(task_id).strip()
            for (task_id,) in db.query(
                Task.task_id
            ).all()
            if task_id is not None
        }

        print(
            f"Tasks loaded: {len(task_ids):,}"
        )

        # ---------------------------------------------------------
        # LOAD PROJECT IDS ONCE
        # ---------------------------------------------------------

        print("\nLoading project IDs from database...")

        project_ids = {
            str(project_id).strip()
            for (project_id,) in db.query(
                Project.project_id
            ).all()
            if project_id is not None
        }

        print(
            f"Projects loaded: {len(project_ids):,}"
        )

        # ---------------------------------------------------------
        # LOAD EXISTING ASSIGNMENTS ONCE
        # ---------------------------------------------------------

        print("\nLoading existing assignments...")

        existing_assignments = (
            db.query(Assignment).all()
        )

        assignment_map = {
            str(assignment.assignment_id).strip(): assignment
            for assignment in existing_assignments
            if assignment.assignment_id is not None
        }

        print(
            f"Existing assignments: "
            f"{len(assignment_map):,}"
        )

        # ---------------------------------------------------------
        # PROCESS CSV
        # ---------------------------------------------------------

        print("\nProcessing assignments...")

        processed_since_commit = 0

        for index, row in df.iterrows():

            assignment_id = to_string(
                row,
                "assignment_id"
            )

            project_id = to_string(
                row,
                "project_id"
            )

            task_id = to_string(
                row,
                "task_id"
            )

            employee_id = to_string(
                row,
                "employee_id"
            )

            # -----------------------------------------------------
            # CHECK REQUIRED VALUES
            # -----------------------------------------------------

            if not all([
                assignment_id,
                project_id,
                task_id,
                employee_id,
            ]):

                skipped += 1
                continue

            # -----------------------------------------------------
            # CHECK EMPLOYEE
            # -----------------------------------------------------

            if employee_id not in employee_ids:
                skipped += 1
                continue

            # -----------------------------------------------------
            # CHECK TASK
            # -----------------------------------------------------

            if task_id not in task_ids:
                skipped += 1
                continue

            # -----------------------------------------------------
            # CHECK PROJECT
            # -----------------------------------------------------

            if project_id not in project_ids:
                skipped += 1
                continue

            # -----------------------------------------------------
            # BUILD ASSIGNMENT DATA
            # -----------------------------------------------------

            data = {

                "project_id": project_id,

                "task_id": task_id,

                "employee_id": employee_id,

                "project_domain": to_string(
                    row,
                    "project_domain"
                ),

                "project_type": to_string(
                    row,
                    "project_type"
                ),

                "project_complexity": to_string(
                    row,
                    "project_complexity"
                ),

                "project_criticality": to_string(
                    row,
                    "project_criticality"
                ),

                "role_required": to_string(
                    row,
                    "role_required"
                ),

                "team_size_required": to_int(
                    row,
                    "team_size_required"
                ),

                "estimated_hours": to_float(
                    row,
                    "estimated_hours"
                ),

                "deadline_days": to_int(
                    row,
                    "deadline_days"
                ),

                "priority": to_string(
                    row,
                    "priority"
                ),

                "required_skill_ids": to_string(
                    row,
                    "required_skill_ids"
                ),

                "required_skill_names": to_string(
                    row,
                    "required_skill_names"
                ),

                "required_skill_levels": to_string(
                    row,
                    "required_skill_levels"
                ),

                "critical_skill_ids": to_string(
                    row,
                    "critical_skill_ids"
                ),

                "critical_skill_names": to_string(
                    row,
                    "critical_skill_names"
                ),

                "skill_match_pct": to_float(
                    row,
                    "skill_match_pct"
                ),

                "critical_skill_match_pct": to_float(
                    row,
                    "critical_skill_match_pct"
                ),

                "skill_level_match_pct": to_float(
                    row,
                    "skill_level_match_pct"
                ),

                "experience_match_pct": to_float(
                    row,
                    "experience_match_pct"
                ),

                "domain_match": to_bool(
                    row,
                    "domain_match"
                ),

                "role_match": to_bool(
                    row,
                    "role_match"
                ),

                "critical_project_experience": to_int(
                    row,
                    "critical_project_experience"
                ),

                "performance_score": to_float(
                    row,
                    "performance_score"
                ),

                "current_workload_pct": to_float(
                    row,
                    "current_workload_pct"
                ),

                "availability_pct": to_float(
                    row,
                    "availability_pct"
                ),

                "reliability_score": to_float(
                    row,
                    "reliability_score"
                ),

                "collaboration_score": to_float(
                    row,
                    "collaboration_score"
                ),

                "completion_status": to_string(
                    row,
                    "completion_status"
                ),

                "completion_time_hours": to_float(
                    row,
                    "completion_time_hours"
                ),

                "delay_days": to_float(
                    row,
                    "delay_days"
                ),

                "quality_score": to_float(
                    row,
                    "quality_score"
                ),

                "manager_rating": to_int(
                    row,
                    "manager_rating"
                ),

                "project_success": to_bool(
                    row,
                    "project_success"
                ),

                "task_start_date": to_date(
                    row,
                    "task_start_date"
                ),

                "task_due_date": to_date(
                    row,
                    "task_due_date"
                ),
            }

            # -----------------------------------------------------
            # CHECK EXISTING ASSIGNMENT
            # -----------------------------------------------------

            existing = assignment_map.get(
                assignment_id
            )

            if existing is not None:

                for field, field_value in data.items():

                    setattr(
                        existing,
                        field,
                        field_value
                    )

                updated += 1

            else:

                assignment = Assignment(
                    assignment_id=assignment_id,
                    **data
                )

                db.add(assignment)

                assignment_map[
                    assignment_id
                ] = assignment

                inserted += 1

            processed_since_commit += 1

            # -----------------------------------------------------
            # COMMIT EVERY 1000 RECORDS
            # -----------------------------------------------------

            if processed_since_commit >= BATCH_SIZE:

                db.commit()

                processed_since_commit = 0

                print(
                    f"Processed: {index + 1:,}/"
                    f"{len(df):,} | "
                    f"Inserted: {inserted:,} | "
                    f"Updated: {updated:,} | "
                    f"Skipped: {skipped:,}"
                )

        # ---------------------------------------------------------
        # FINAL COMMIT
        # ---------------------------------------------------------

        db.commit()

        print()
        print("=" * 80)
        print("ASSIGNMENT LOADING COMPLETE")
        print("=" * 80)

        print(f"Inserted : {inserted:,}")
        print(f"Updated  : {updated:,}")
        print(f"Skipped  : {skipped:,}")

        print("=" * 80)

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    load_assignments()
    