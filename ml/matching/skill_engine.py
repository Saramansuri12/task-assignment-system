from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TASK_SKILLS_PATH = (
    BASE_DIR / "data" / "raw" / "task_required_skills.csv"
)

EMPLOYEE_SKILLS_PATH = (
    BASE_DIR / "data" / "raw" / "employee_skill_profiles.csv"
)


# ============================================================
# LOAD SKILL DATA
# ============================================================

def load_skill_data():
    """
    Load task skill requirements and employee skill profiles.
    """

    task_skills = pd.read_csv(
        TASK_SKILLS_PATH,
        encoding="utf-8"
    )

    employee_skills = pd.read_csv(
        EMPLOYEE_SKILLS_PATH,
        encoding="latin1"
    )

    return task_skills, employee_skills


# ============================================================
# TASK SKILL REQUIREMENTS
# ============================================================

def get_task_skill_requirements(
    task_id,
    task_skills_df
):
    """
    Return all skill requirements for a task.
    """

    task_skills = task_skills_df[
        task_skills_df["task_id"] == task_id
    ].copy()

    return task_skills


# ============================================================
# EMPLOYEE SKILL PROFILE
# ============================================================

def get_employee_skill_profile(
    employee_id,
    employee_skills_df
):
    """
    Return all skills possessed by an employee.
    """

    employee_skills = employee_skills_df[
        employee_skills_df["employee_id"] == employee_id
    ].copy()

    return employee_skills


# ============================================================
# INDIVIDUAL SKILL COVERAGE
# ============================================================

def calculate_skill_coverage(
    employee_id,
    task_id,
    task_skills_df,
    employee_skills_df
):
    """
    Calculate how well an employee covers
    the skills required by a task.
    """

    required = get_task_skill_requirements(
        task_id,
        task_skills_df
    )

    employee = get_employee_skill_profile(
        employee_id,
        employee_skills_df
    )

    # --------------------------------------------------------
    # No requirements
    # --------------------------------------------------------

    if required.empty:
        return {
            "skill_match_pct": 100.0,
            "critical_skill_match_pct": 100.0,
            "skill_level_match_pct": 100.0,
            "total_required_skills": 0,
            "total_critical_skills": 0,
            "matched_skills": [],
            "missing_skills": [],
            "missing_critical_skills": []
        }

    # --------------------------------------------------------
    # Employee skill lookup
    # --------------------------------------------------------

    employee_skill_levels = dict(
        zip(
            employee["skill_id"],
            employee["skill_level"]
        )
    )

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    total_required = len(required)

    total_critical = int(
        required["is_critical"].sum()
    )

    matched_skills = []
    missing_skills = []
    missing_critical_skills = []

    level_matched = 0

    critical_matched = 0

    # --------------------------------------------------------
    # Evaluate every required skill
    # --------------------------------------------------------

    for _, row in required.iterrows():

        skill_id = row["skill_id"]
        skill_name = row["skill_name"]

        required_level = float(
            row["required_level"]
        )

        is_critical = bool(
            row["is_critical"]
        )

        employee_level = employee_skill_levels.get(
            skill_id
        )

        # ----------------------------------------------------
        # Employee has skill
        # ----------------------------------------------------

        if employee_level is not None:

            employee_level = float(employee_level)

            matched_skills.append({
                "skill_id": skill_id,
                "skill_name": skill_name,
                "required_level": required_level,
                "employee_level": employee_level,
                "level_match": employee_level >= required_level,
                "is_critical": is_critical
            })

            # Skill exists
            if employee_level >= required_level:
                level_matched += 1

                if is_critical:
                    critical_matched += 1

        # ----------------------------------------------------
        # Employee does not have skill
        # ----------------------------------------------------

        else:

            missing_skills.append({
                "skill_id": skill_id,
                "skill_name": skill_name,
                "required_level": required_level,
                "is_critical": is_critical
            })

            if is_critical:
                missing_critical_skills.append({
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "required_level": required_level
                })

    # --------------------------------------------------------
    # Percentages
    # --------------------------------------------------------

    skill_match_pct = (
        len(matched_skills)
        / total_required
        * 100
    )

    skill_level_match_pct = (
        level_matched
        / total_required
        * 100
    )

    if total_critical > 0:

        critical_skill_match_pct = (
            critical_matched
            / total_critical
            * 100
        )

    else:

        critical_skill_match_pct = 100.0

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "skill_match_pct": round(
            skill_match_pct,
            2
        ),

        "critical_skill_match_pct": round(
            critical_skill_match_pct,
            2
        ),

        "skill_level_match_pct": round(
            skill_level_match_pct,
            2
        ),

        "total_required_skills": total_required,

        "total_critical_skills": total_critical,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "missing_critical_skills":
            missing_critical_skills
    }


# ============================================================
# TEAM SKILL COVERAGE
# ============================================================

def calculate_team_skill_coverage(
    employee_ids,
    task_id,
    task_skills_df,
    employee_skills_df
):
    """
    Calculate collective skill coverage for a team.

    A skill is considered covered when at least one
    team member possesses it at the required level.
    """

    required = get_task_skill_requirements(
        task_id,
        task_skills_df
    )

    team = employee_skills_df[
        employee_skills_df["employee_id"].isin(
            employee_ids
        )
    ]

    if required.empty:
        return {
            "skill_coverage_pct": 100.0,
            "critical_skill_coverage_pct": 100.0,
            "skill_level_coverage_pct": 100.0,
            "missing_skills": [],
            "missing_critical_skills": []
        }

    # --------------------------------------------------------
    # Build team skill lookup
    # --------------------------------------------------------

    team_skill_levels = {}

    for _, row in team.iterrows():

        skill_id = row["skill_id"]
        skill_level = float(row["skill_level"])

        if (
            skill_id not in team_skill_levels
            or skill_level > team_skill_levels[skill_id]
        ):
            team_skill_levels[skill_id] = skill_level

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    total_required = len(required)

    total_critical = int(
        required["is_critical"].sum()
    )

    skills_covered = 0
    critical_covered = 0
    level_covered = 0

    missing_skills = []
    missing_critical_skills = []

    # --------------------------------------------------------
    # Evaluate required skills
    # --------------------------------------------------------

    for _, row in required.iterrows():

        skill_id = row["skill_id"]
        skill_name = row["skill_name"]

        required_level = float(
            row["required_level"]
        )

        is_critical = bool(
            row["is_critical"]
        )

        team_level = team_skill_levels.get(
            skill_id
        )

        # ----------------------------------------------------
        # Skill exists in team
        # ----------------------------------------------------

        if team_level is not None:

            skills_covered += 1

            if team_level >= required_level:

                level_covered += 1

                if is_critical:
                    critical_covered += 1

            elif is_critical:

                missing_critical_skills.append({
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "required_level": required_level,
                    "best_team_level": team_level
                })

        # ----------------------------------------------------
        # Skill completely missing
        # ----------------------------------------------------

        else:

            missing_skills.append({
                "skill_id": skill_id,
                "skill_name": skill_name,
                "required_level": required_level,
                "is_critical": is_critical
            })

            if is_critical:

                missing_critical_skills.append({
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "required_level": required_level
                })

    # --------------------------------------------------------
    # Percentages
    # --------------------------------------------------------

    skill_coverage_pct = (
        skills_covered
        / total_required
        * 100
    )

    skill_level_coverage_pct = (
        level_covered
        / total_required
        * 100
    )

    if total_critical > 0:

        critical_skill_coverage_pct = (
            critical_covered
            / total_critical
            * 100
        )

    else:

        critical_skill_coverage_pct = 100.0

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "skill_coverage_pct": round(
            skill_coverage_pct,
            2
        ),

        "critical_skill_coverage_pct": round(
            critical_skill_coverage_pct,
            2
        ),

        "skill_level_coverage_pct": round(
            skill_level_coverage_pct,
            2
        ),

        "missing_skills": missing_skills,

        "missing_critical_skills":
            missing_critical_skills
    }