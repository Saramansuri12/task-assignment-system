from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from app.db.database import Base


class TaskSkill(Base):
    __tablename__ = "task_skills"

    task_id = Column(
        String(100),
        ForeignKey("tasks.task_id"),
        primary_key=True
    )

    skill_id = Column(
        String(200),
        ForeignKey("skills.skill_id"),
        primary_key=True
    )

    required_level = Column(Float, nullable=True)

    is_critical = Column(Boolean, nullable=True)