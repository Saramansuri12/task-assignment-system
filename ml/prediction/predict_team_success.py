from pathlib import Path
import sys

import joblib
import pandas as pd


# ============================================================
# ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]

sys.path.append(
    str(BASE_DIR)
)


# ============================================================
# IMPORT PROJECT MODULES
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

from ml.matching.team_formation import (
    form_best_team
)

from ml.matching.team_features import (
    build_team_features
)


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "xgboost_assignment_model.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


# ============================================================
# CREATE MODEL INPUT
# ============================================================

def create_team_model_input(
    task,
    team_features,
    team_coverage
):
    """
    Combine task features and aggregated
    team features into the feature structure
    expected by the XGBoost model.
    """

    assignment_data = {

        # ----------------------------------------------------
        # TASK / PROJECT FEATURES
        # ----------------------------------------------------

        "project_domain":
        task.get(
            "project_domain",
            "Technology"
        ),

        "project_type":
        task.get(
            "project_type",
            "Development"
        ),

        "project_complexity":
        task.get(
            "project_complexity",
            "Moderate"
        ),

        "project_criticality":
        task.get(
            "project_criticality",
            "Medium"
        ),

        "role_required":
        task.get(
            "role_required",
            "Developer"
        ),

        "team_size_required":
        task.get(
            "team_size_required",
            1
        ),

        "estimated_hours":
        task.get(
            "estimated_hours",
            100
        ),

        "deadline_days":
        task.get(
            "deadline_days",
            30
        ),

        "priority":
        task.get(
            "priority",
            "Medium"
        ),


        # ----------------------------------------------------
        # TEAM SKILL FEATURES
        # ----------------------------------------------------

        "skill_match_pct":
        team_coverage.get(
            "skill_coverage_pct",
            team_features[
                "skill_match_pct"
            ]
        ),

        "critical_skill_match_pct":
        team_coverage.get(
            "critical_skill_coverage_pct",
            team_features[
                "critical_skill_match_pct"
            ]
        ),

        "skill_level_match_pct":
        team_coverage.get(
            "skill_level_coverage_pct",
            team_features[
                "skill_level_match_pct"
            ]
        ),


        # ----------------------------------------------------
        # EXPERIENCE / MATCHING FEATURES
        # ----------------------------------------------------

        "experience_match_pct":
        task.get(
            "experience_match_pct",
            100
        ),

        "domain_match":
        task.get(
            "domain_match",
            1
        ),

        "role_match":
        task.get(
            "role_match",
            1
        ),


        # ----------------------------------------------------
        # AGGREGATED TEAM FEATURES
        # ----------------------------------------------------

        "critical_project_experience":
        team_features[
            "critical_project_experience"
        ],

        "performance_score":
        team_features[
            "performance_score"
        ],

        "current_workload_pct":
        team_features[
            "current_workload_pct"
        ],

        "availability_pct":
        team_features[
            "availability_pct"
        ],

        "reliability_score":
        team_features[
            "reliability_score"
        ],

        "collaboration_score":
        team_features[
            "collaboration_score"
        ]
    }


    return pd.DataFrame(
        [assignment_data]
    )


# ============================================================
# PREDICT TEAM SUCCESS
# ============================================================

def predict_team_success(
    task,
    team,
    team_coverage,
    model
):
    """
    Predict the probability that the
    selected team successfully completes
    the task/project.
    """

    # --------------------------------------------------------
    # BUILD TEAM FEATURES
    # --------------------------------------------------------

    team_features = (

        build_team_features(
            team
        )

    )


    # --------------------------------------------------------
    # CREATE MODEL INPUT
    # --------------------------------------------------------

    input_df = (

        create_team_model_input(

            task,

            team_features,

            team_coverage
        )

    )


    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------

    probability = (

        model.predict_proba(
            input_df
        )[0][1]

    )


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {

        "success_probability":
        round(
            float(probability) * 100,
            2
        ),

        "team_features":
        team_features,

        "model_input":
        input_df
    }


# ============================================================
# TEST COMPLETE PIPELINE
# ============================================================

if __name__ == "__main__":


    # ========================================================
    # LOAD MODEL
    # ========================================================

    print(
        "Loading XGBoost model..."
    )

    model = (
        load_model()
    )


    # ========================================================
    # LOAD EMPLOYEES
    # ========================================================

    print(
        "Loading employee data..."
    )

    employees = (

        load_employee_profiles()
    )


    # ========================================================
    # LOAD SKILL DATA
    # ========================================================

    print(
        "Loading skill data..."
    )

    task_skills, employee_skills = (

        load_skill_data()
    )


    # ========================================================
    # SELECT TASK
    # ========================================================

    task_id = (

        task_skills[
            "task_id"
        ].iloc[0]

    )


    # ========================================================
    # SAMPLE TASK DETAILS
    # ========================================================

    task = {

        "task_id":
        task_id,

        "project_domain":
        "Technology",

        "project_type":
        "Development",

        "project_complexity":
        "Moderate",

        "project_criticality":
        "Medium",

        "role_required":
        "Developer",

        "team_size_required":
        5,

        "estimated_hours":
        120,

        "deadline_days":
        30,

        "priority":
        "Medium"
    }


    print(
        f"\nTask ID: {task_id}"
    )


    # ========================================================
    # FIND CANDIDATES
    # ========================================================

    print(
        "\nFinding candidates..."
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


    # ========================================================
    # FORM TEAM
    # ========================================================

    print(
        "\nForming best team..."
    )

    team_result = (

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


    team = (

        team_result[
            "team"
        ]

    )


    # ========================================================
    # PREDICT SUCCESS
    # ========================================================

    print(
        "\nPredicting team success..."
    )

    prediction = (

        predict_team_success(

            task=
            task,

            team=
            team,

            team_coverage=
            team_result[
                "skill_coverage"
            ],

            model=
            model
        )

    )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print(

        "\n"

        +

        "=" * 60

    )

    print(
        "FINAL TEAM ASSIGNMENT RESULT"
    )

    print(
        "=" * 60
    )


    print(

        f"\nTeam Size: "
        f"{len(team)}"

    )


    print(

        f"Team Quality Score: "
        f"{team_result['team_score']}"

    )


    print(

        f"Skill Coverage: "
        f"{team_result['skill_coverage']['skill_coverage_pct']}%"

    )


    print(

        f"Critical Skill Coverage: "
        f"{team_result['skill_coverage']['critical_skill_coverage_pct']}%"

    )


    print(

        f"\nPROJECT SUCCESS PROBABILITY: "
        f"{prediction['success_probability']}%"

    )


    # ========================================================
    # DISPLAY TEAM
    # ========================================================

    print(
        "\nSELECTED TEAM"
    )

    print(
        "=" * 60
    )


    display_columns = [

        "employee_id",

        "job_title",

        "candidate_score",

        "current_workload_pct",

        "availability_pct",

        "reliability_score"
    ]


    print(

        team[
            display_columns
        ]

        .to_string(
            index=False
        )

    )