from sqlalchemy import Column, String, Float, ForeignKey

from app.db.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id = Column(
        String(100),
        primary_key=True,
        index=True
    )

    employee_id = Column(
        String(100),
        ForeignKey("employees.employee_id"),
        nullable=False,
        index=True
    )

    task_id = Column(
        String(100),
        ForeignKey("tasks.task_id"),
        nullable=False,
        index=True
    )

    project_id = Column(
        String(100),
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True
    )

    success_probability = Column(
        Float,
        nullable=True
    )

    status = Column(
        String(100),
        nullable=True
    )