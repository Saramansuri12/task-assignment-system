from typing import Optional

from pydantic import BaseModel, ConfigDict


class SkillCreate(BaseModel):
    # skills.skill_id is the primary key. Generated when omitted.
    skill_id: Optional[str] = None

    skill_name: str
    description: Optional[str] = None


class SkillUpdate(BaseModel):
    skill_name: Optional[str] = None
    description: Optional[str] = None


class SkillResponse(BaseModel):
    skill_id: str
    skill_name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)