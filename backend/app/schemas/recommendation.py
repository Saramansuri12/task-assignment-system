from typing import List

from pydantic import BaseModel, Field


# =========================================================
# RECOMMENDATION REQUEST
# =========================================================

class RecommendationRequest(BaseModel):
    task_id: str

    top_k: int = Field(
        default=5,
        ge=1,
        le=20
    )


# =========================================================
# EMPLOYEE RECOMMENDATION
# =========================================================

class EmployeeRecommendation(BaseModel):
    employee_id: str
    employee_name: str | None = None

    match_score: float

    skill_match: float
    experience_match: float
    availability_score: float
    reliability_score: float

    reason: str
    scoring_method: str


# =========================================================
# RECOMMENDATION RESPONSE
# =========================================================

class RecommendationResponse(BaseModel):
    task_id: str
    recommendations: List[EmployeeRecommendation]