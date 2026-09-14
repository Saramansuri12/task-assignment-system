from typing import List, Optional
from pydantic import BaseModel


class TeamMemberRecommendation(BaseModel):
    employee_id: str
    name: Optional[str] = None

    skill_match: float
    workload_score: float
    experience_score: float
    performance_score: float
    final_score: float

    contribution_score: float
    matched_skills: List[str] = []


class TeamRecommendationResponse(BaseModel):
    task_id: str
    required_team_size: int

    team: List[TeamMemberRecommendation]

    skill_coverage: float
    covered_skills: List[str]
    uncovered_skills: List[str]
    uncovered_critical_skills: List[str]

    team_valid: bool
    recommendation_reason: str