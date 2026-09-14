from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# DATA PATH
# ============================================================

EMPLOYEE_DATA_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "employee_derived_attributes.csv"
)


# ============================================================
# LOAD EMPLOYEE DATA
# ============================================================

def load_employee_profiles():

    if not EMPLOYEE_DATA_PATH.exists():

        raise FileNotFoundError(
            f"Employee dataset not found: "
            f"{EMPLOYEE_DATA_PATH}"
        )


    employees = pd.read_csv(
        EMPLOYEE_DATA_PATH
    )


    # --------------------------------------------------------
    # STANDARDIZE COLUMN NAMES
    # --------------------------------------------------------

    employees = employees.rename(
        columns={

            "Performance_Score":
            "performance_score",

            "Years_At_Company":
            "years_experience",

            "Department":
            "department",

            "Job_Title":
            "job_title",

            "Education_Level":
            "education_level",

            "Projects_Handled":
            "projects_handled"
        }
    )


    # --------------------------------------------------------
    # DERIVE WORKLOAD
    # --------------------------------------------------------

    employees[
        "current_workload_pct"
    ] = (
        employees[
            "baseline_load"
        ]
        * 100
    ).round(2)


    # --------------------------------------------------------
    # DERIVE AVAILABILITY
    # --------------------------------------------------------

    employees[
        "availability_pct"
    ] = (
        (
            1
            -
            employees[
                "baseline_load"
            ]
        )
        * 100
    ).round(2)


    # --------------------------------------------------------
    # NORMALIZE PERFORMANCE SCORE
    # --------------------------------------------------------

    employees[
        "performance_score"
    ] = (
        employees[
            "performance_score"
        ]
        /
        5
        *
        100
    ).round(2)


    # --------------------------------------------------------
    # CLEAN NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = [

        "years_experience",
        "performance_score",
        "reliability_score",
        "collaboration_score",
        "critical_project_experience",
        "current_workload_pct",
        "availability_pct"
    ]


    for column in numeric_columns:

        employees[column] = (
            employees[column]
            .fillna(0)
        )


    return employees


# ============================================================
# GET EMPLOYEE
# ============================================================

def get_employee(
    employee_id,
    employees_df
):

    employee = employees_df[
        employees_df[
            "employee_id"
        ]
        == employee_id
    ]


    if employee.empty:

        return None


    return employee.iloc[0]


# ============================================================
# GET CANDIDATES
# ============================================================

def get_candidate_employees(
    employees_df,
    max_workload=85
):

    candidates = employees_df[

        employees_df[
            "current_workload_pct"
        ]
        <= max_workload

    ].copy()


    return candidates