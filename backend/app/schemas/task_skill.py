from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskSkillCreate(BaseModel):

    task_id: str
    skill_id: str

    required_level: Optional[float] = Field(
        default=None,
        ge=0
    )

    is_critical: Optional[bool] = None


class TaskSkillResponse(TaskSkillCreate):

    model_config = ConfigDict(from_attributes=True)
