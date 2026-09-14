from pathlib import Path
import sys

import joblib
import pandas as pd


# --------------------------------------------------
# ADD PROJECT ROOT TO PYTHON PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.append(
    str(BASE_DIR)
)


# --------------------------------------------------
# IMPORT PROJECT MODULES
# --------------------------------------------------

from ml.matching.feature_matching import (
    build_matching_features
)

from ml.matching.eligibility import (
    check_employee_eligibility
)

from ml.explainability.explain_prediction import (
    explain_prediction
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
            f"Model not found at: {MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


# --------------------------------------------------
# CREATE ML INPUT
# --------------------------------------------------

def create_assignment_features(
    employee,
    task
):

    # ----------------------------------------------
    # CALCULATE MATCHING FEATURES
    # ----------------------------------------------

    matching_features = (
        build_matching_features(
            employee,
            task
        )
    )


    # ----------------------------------------------
    # COMBINE TASK + EMPLOYEE + MATCHING DATA
    # ----------------------------------------------

    assignment_data = {

        # ------------------------------------------
        # TASK / PROJECT FEATURES
        # ------------------------------------------

        "project_domain":
        task.get(
            "project_domain"
        ),

        "project_type":
        task.get(
            "project_type"
        ),

        "project_complexity":
        task.get(
            "project_complexity"
        ),

        "project_criticality":
        task.get(
            "project_criticality"
        ),

        "role_required":
        task.get(
            "role_required"
        ),

        "team_size_required":
        task.get(
            "team_size_required"
        ),

        "estimated_hours":
        task.get(
            "estimated_hours"
        ),

        "deadline_days":
        task.get(
            "deadline_days"
        ),

        "priority":
        task.get(
            "priority"
        ),


        # ------------------------------------------
        # MATCHING FEATURES
        # ------------------------------------------

        "skill_match_pct":
        matching_features[
            "skill_match_pct"
        ],

        "critical_skill_match_pct":
        matching_features[
            "critical_skill_match_pct"
        ],

        "skill_level_match_pct":
        matching_features[
            "skill_level_match_pct"
        ],

        "experience_match_pct":
        matching_features[
            "experience_match_pct"
        ],

        "domain_match":
        matching_features[
            "domain_match"
        ],

        "role_match":
        matching_features[
            "role_match"
        ],


        # ------------------------------------------
        # EMPLOYEE FEATURES
        # ------------------------------------------

        "critical_project_experience":
        employee.get(
            "critical_project_experience",
            0
        ),

        "performance_score":
        employee.get(
            "performance_score"
        ),

        "current_workload_pct":
        employee.get(
            "current_workload_pct"
        ),

        "availability_pct":
        employee.get(
            "availability_pct"
        ),

        "reliability_score":
        employee.get(
            "reliability_score"
        ),

        "collaboration_score":
        employee.get(
            "collaboration_score"
        )
    }


    return assignment_data


# --------------------------------------------------
# RANK EMPLOYEES
# --------------------------------------------------

def rank_employees(
    employees,
    task,
    model
):

    eligible_results = []

    rejected_results = []


    # ----------------------------------------------
    # CHECK EVERY EMPLOYEE
    # ----------------------------------------------

    for employee in employees:


        # ------------------------------------------
        # CREATE ASSIGNMENT FEATURES
        # ------------------------------------------

        assignment_data = (
            create_assignment_features(
                employee,
                task
            )
        )


        # ------------------------------------------
        # CREATE ELIGIBILITY FEATURES
        # ------------------------------------------

        matching_features = {

            "skill_match_pct":
            assignment_data[
                "skill_match_pct"
            ],

            "critical_skill_match_pct":
            assignment_data[
                "critical_skill_match_pct"
            ],

            "role_match":
            assignment_data[
                "role_match"
            ]
        }


        # ------------------------------------------
        # CHECK ELIGIBILITY
        # ------------------------------------------

        eligibility_result = (
            check_employee_eligibility(
                employee,
                task,
                matching_features
            )
        )


        # ------------------------------------------
        # REJECT EMPLOYEE
        # ------------------------------------------

        if not eligibility_result["eligible"]:

            rejected_results.append({

                "employee_id":
                employee.get(
                    "employee_id"
                ),

                "employee_name":
                employee.get(
                    "name"
                ),

                "reasons":
                eligibility_result[
                    "reasons"
                ]
            })

            continue


        # ------------------------------------------
        # PREDICT SUCCESS PROBABILITY
        # ------------------------------------------

        input_df = pd.DataFrame(
            [assignment_data]
        )


        probability = (
            model.predict_proba(
                input_df
            )[0][1]
        )


        # ------------------------------------------
        # GENERATE SHAP EXPLANATION
        # ------------------------------------------

        explanation = (
            explain_prediction(
                model,
                assignment_data
            )
        )


        # Keep only top 5 factors

        top_explanations = (
            explanation[:5]
        )


        # ------------------------------------------
        # STORE ELIGIBLE RESULT
        # ------------------------------------------

        eligible_results.append({

            "employee_id":
            employee.get(
                "employee_id"
            ),

            "employee_name":
            employee.get(
                "name"
            ),

            "success_probability":
            round(
                float(probability) * 100,
                2
            ),

            "skill_match_pct":
            assignment_data[
                "skill_match_pct"
            ],

            "critical_skill_match_pct":
            assignment_data[
                "critical_skill_match_pct"
            ],

            "experience_match_pct":
            assignment_data[
                "experience_match_pct"
            ],

            "role_match":
            assignment_data[
                "role_match"
            ],

            "current_workload_pct":
            employee.get(
                "current_workload_pct"
            ),

            # --------------------------------------
            # SHAP EXPLANATIONS
            # --------------------------------------

            "why_recommended":
            top_explanations
        })


    # ----------------------------------------------
    # SORT ELIGIBLE EMPLOYEES
    # ----------------------------------------------

    ranked_results = sorted(

        eligible_results,

        key=lambda x:
        x[
            "success_probability"
        ],

        reverse=True
    )


    # ----------------------------------------------
    # ADD RANK
    # ----------------------------------------------

    for index, employee in enumerate(

        ranked_results,

        start=1
    ):

        employee[
            "rank"
        ] = index


    # ----------------------------------------------
    # RETURN RESULTS
    # ----------------------------------------------

    return {

        "ranked_employees":
        ranked_results,

        "rejected_employees":
        rejected_results
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "Loading trained model..."
    )

    model = load_model()

    print(
        "Model loaded successfully!"
    )


    # ----------------------------------------------
    # SAMPLE TASK
    # ----------------------------------------------

    task = {

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
        # MATCHING REQUIREMENTS
        # ------------------------------------------

        "required_skills": [

            "Python",

            "Django",

            "REST API"
        ],

        "critical_skills": [

            "Python",

            "Django"
        ],

        "required_experience":
        3,

        "required_skill_level":
        7
    }


    # ----------------------------------------------
    # SAMPLE EMPLOYEES
    # ----------------------------------------------

    employees = [


        # ------------------------------------------
        # ALICE
        # ------------------------------------------

        {

            "employee_id":
            "EMP-001",

            "name":
            "Alice",

            "skills": [

                "Python",

                "Django",

                "REST API",

                "PostgreSQL"
            ],

            "role":
            "Backend Developer",

            "domains": [

                "Travel",

                "Finance"
            ],

            "years_experience":
            5,

            "skill_level":
            8,

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
        },


        # ------------------------------------------
        # BOB
        # ------------------------------------------

        {

            "employee_id":
            "EMP-002",

            "name":
            "Bob",

            "skills": [

                "Python",

                "Flask",

                "SQL"
            ],

            "role":
            "Backend Developer",

            "domains": [

                "Travel"
            ],

            "years_experience":
            3,

            "skill_level":
            6,

            "critical_project_experience":
            0,

            "performance_score":
            75,

            "current_workload_pct":
            60,

            "availability_pct":
            40,

            "reliability_score":
            78,

            "collaboration_score":
            80
        },


        # ------------------------------------------
        # CHARLIE
        # ------------------------------------------

        {

            "employee_id":
            "EMP-003",

            "name":
            "Charlie",

            "skills": [

                "Java",

                "Spring Boot",

                "Microservices"
            ],

            "role":
            "Backend Developer",

            "domains": [

                "Finance"
            ],

            "years_experience":
            7,

            "skill_level":
            9,

            "critical_project_experience":
            1,

            "performance_score":
            88,

            "current_workload_pct":
            45,

            "availability_pct":
            65,

            "reliability_score":
            90,

            "collaboration_score":
            85
        }
    ]


    # ----------------------------------------------
    # RANK EMPLOYEES
    # ----------------------------------------------

    results = rank_employees(

        employees,

        task,

        model
    )


    ranked_employees = (

        results[
            "ranked_employees"
        ]
    )


    rejected_employees = (

        results[
            "rejected_employees"
        ]
    )


    # ----------------------------------------------
    # DISPLAY RECOMMENDED EMPLOYEES
    # ----------------------------------------------

    print(
        "\nRECOMMENDED EMPLOYEES"
    )

    print(
        "=" * 60
    )


    if not ranked_employees:

        print(
            "\nNo eligible employees found."
        )


    for employee in ranked_employees:


        print(
            f"\nRank "
            f"{employee['rank']}"
        )


        print(
            f"Employee: "
            f"{employee['employee_name']}"
        )


        print(
            f"Success Probability: "
            f"{employee['success_probability']}%"
        )


        print(
            f"Skill Match: "
            f"{employee['skill_match_pct']}%"
        )


        print(
            f"Critical Skill Match: "
            f"{employee['critical_skill_match_pct']}%"
        )


        print(
            f"Experience Match: "
            f"{employee['experience_match_pct']}%"
        )


        print(
            f"Current Workload: "
            f"{employee['current_workload_pct']}%"
        )


        # ------------------------------------------
        # DISPLAY SHAP EXPLANATION
        # ------------------------------------------

        print(
            "\nWhy Recommended:"
        )


        for explanation in employee[
            "why_recommended"
        ]:


            if (
                explanation[
                    "direction"
                ]
                == "positive"
            ):

                symbol = "+"

            else:

                symbol = "-"


            print(

                f"{symbol} "
                f"{explanation['factor']} "
                f"(Impact: "
                f"{explanation['impact']})"

            )


    # ----------------------------------------------
    # DISPLAY REJECTED EMPLOYEES
    # ----------------------------------------------

    print(
        "\n\nNOT ELIGIBLE EMPLOYEES"
    )

    print(
        "=" * 60
    )


    if not rejected_employees:

        print(
            "\nAll employees are eligible."
        )


    for employee in rejected_employees:


        print(
            f"\nEmployee: "
            f"{employee['employee_name']}"
        )


        print(
            "Reasons:"
        )


        for reason in employee[
            "reasons"
        ]:

            print(
                f"- {reason}"
            )