from pathlib import Path
import sys


# ============================================================
# ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]


if str(BASE_DIR) not in sys.path:

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


from ml.matching.adaptive_team_builder import (
    build_adaptive_team
)


from ml.prediction.predict_team_success import (
    load_model,
    predict_team_success
)


# ============================================================
# ASSIGNMENT ENGINE
# ============================================================

class AssignmentEngine:


    # ========================================================
    # INITIALIZE ENGINE
    # ========================================================

    def __init__(self):

        print(
            "\nInitializing Assignment Engine..."
        )


        # ----------------------------------------------------
        # LOAD EMPLOYEE DATA ONCE
        # ----------------------------------------------------

        print(
            "Loading employee data..."
        )


        self.employees_df = (
            load_employee_profiles()
        )


        print(
            f"Employees loaded: "
            f"{len(self.employees_df)}"
        )


        # ----------------------------------------------------
        # LOAD SKILL DATA ONCE
        # ----------------------------------------------------

        print(
            "Loading skill data..."
        )


        (
            self.task_skills_df,
            self.employee_skills_df
        ) = load_skill_data()


        print(
            f"Task skill records: "
            f"{len(self.task_skills_df)}"
        )


        print(
            f"Employee skill records: "
            f"{len(self.employee_skills_df)}"
        )


        # ----------------------------------------------------
        # LOAD MODEL ONCE
        # ----------------------------------------------------

        print(
            "Loading XGBoost model..."
        )


        self.model = (
            load_model()
        )


        print(
            "Assignment Engine ready!"
        )


    # ========================================================
    # ASSIGN TEAM
    # ========================================================

    def assign_team(
        self,
        task
    ):


        # ----------------------------------------------------
        # TASK ID
        # ----------------------------------------------------

        task_id = task.get(
            "task_id",
            "UNKNOWN"
        )


        print(
            f"\nAssigning team for: "
            f"{task_id}"
        )


        # ----------------------------------------------------
        # BUILD TEAM
        # ----------------------------------------------------

        result = (

            build_adaptive_team(

                employees_df=
                self.employees_df,

                task=
                task,

                task_skills_df=
                self.task_skills_df,

                employee_skills_df=
                self.employee_skills_df
            )

        )


        # ----------------------------------------------------
        # CHECK IF VALID TEAM WAS FOUND
        # ----------------------------------------------------

        if not result.get(
            "valid",
            False
        ):

            return {

                "task_id":
                task_id,

                "status":
                "failed",

                "message":
                (
                    "No valid team found "
                    "with complete skill coverage."
                )
            }


        # ----------------------------------------------------
        # EXTRACT TEAM
        # ----------------------------------------------------

        team = (

            result[
                "team"
            ]

        )


        # ----------------------------------------------------
        # EXTRACT SKILL COVERAGE
        # ----------------------------------------------------

        coverage = (

            result[
                "skill_coverage"
            ]

        )


        # ----------------------------------------------------
        # PREDICT TEAM SUCCESS
        # ----------------------------------------------------
        #
        # predict_team_success() RETURNS A DICTIONARY:
        #
        # {
        #     "success_probability": ...,
        #     "team_features": ...,
        #     "model_input": ...
        # }
        #
        # ----------------------------------------------------

        prediction_result = (

            predict_team_success(

                task=
                task,

                team=
                team,

                team_coverage=
                coverage,

                model=
                self.model
            )

        )


        # ----------------------------------------------------
        # EXTRACT SUCCESS PROBABILITY
        # ----------------------------------------------------

        success_probability = (

            prediction_result[
                "success_probability"
            ]

        )


        # ----------------------------------------------------
        # SELECT TEAM COLUMNS
        # ----------------------------------------------------

        team_columns = [

            "employee_id",

            "job_title",

            "candidate_score",

            "skill_match_pct",

            "critical_skill_match_pct",

            "skill_level_match_pct",

            "current_workload_pct",

            "availability_pct",

            "reliability_score"
        ]


        # ----------------------------------------------------
        # KEEP ONLY AVAILABLE COLUMNS
        # ----------------------------------------------------

        available_columns = [

            column

            for column in team_columns

            if column in team.columns
        ]


        # ----------------------------------------------------
        # CONVERT TEAM DATA TO JSON-READY FORMAT
        # ----------------------------------------------------

        team_data = (

            team[
                available_columns
            ]

            .to_dict(
                orient="records"
            )

        )


        # ----------------------------------------------------
        # RETURN FINAL RESULT
        # ----------------------------------------------------

        return {


            # ------------------------------------------------
            # TASK INFORMATION
            # ------------------------------------------------

            "task_id":
            task_id,


            "status":
            "success",


            # ------------------------------------------------
            # TEAM
            # ------------------------------------------------

            "team":
            team_data,


            "team_size":
            len(
                team
            ),


            # ------------------------------------------------
            # TEAM SCORE
            # ------------------------------------------------

            "team_score":
            round(

                float(

                    result.get(
                        "team_score",
                        0
                    )

                ),

                2
            ),


            # ------------------------------------------------
            # CANDIDATE POOL
            # ------------------------------------------------

            "candidate_pool_used":
            result.get(
                "candidate_pool_size",
                None
            ),


            # ------------------------------------------------
            # SKILL COVERAGE
            # ------------------------------------------------

            "skill_coverage":
            round(

                float(

                    coverage.get(
                        "skill_coverage_pct",
                        0
                    )

                ),

                2
            ),


            # ------------------------------------------------
            # CRITICAL SKILL COVERAGE
            # ------------------------------------------------

            "critical_skill_coverage":
            round(

                float(

                    coverage.get(
                        "critical_skill_coverage_pct",
                        0
                    )

                ),

                2
            ),


            # ------------------------------------------------
            # SUCCESS PROBABILITY
            # ------------------------------------------------

            "success_probability":
            float(
                success_probability
            )
        }


# ============================================================
# SINGLE ENGINE INSTANCE
# ============================================================

_engine = None


# ============================================================
# GET ASSIGNMENT ENGINE
# ============================================================

def get_assignment_engine():

    global _engine


    # --------------------------------------------------------
    # CREATE ENGINE ONLY ONCE
    # --------------------------------------------------------

    if _engine is None:

        _engine = (

            AssignmentEngine()

        )


    return _engine