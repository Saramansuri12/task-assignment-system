from pathlib import Path
import sys

import joblib
import pandas as pd
import shap


# --------------------------------------------------
# ADD PROJECT ROOT TO PYTHON PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.append(
    str(BASE_DIR)
)


# --------------------------------------------------
# MODEL PATH
# --------------------------------------------------

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "xgboost_assignment_model.pkl"
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


# --------------------------------------------------
# CLEAN FEATURE NAME
# --------------------------------------------------

def clean_feature_name(
    feature_name
):

    # Remove preprocessing prefixes

    feature_name = (
        feature_name
        .replace(
            "numerical__",
            ""
        )
        .replace(
            "categorical__",
            ""
        )
    )


    # ----------------------------------------------
    # FEATURE NAME MAPPING
    # ----------------------------------------------

    feature_mapping = {

        # Matching Features

        "skill_match_pct":
        "Skill Match",

        "critical_skill_match_pct":
        "Critical Skill Match",

        "skill_level_match_pct":
        "Skill Level Match",

        "experience_match_pct":
        "Experience Match",

        "domain_match":
        "Domain Match",

        "role_match":
        "Role Match",


        # Employee Features

        "performance_score":
        "Performance Score",

        "current_workload_pct":
        "Current Workload",

        "availability_pct":
        "Availability",

        "reliability_score":
        "Reliability Score",

        "collaboration_score":
        "Collaboration Score",

        "critical_project_experience":
        "Critical Project Experience",


        # Task Features

        "team_size_required":
        "Required Team Size",

        "estimated_hours":
        "Estimated Hours",

        "deadline_days":
        "Deadline Days",

        "project_domain":
        "Project Domain",

        "project_type":
        "Project Type",

        "project_complexity":
        "Project Complexity",

        "project_criticality":
        "Project Criticality",

        "role_required":
        "Required Role",

        "priority":
        "Priority"
    }


    # ----------------------------------------------
    # HANDLE NORMAL AND ONE-HOT FEATURES
    # ----------------------------------------------

    for key, value in feature_mapping.items():

        # Exact numerical feature match

        if feature_name == key:

            return value


        # One-hot encoded categorical feature

        if feature_name.startswith(
            key + "_"
        ):

            category = feature_name[
                len(key) + 1:
            ]

            return (
                f"{value}: {category}"
            )


    # ----------------------------------------------
    # FALLBACK
    # ----------------------------------------------

    return (
        feature_name
        .replace(
            "_",
            " "
        )
        .title()
    )


# --------------------------------------------------
# EXPLAIN PREDICTION
# --------------------------------------------------

def explain_prediction(
    pipeline,
    assignment_data
):

    # ----------------------------------------------
    # CONVERT INPUT TO DATAFRAME
    # ----------------------------------------------

    input_df = pd.DataFrame(
        [assignment_data]
    )


    # ----------------------------------------------
    # EXTRACT PIPELINE COMPONENTS
    # ----------------------------------------------

    preprocessor = (
        pipeline.named_steps[
            "preprocessor"
        ]
    )

    model = (
        pipeline.named_steps[
            "model"
        ]
    )


    # ----------------------------------------------
    # PREPROCESS INPUT
    # ----------------------------------------------

    processed_input = (
        preprocessor.transform(
            input_df
        )
    )


    # ----------------------------------------------
    # GET FEATURE NAMES
    # ----------------------------------------------

    feature_names = (
        preprocessor.get_feature_names_out()
    )


    # ----------------------------------------------
    # CREATE SHAP EXPLAINER
    # ----------------------------------------------

    explainer = shap.TreeExplainer(
        model
    )


    # ----------------------------------------------
    # CALCULATE SHAP VALUES
    # ----------------------------------------------

    shap_values = (
        explainer.shap_values(
            processed_input
        )
    )


    # ----------------------------------------------
    # HANDLE DIFFERENT SHAP OUTPUT FORMATS
    # ----------------------------------------------

    if isinstance(
        shap_values,
        list
    ):

        # Binary classification positive class

        shap_values = (
            shap_values[1]
        )


    # ----------------------------------------------
    # CREATE CONTRIBUTIONS
    # ----------------------------------------------

    contributions = []


    for index, (
        feature,
        value
    ) in enumerate(

        zip(
            feature_names,
            shap_values[0]
        )

    ):


        # ------------------------------------------
        # GET PROCESSED FEATURE VALUE
        # ------------------------------------------

        feature_value = (
            processed_input[
                0,
                index
            ]
        )


        # ------------------------------------------
        # SKIP INACTIVE ONE-HOT FEATURES
        # ------------------------------------------

        # For categorical features, only show the
        # category that is active (value = 1).

        if feature.startswith(
            "categorical__"
        ):

            if feature_value == 0:

                continue


        # ------------------------------------------
        # SHAP IMPACT
        # ------------------------------------------

        impact = round(
            float(value),
            4
        )


        # ------------------------------------------
        # STORE CONTRIBUTION
        # ------------------------------------------

        contributions.append({

            "factor":
            clean_feature_name(
                feature
            ),

            "impact":
            impact,

            "direction":
            (
                "positive"
                if impact > 0
                else "negative"
            )

        })


    # ----------------------------------------------
    # SORT BY ABSOLUTE IMPACT
    # ----------------------------------------------

    contributions = sorted(

        contributions,

        key=lambda x:
        abs(
            x["impact"]
        ),

        reverse=True
    )


    return contributions


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "Loading trained model..."
    )

    pipeline = load_model()

    print(
        "Model loaded successfully!"
    )


    # ----------------------------------------------
    # SAMPLE ASSIGNMENT DATA
    # ----------------------------------------------

    assignment_data = {

        # ------------------------------------------
        # PROJECT / TASK FEATURES
        # ------------------------------------------

        "project_domain":
        "Travel",

        "project_type":
        "API Development",

        "project_complexity":
        "Moderate",

        "project_criticality":
        "Low",

        "role_required":
        "Backend Developer",

        "team_size_required":
        5,

        "estimated_hours":
        120,

        "deadline_days":
        30,

        "priority":
        "Medium",


        # ------------------------------------------
        # MATCHING FEATURES
        # ------------------------------------------

        "skill_match_pct":
        100.0,

        "critical_skill_match_pct":
        100.0,

        "skill_level_match_pct":
        100.0,

        "experience_match_pct":
        100.0,

        "domain_match":
        1,

        "role_match":
        1,


        # ------------------------------------------
        # EMPLOYEE FEATURES
        # ------------------------------------------

        "critical_project_experience":
        1,

        "performance_score":
        90,

        "current_workload_pct":
        25,

        "availability_pct":
        80,

        "reliability_score":
        92,

        "collaboration_score":
        88
    }


    # ----------------------------------------------
    # EXPLAIN PREDICTION
    # ----------------------------------------------

    contributions = (
        explain_prediction(
            pipeline,
            assignment_data
        )
    )


    # ----------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------

    print(
        "\nWHY THIS ASSIGNMENT WAS RECOMMENDED"
    )

    print(
        "=" * 60
    )


    # ----------------------------------------------
    # DISPLAY TOP 10 FACTORS
    # ----------------------------------------------

    for contribution in contributions[:10]:

        if (
            contribution[
                "direction"
            ]
            == "positive"
        ):

            direction_symbol = "+"

        else:

            direction_symbol = "-"


        print(

            f"{direction_symbol} "
            f"{contribution['factor']} "
            f"| Impact: "
            f"{contribution['impact']}"

        )