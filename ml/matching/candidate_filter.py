from pathlib import Path
import sys

import pandas as pd


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

from ml.matching.skill_engine import (
    calculate_skill_coverage
)


# ============================================================
# CALCULATE CANDIDATE SCORE
# ============================================================

def calculate_candidate_score(
    employee,
    skill_coverage
):
    """
    Calculate a lightweight candidate relevance score.

    This score is NOT the final ML prediction.

    Its purpose is only to reduce thousands of employees
    into a manageable candidate pool for team formation.
    """

    skill_score = (
        skill_coverage[
            "skill_match_pct"
        ]
    )

    critical_skill_score = (
        skill_coverage[
            "critical_skill_match_pct"
        ]
    )

    skill_level_score = (
        skill_coverage[
            "skill_level_match_pct"
        ]
    )

    performance_score = float(
        employee.get(
            "performance_score",
            0
        )
    )

    reliability_score = float(
        employee.get(
            "reliability_score",
            0
        )
    )

    availability_score = float(
        employee.get(
            "availability_pct",
            0
        )
    )

    workload_score = (

        100

        -

        float(
            employee.get(
                "current_workload_pct",
                100
            )
        )
    )


    # --------------------------------------------------------
    # WEIGHTED CANDIDATE SCORE
    # --------------------------------------------------------

    score = (

        skill_score
        * 0.30

        +

        critical_skill_score
        * 0.20

        +

        skill_level_score
        * 0.15

        +

        reliability_score
        * 0.10

        +

        performance_score
        * 0.10

        +

        availability_score
        * 0.10

        +

        workload_score
        * 0.05
    )


    return round(
        score,
        2
    )


# ============================================================
# FILTER CANDIDATES
# ============================================================

def get_top_candidates(
    employees_df,
    task_id,
    task_skills_df,
    employee_skills_df,
    max_workload=85,
    top_n=30
):
    """
    Filter the full employee dataset into the most relevant
    candidate employees for a specific task.

    Steps:

    1. Remove overloaded employees.
    2. Calculate real ESCO skill coverage.
    3. Score candidates.
    4. Return the top N employees.
    """

    # --------------------------------------------------------
    # WORKLOAD FILTER
    # --------------------------------------------------------

    candidates = employees_df[

        employees_df[
            "current_workload_pct"
        ]
        <= max_workload

    ].copy()


    print(
        f"Employees after workload filter: "
        f"{len(candidates)}"
    )


    candidate_results = []


    # ========================================================
    # EVALUATE EMPLOYEES
    # ========================================================

    for _, employee in candidates.iterrows():

        employee_id = employee[
            "employee_id"
        ]


        # ----------------------------------------------------
        # REAL SKILL COVERAGE
        # ----------------------------------------------------

        skill_coverage = (
            calculate_skill_coverage(

                employee_id,

                task_id,

                task_skills_df,

                employee_skills_df
            )
        )


        # ----------------------------------------------------
        # SKIP EMPLOYEES WITH ZERO SKILL MATCH
        # ----------------------------------------------------

        if (

            skill_coverage[
                "skill_match_pct"
            ]
            == 0
        ):

            continue


        # ----------------------------------------------------
        # CANDIDATE SCORE
        # ----------------------------------------------------

        candidate_score = (
            calculate_candidate_score(

                employee,

                skill_coverage
            )
        )


        # ----------------------------------------------------
        # STORE RESULT
        # ----------------------------------------------------

        result = (
            employee.to_dict()
        )


        result.update({

            "candidate_score":
            candidate_score,

            "skill_match_pct":
            skill_coverage[
                "skill_match_pct"
            ],

            "critical_skill_match_pct":
            skill_coverage[
                "critical_skill_match_pct"
            ],

            "skill_level_match_pct":
            skill_coverage[
                "skill_level_match_pct"
            ]

        })


        candidate_results.append(
            result
        )


    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    if not candidate_results:

        return pd.DataFrame()


    candidate_df = pd.DataFrame(
        candidate_results
    )


    # ========================================================
    # SORT
    # ========================================================

    candidate_df = (

        candidate_df

        .sort_values(

            by=
            "candidate_score",

            ascending=False
        )

        .head(
            top_n
        )

        .reset_index(
            drop=True
        )
    )


    return candidate_df