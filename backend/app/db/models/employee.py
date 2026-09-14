from sqlalchemy import Column, String, Float, Integer
from app.db.database import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(
        String(100),
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=True
    )

    role = Column(
        String(200),
        nullable=True
    )

    seniority = Column(
        String(100),
        nullable=True
    )

    years_experience = Column(
        Float,
        nullable=True
    )

    performance_score = Column(
        Float,
        nullable=True
    )

    current_workload_pct = Column(
        Float,
        nullable=True
    )

    availability_pct = Column(
        Float,
        nullable=True
    )

    available_from = Column(
        String(100),
        nullable=True
    )

    critical_project_experience = Column(
        Integer,
        nullable=True
    )