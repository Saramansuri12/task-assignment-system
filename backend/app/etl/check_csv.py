from pathlib import Path
import csv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


FILES = [
    "task_assignments.csv",
    "projects_tasks.csv",
    "task_required_skills.csv",
    "employee_skill_profiles.csv",
    "employee_derived_attributes.csv",
    "esco_skill_reference.csv",
]


def main():

    print("\n" + "=" * 70)
    print("CSV DATASET CHECK")
    print("=" * 70)

    print("Data directory:")
    print(DATA_DIR)
    print()

    for filename in FILES:

        path = DATA_DIR / filename

        if not path.exists():
            print(f"[MISSING] {filename}")
            continue

        if path.stat().st_size == 0:
            print(f"[EMPTY]   {filename}")
            continue

        try:
            with open(
                path,
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:

                reader = csv.reader(file)

                header = next(reader)

                rows = sum(1 for _ in reader)

            print(
                f"[OK] {filename:<35} "
                f"{rows:,} rows"
            )

            print(
                f"     columns: {len(header)}"
            )

        except Exception as e:

            print(
                f"[ERROR] {filename}: {e}"
            )

    print("=" * 70)


if __name__ == "__main__":
    main()