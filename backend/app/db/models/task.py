from sqlalchemy import Column, String, Float, Integer, ForeignKey, Date
from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(String(100), primary_key=True, index=True)

    project_id = Column(
        String(100),
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True
    )

    task_title = Column(String(500), nullable=True)
    task_description = Column(String(2000), nullable=True)

    project_complexity = Column(String(50), nullable=True)
    project_criticality = Column(String(50), nullable=True)

    role_required = Column(String(200), nullable=True)

    team_size_required = Column(Integer, nullable=True)

    estimated_hours = Column(Float, nullable=True)

    deadline_days = Column(Integer, nullable=True)

    priority = Column(String(50), nullable=True)

    required_experience_years = Column(Float, nullable=True)

    task_start_date = Column(Date, nullable=True)
    task_due_date = Column(Date, nullable=True)

    assigned_count = Column(Integer, nullable=True)