import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.skill import Skill
from app.etl.csv_reader import load_csv, clean_dataframe


FILE_NAME = "esco_skill_reference.csv"


def load_skills(db: Session):

    print("\nLoading ESCO skills...")

    df = load_csv(FILE_NAME)

    df = clean_dataframe(df)

    print("Columns detected:")
    print(df.columns.tolist())

    if "skill_id" not in df.columns:
        raise ValueError(
            "skill_id column not found in ESCO skill reference."
        )

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():

        skill_id = row.get("skill_id")

        if pd.isna(skill_id):
            skipped += 1
            continue

        skill_id = str(
            skill_id
        ).strip()

        skill = (
            db.query(Skill)
            .filter(
                Skill.skill_id == skill_id
            )
            .first()
        )

        skill_name = None
        description = None

        if "skill_name" in df.columns:
            value = row["skill_name"]

            if not pd.isna(value):
                skill_name = str(value).strip()

        if "description" in df.columns:
            value = row["description"]

            if not pd.isna(value):
                description = str(value).strip()

        if skill is None:

            skill = Skill(
                skill_id=skill_id,
                skill_name=skill_name,
                description=description
            )

            db.add(skill)

            inserted += 1

        else:

            skill.skill_name = skill_name
            skill.description = description

            updated += 1

    db.commit()

    print("\nSkill loading complete.")

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

        load_skills(db)

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()