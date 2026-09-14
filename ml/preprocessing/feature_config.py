TARGET = "project_success"


ID_COLUMNS = [
    "assignment_id",
    "project_id",
    "task_id",
    "employee_id",
]


LEAKAGE_COLUMNS = [
    "completion_status",
    "completion_time_hours",
    "delay_days",
    "quality_score",
    "manager_rating",
]


FEATURES = [
    # Project / Task
    "project_domain",
    "project_type",
    "project_complexity",
    "project_criticality",
    "role_required",

    "team_size_required",
    "estimated_hours",
    "deadline_days",
    "priority",

    # Matching features
    "skill_match_pct",
    "critical_skill_match_pct",
    "skill_level_match_pct",
    "experience_match_pct",
    "domain_match",
    "role_match",

    # Employee features
    "critical_project_experience",
    "performance_score",
    "current_workload_pct",
    "availability_pct",
    "reliability_score",
    "collaboration_score",
]