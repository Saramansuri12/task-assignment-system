"""
DATABASE -> ML FEATURE ADAPTER
==============================

The trained model at ml/models/xgboost_assignment_model.pkl is a full
sklearn Pipeline:

    ColumnTransformer(SimpleImputer + OneHotEncoder) -> XGBClassifier

It expects a pandas DataFrame with EXACTLY these 21 raw columns
(order does not matter, names do - the ColumnTransformer selects by name):

    project_domain, project_type, project_complexity, project_criticality,
    role_required, team_size_required, estimated_hours, deadline_days,
    priority, skill_match_pct, critical_skill_match_pct,
    skill_level_match_pct, experience_match_pct, domain_match, role_match,
    critical_project_experience, performance_score, current_workload_pct,
    availability_pct, reliability_score, collaboration_score

This module converts SQLAlchemy rows into that shape. It does NOT
re-implement preprocessing - the pipeline does its own imputation and
one-hot encoding, exactly as it did at training time.

The six matching features are computed with the ORIGINAL training-time
helpers in ml/matching/feature_matching.py, so production matches
training.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------
# Make the project-root `ml` package importable from the backend.
# backend/app/ml/feature_adapter.py -> parents[3] == project root
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from ml.matching.feature_matching import build_matching_features
    from ml.matching.eligibility import check_employee_eligibility

    ML_HELPERS_AVAILABLE = True

except Exception as exc:  # pragma: no cover
    print(f"[ML] Matching helpers unavailable: {exc}")

    build_matching_features = None
    check_employee_eligibility = None

    ML_HELPERS_AVAILABLE = False


# The exact column set the trained pipeline was fitted on.
MODEL_FEATURE_COLUMNS = [
    "project_domain",
    "project_type",
    "project_complexity",
    "project_criticality",
    "role_required",
    "team_size_required",
    "estimated_hours",
    "deadline_days",
    "priority",
    "skill_match_pct",
    "critical_skill_match_pct",
    "skill_level_match_pct",
    "experience_match_pct",
    "domain_match",
    "role_match",
    "critical_project_experience",
    "performance_score",
    "current_workload_pct",
    "availability_pct",
    "reliability_score",
    "collaboration_score",
]


# =====================================================================
# TASK / PROJECT  ->  ML TASK DICT
# =====================================================================

def build_task_payload(
    task,
    project,
    task_skill_rows: List[Any],
) -> Dict[str, Any]:
    """
    task             : app.db.models.Task
    project          : app.db.models.Project or None
    task_skill_rows  : list of (TaskSkill, Skill) tuples
    """

    required_skills = []
    critical_skills = []
    required_levels = []

    for task_skill, skill in task_skill_rows:

        skill_name = (
            skill.skill_name
            if skill is not None and skill.skill_name
            else str(task_skill.skill_id)
        )

        required_skills.append(skill_name)

        if task_skill.required_level is not None:
            required_levels.append(float(task_skill.required_level))

        if task_skill.is_critical:
            critical_skills.append(skill_name)

    average_required_level = (
        sum(required_levels) / len(required_levels)
        if required_levels
        else 0
    )

    # Task-level values win; fall back to the parent project.
    def pick(task_value, project_value):
        return task_value if task_value not in (None, "") else project_value

    return {
        # Raw model features
        "project_domain": (
            project.project_domain if project is not None else None
        ),
        "project_type": (
            project.project_type if project is not None else None
        ),
        "project_complexity": pick(
            task.project_complexity,
            project.project_complexity if project is not None else None,
        ),
        "project_criticality": pick(
            task.project_criticality,
            project.project_criticality if project is not None else None,
        ),
        "role_required": task.role_required,
        "team_size_required": task.team_size_required,
        "estimated_hours": task.estimated_hours,
        "deadline_days": task.deadline_days,
        "priority": pick(
            task.priority,
            project.priority if project is not None else None,
        ),

        # Inputs for the matching-feature helpers
        "required_skills": required_skills,
        "critical_skills": critical_skills,
        "required_experience": float(
            task.required_experience_years or 0
        ),
        "required_skill_level": average_required_level,
    }


# =====================================================================
# EMPLOYEE  ->  ML EMPLOYEE DICT
# =====================================================================

def build_employee_payload(
    employee,
    employee_skill_rows: List[Any],
    domains: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    employee            : app.db.models.Employee
    employee_skill_rows : list of (EmployeeSkill, Skill) tuples
    domains             : project domains the employee has worked in
    """

    skill_names = []
    skill_levels = []

    for employee_skill, skill in employee_skill_rows:

        skill_name = (
            skill.skill_name
            if skill is not None and skill.skill_name
            else str(employee_skill.skill_id)
        )

        skill_names.append(skill_name)

        if employee_skill.skill_level is not None:
            skill_levels.append(float(employee_skill.skill_level))

    average_skill_level = (
        sum(skill_levels) / len(skill_levels)
        if skill_levels
        else 0
    )

    return {
        "employee_id": str(employee.employee_id),
        "name": employee.name,
        "role": employee.role,

        "skills": skill_names,
        "skill_level": average_skill_level,
        "domains": domains or [],

        "years_experience": float(
            employee.years_experience or 0
        ),
        "critical_project_experience": (
            employee.critical_project_experience
            if employee.critical_project_experience is not None
            else 0
        ),
        "performance_score": employee.performance_score,
        "current_workload_pct": employee.current_workload_pct,
        "availability_pct": employee.availability_pct,

        # Not present in the current schema. Left as None on purpose so
        # the pipeline's SimpleImputer fills them with the training
        # median instead of us inventing a value.
        "reliability_score": getattr(
            employee, "reliability_score", None
        ),
        "collaboration_score": getattr(
            employee, "collaboration_score", None
        ),
    }


# =====================================================================
# BUILD ONE MODEL INPUT ROW
# =====================================================================

def build_feature_row(
    employee_payload: Dict[str, Any],
    task_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Produce a single dict with exactly MODEL_FEATURE_COLUMNS as keys.
    """

    if ML_HELPERS_AVAILABLE:
        matching = build_matching_features(
            employee_payload,
            task_payload,
        )
    else:
        matching = {
            "skill_match_pct": 0.0,
            "critical_skill_match_pct": 0.0,
            "skill_level_match_pct": 0.0,
            "experience_match_pct": 0.0,
            "domain_match": 0,
            "role_match": 0,
        }

    row = {
        "project_domain": task_payload.get("project_domain"),
        "project_type": task_payload.get("project_type"),
        "project_complexity": task_payload.get("project_complexity"),
        "project_criticality": task_payload.get("project_criticality"),
        "role_required": task_payload.get("role_required"),
        "team_size_required": task_payload.get("team_size_required"),
        "estimated_hours": task_payload.get("estimated_hours"),
        "deadline_days": task_payload.get("deadline_days"),
        "priority": task_payload.get("priority"),

        "skill_match_pct": matching["skill_match_pct"],
        "critical_skill_match_pct": matching["critical_skill_match_pct"],
        "skill_level_match_pct": matching["skill_level_match_pct"],
        "experience_match_pct": matching["experience_match_pct"],
        "domain_match": matching["domain_match"],
        "role_match": matching["role_match"],

        "critical_project_experience":
            employee_payload.get("critical_project_experience"),
        "performance_score":
            employee_payload.get("performance_score"),
        "current_workload_pct":
            employee_payload.get("current_workload_pct"),
        "availability_pct":
            employee_payload.get("availability_pct"),
        "reliability_score":
            employee_payload.get("reliability_score"),
        "collaboration_score":
            employee_payload.get("collaboration_score"),
    }

    return row, matching


# =====================================================================
# ELIGIBILITY (reuses the original training-time rules)
# =====================================================================

def check_eligibility(
    employee_payload: Dict[str, Any],
    task_payload: Dict[str, Any],
    matching: Dict[str, Any],
) -> Dict[str, Any]:

    if not ML_HELPERS_AVAILABLE:
        return {"eligible": True, "reasons": []}

    return check_employee_eligibility(
        employee_payload,
        task_payload,
        {
            "skill_match_pct": matching["skill_match_pct"],
            "critical_skill_match_pct": matching["critical_skill_match_pct"],
            "role_match": matching["role_match"],
        },
    )
