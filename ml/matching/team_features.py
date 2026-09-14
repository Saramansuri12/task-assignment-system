import pandas as pd


# ============================================================
# BUILD TEAM FEATURES
# ============================================================

def build_team_features(
    team
):
    """
    Convert selected team members into
    aggregated features that can be used
    by the trained XGBoost model.
    """

    if team.empty:

        raise ValueError(
            "Cannot build features from an empty team."
        )


    # ========================================================
    # AVERAGE EMPLOYEE METRICS
    # ========================================================

    performance_score = (
        team[
            "performance_score"
        ]
        .mean()
    )


    current_workload_pct = (
        team[
            "current_workload_pct"
        ]
        .mean()
    )


    availability_pct = (
        team[
            "availability_pct"
        ]
        .mean()
    )


    reliability_score = (
        team[
            "reliability_score"
        ]
        .mean()
    )


    collaboration_score = (
        team[
            "collaboration_score"
        ]
        .mean()
    )


    # ========================================================
    # CRITICAL PROJECT EXPERIENCE
    # ========================================================

    critical_project_experience = (
        team[
            "critical_project_experience"
        ]
        .mean()
    )


    # ========================================================
    # SKILL MATCH FEATURES
    # ========================================================

    skill_match_pct = (
        team[
            "skill_match_pct"
        ]
        .mean()
    )


    critical_skill_match_pct = (
        team[
            "critical_skill_match_pct"
        ]
        .mean()
    )


    skill_level_match_pct = (
        team[
            "skill_level_match_pct"
        ]
        .mean()
    )


    # ========================================================
    # RETURN FEATURES
    # ========================================================

    return {

        "skill_match_pct":
        round(
            float(skill_match_pct),
            2
        ),

        "critical_skill_match_pct":
        round(
            float(
                critical_skill_match_pct
            ),
            2
        ),

        "skill_level_match_pct":
        round(
            float(
                skill_level_match_pct
            ),
            2
        ),

        "performance_score":
        round(
            float(
                performance_score
            ),
            2
        ),

        "current_workload_pct":
        round(
            float(
                current_workload_pct
            ),
            2
        ),

        "availability_pct":
        round(
            float(
                availability_pct
            ),
            2
        ),

        "reliability_score":
        round(
            float(
                reliability_score
            ),
            2
        ),

        "collaboration_score":
        round(
            float(
                collaboration_score
            ),
            2
        ),

        "critical_project_experience":
        round(
            float(
                critical_project_experience
            ),
            2
        )
    }