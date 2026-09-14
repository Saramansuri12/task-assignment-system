from pathlib import Path
import sys

BASE_DIR = Path(
    __file__
).resolve().parents[2]

sys.path.append(
    str(BASE_DIR)
)


from ml.data.employee_loader import (
    load_employee_profiles
)

from ml.matching.skill_engine import (
    load_skill_data
)

from ml.matching.candidate_filter import (
    get_top_candidates
)

from ml.matching.team_formation import (
    form_best_team
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading employee data...")

employees = (
    load_employee_profiles()
)


print("Loading skill data...")

task_skills, employee_skills = (
    load_skill_data()
)


# ============================================================
# SELECT TASK
# ============================================================

task_id = (
    task_skills[
        "task_id"
    ].iloc[0]
)


# ============================================================
# TASK DETAILS
# ============================================================

task = {

    "task_id":
    task_id,

    "team_size_required":
    5,

    "project_criticality":
    "Medium"
}


print(
    f"\nTask ID: {task_id}"
)


# ============================================================
# GET CANDIDATES
# ============================================================

print(
    "\nFinding relevant candidates..."
)


candidates = (

    get_top_candidates(

        employees_df=
        employees,

        task_id=
        task_id,

        task_skills_df=
        task_skills,

        employee_skills_df=
        employee_skills,

        top_n=
        30
    )

)


print(
    f"Candidates found: "
    f"{len(candidates)}"
)


# ============================================================
# FORM TEAM
# ============================================================

print(
    "\nForming best team..."
)


result = (

    form_best_team(

        candidates_df=
        candidates,

        task=
        task,

        task_skills_df=
        task_skills,

        employee_skills_df=
        employee_skills
    )

)


# ============================================================
# DISPLAY TEAM
# ============================================================

team = result[
    "team"
]


print(
    "\nRECOMMENDED TEAM"
)

print(
    "=" * 80
)


if team.empty:

    print(
        "No suitable team found."
    )

else:

    columns = [

        "employee_id",

        "job_title",

        "candidate_score",

        "skill_match_pct",

        "current_workload_pct",

        "availability_pct",

        "reliability_score"
    ]


    print(

        team[
            columns
        ]

        .to_string(
            index=False
        )
    )


# ============================================================
# TEAM SCORE
# ============================================================

print(
    "\nTEAM SCORE:"
)

print(
    result[
        "team_score"
    ]
)


# ============================================================
# EXPLANATION
# ============================================================

print(
    "\nWHY THIS TEAM?"
)

print(
    "=" * 80
)


for reason in result[
    "reasons"
]:

    print(
        f"- {reason}"
    )