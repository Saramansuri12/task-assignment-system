from app.db.database import SessionLocal

from app.db.models import (
    Employee,
    Skill,
    EmployeeSkill,
    Project,
    Task,
    TaskSkill,
    Assignment,
)


def main():
    db = SessionLocal()

    try:
        print("\n" + "=" * 60)
        print("DATABASE CONTENT CHECK")
        print("=" * 60)

        tables = {
            "Employees": Employee,
            "Skills": Skill,
            "Employee Skills": EmployeeSkill,
            "Projects": Project,
            "Tasks": Task,
            "Task Skills": TaskSkill,
            "Assignments": Assignment,
        }

        for name, model in tables.items():
            count = db.query(model).count()
            print(f"{name:<20}: {count}")

        print("=" * 60)

    except Exception as e:
        print("\nDATABASE ERROR:")
        print(type(e).__name__)
        print(str(e))

    finally:
        db.close()


if __name__ == "__main__":
    main()