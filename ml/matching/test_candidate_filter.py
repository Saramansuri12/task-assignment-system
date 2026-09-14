from pathlib import Path
import sys


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.append(
    str(BASE_DIR)
)


# ============================================================
# IMPORTS
# ============================================================

from ml.data.employee_loader import (
    load_employee_profiles
)

from ml.matching.skill_engine import (
    load_skill_data
)

from ml.matching.candidate_filter import (
    get_top_candidates
)


# ============================================================
# LOAD EMPLOYEE DATA
# ============================================================

print("Loading employee data...")

employees = load_employee_profiles()


# ============================================================
# LOAD SKILL DATA
# ============================================================

print("Loading skill data...")

task_skills, employee_skills = (
    load_skill_data()
)


# ============================================================
# SELECT A REAL TASK
# ============================================================

task_id = (
    task_skills[
        "task_id"
    ].iloc[0]
)


print(
    f"\nTesting Task ID: {task_id}"
)


# ============================================================
# GET TOP CANDIDATES
# ============================================================

candidates = get_top_candidates(

    employees_df=employees,

    task_id=task_id,

    task_skills_df=task_skills,

    employee_skills_df=employee_skills,

    max_workload=85,

    top_n=30
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\nTOP CANDIDATES")

print("=" * 80)


if candidates.empty:

    print(
        "No suitable candidates found."
    )

else:

    columns = [

        "employee_id",

        "job_title",

        "candidate_score",

        "skill_match_pct",

        "critical_skill_match_pct",

        "skill_level_match_pct",

        "current_workload_pct",

        "availability_pct"
    ]


    print(

        candidates[
            columns
        ]

        .head(10)

        .to_string(
            index=False
        )
    )