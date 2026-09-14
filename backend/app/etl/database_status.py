from sqlalchemy import text

from app.db.database import SessionLocal


TABLES = [
    "employees",
    "skills",
    "projects",
    "tasks",
    "employee_skills",
    "task_skills",
    "assignments",
]


def check_database():

    print()
    print("=" * 80)
    print("DATABASE STATUS")
    print("=" * 80)

    db = SessionLocal()

    try:

        for table in TABLES:

            try:

                result = db.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                )

                count = result.scalar() or 0

                status = "OK" if count > 0 else "EMPTY"

                print(
                    f"{table:<25} "
                    f"{count:>10,} records   "
                    f"[{status}]"
                )

            except Exception as exc:

                print(
                    f"{table:<25} ERROR: {exc}"
                )

                db.rollback()

    finally:

        db.close()

    print("=" * 80)


if __name__ == "__main__":
    check_database()