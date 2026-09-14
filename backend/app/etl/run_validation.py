from app.etl.csv_reader import load_csv


DATASETS = [
    "employee_derived_attributes.csv",
    "employee_skill_profiles.csv",
    "esco_skill_reference.csv",
    "projects_tasks.csv",
    "task_assignments.csv",
    "task_required_skills.csv",
]


def main():

    print("=" * 80)
    print("TASK ASSIGNMENT SYSTEM")
    print("DATASET VALIDATION")
    print("=" * 80)

    for dataset in DATASETS:

        try:

            df = load_csv(dataset)

            print(
                f"SUCCESS: {dataset}"
            )

        except Exception as exc:

            print(
                f"FAILED: {dataset}"
            )

            print(
                f"ERROR: {exc}"
            )

    print("\n")
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()