import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.task import Task
from app.db.models.skill import Skill
from app.db.models.task_skill import TaskSkill
from app.etl.csv_reader import load_csv, clean_dataframe


FILE_NAME = "task_required_skills.csv"
FALLBACK_FILE_NAME = "task_assignments.csv"


def load_task_skills(db: Session):

    print("\nLoading task required skills...")

    try:
        df = load_csv(FILE_NAME)
    except RuntimeError as exc:
        if "No columns to parse from file" not in str(exc):
            raise

        print(
            f"{FILE_NAME} is empty; deriving task skills from "
            f"{FALLBACK_FILE_NAME}."
        )
        df = load_csv(FALLBACK_FILE_NAME)

    df = clean_dataframe(df)

    print("Columns detected:")
    print(df.columns.tolist())

    if "task_id" not in df.columns:
        raise ValueError(
            "task_id column not found."
        )

    if "skill_id" not in df.columns and "required_skill_ids" not in df.columns:
        raise ValueError(
            "skill_id or required_skill_ids column not found."
        )

    fallback_format = "required_skill_ids" in df.columns

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():

        task_id = row["task_id"]

        if fallback_format:
            skill_ids = str(row.get("required_skill_ids", "")).split("|")
            levels = str(row.get("required_skill_levels", "")).split("|")
            critical_ids = set(
                str(row.get("critical_skill_ids", "")).split("|")
            )
            skill_rows = [
                (skill_id, levels[index] if index < len(levels) else None,
                 skill_id in critical_ids)
                for index, skill_id in enumerate(skill_ids)
                if skill_id and skill_id != "nan"
            ]
        else:
            skill_rows = [(row["skill_id"], row.get("required_level"), False)]

        if pd.isna(task_id):
            skipped += 1
            continue

        task_id = str(task_id).strip()

        for skill_id, level_value, is_critical in skill_rows:
            skill_id = str(skill_id).strip()

            task = db.query(Task).filter(Task.task_id == task_id).first()
            skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()

            if task is None or skill is None:
                skipped += 1
                continue

            relationship = (
                db.query(TaskSkill)
                .filter(
                    TaskSkill.task_id == task_id,
                    TaskSkill.skill_id == skill_id
                )
                .first()
            )

            required_level = None
            if level_value is not None and not pd.isna(level_value):
                required_level = float(level_value)

            if relationship is None:
                db.add(TaskSkill(
                    task_id=task_id,
                    skill_id=skill_id,
                    required_level=required_level,
                    is_critical=is_critical
                ))
                inserted += 1
            else:
                relationship.required_level = required_level
                relationship.is_critical = is_critical
                updated += 1

    db.commit()

    print("\nTask skill loading complete.")

    print(f"Inserted : {inserted:,}")
    print(f"Updated  : {updated:,}")
    print(f"Skipped  : {skipped:,}")


def main():

    db = SessionLocal()

    try:

        load_task_skills(db)

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()