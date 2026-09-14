from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# =========================================================
# REQUIRED SKILL
# =========================================================

class RequiredSkill(BaseModel):
    skill_id: str
    required_level: float = 0


# =========================================================
# ASSIGNMENT RECOMMENDATION REQUEST
# =========================================================

class AssignmentRecommendationRequest(BaseModel):

    required_skills: List[RequiredSkill] = Field(
        default_factory=list
    )

    required_experience: float = 0

    top_k: int = Field(
        default=10,
        ge=1,
        le=50
    )


# =========================================================
# EMPLOYEE RECOMMENDATION
# =========================================================

class EmployeeRecommendation(BaseModel):

    employee_id: str
    name: Optional[str] = None

    skill_match: float
    workload_score: float
    experience_score: float
    performance_score: float

    final_score: float


# =========================================================
# ASSIGNMENT RECOMMENDATION RESPONSE
# =========================================================

class AssignmentRecommendationResponse(BaseModel):

    total_candidates: int

    recommendations: List[
        EmployeeRecommendation
    ]


# =========================================================
# CREATE ASSIGNMENT
# =========================================================

class AssignmentCreate(BaseModel):

    task_id: str
    employee_id: str


# =========================================================
# UPDATE ASSIGNMENT STATUS
# =========================================================

class AssignmentStatusUpdate(BaseModel):

    status: str


# =========================================================
# ASSIGNMENT RESPONSE
# =========================================================

class AssignmentResponse(BaseModel):

    # assignments.assignment_id is String(100), not an integer.
    assignment_id: str

    task_id: str
    employee_id: str
    project_id: Optional[str] = None

    status: Optional[str] = None

    # Written by the ML service when the assignment is created.
    success_probability: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)