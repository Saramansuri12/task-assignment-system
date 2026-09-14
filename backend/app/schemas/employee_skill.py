from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class EmployeeSkillCreate(BaseModel):

    employee_id: str
    skill_id: str

    skill_level: float = Field(
        ge=1,
        le=5
    )


class EmployeeSkillResponse(BaseModel):

    employee_id: str
    skill_id: str
    skill_level: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)