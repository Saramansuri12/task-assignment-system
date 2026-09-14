from sqlalchemy import (
    Column,
    String,
    Float,
    ForeignKey,
)

from app.db.database import Base


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    employee_id = Column(
        String(100),
        ForeignKey("employees.employee_id"),
        primary_key=True
    )

    skill_id = Column(
        String(200),
        ForeignKey("skills.skill_id"),
        primary_key=True
    )

    skill_level = Column(
        "proficiency",
        Float,
        nullable=True
    )