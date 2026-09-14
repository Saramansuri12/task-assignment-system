import os
import pandas as pd


PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        ".."
    )
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "data"
)


CSV_FILES = [
    "employee_derived_attributes.csv",
    "employee_skill_profiles.csv",
    "esco_skill_reference.csv",
    "projects_tasks.csv",
    "task_assignments.csv",
    "task_required_skills.csv",
]


def inspect_csv(file_name: str):

    file_path = os.path.join(
        DATA_DIR,
        file_name
    )

    print("\n" + "=" * 80)
    print(f"FILE: {file_name}")
    print("=" * 80)

    if not os.path.exists(file_path):
        print("FILE NOT FOUND")
        print(f"Expected location: {file_path}")
        return

    try:
        df = pd.read_csv(file_path)

        print(f"\nRows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")

        print("\nCOLUMN INFORMATION")
        print("-" * 80)

        for column in df.columns:

            dtype = df[column].dtype
            missing = df[column].isna().sum()
            unique = df[column].nunique()

            print(
                f"{column:<40} "
                f"type={str(dtype):<12} "
                f"missing={missing:<8} "
                f"unique={unique}"
            )

        print("\nFIRST 3 RECORDS")
        print("-" * 80)

        print(
            df.head(3).to_string(index=False)
        )

    except Exception as e:

        print(f"ERROR reading {file_name}")
        print(str(e))


def main():

    print("\n")
    print("=" * 80)
    print("TASK ASSIGNMENT SYSTEM - DATASET INSPECTOR")
    print("=" * 80)

    print(f"\nDataset directory:")
    print(DATA_DIR)

    for file_name in CSV_FILES:
        inspect_csv(file_name)

    print("\n")
    print("=" * 80)
    print("DATASET INSPECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()