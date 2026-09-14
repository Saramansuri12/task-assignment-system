from sqlalchemy import Column, Date, String
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String(100), primary_key=True, index=True)
    project_name = Column(String(200), nullable=True)

    project_domain = Column(String(200), nullable=True)
    project_type = Column(String(200), nullable=True)

    project_complexity = Column(String(50), nullable=True)
    project_criticality = Column(String(50), nullable=True)

    priority = Column(String(50), nullable=True)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)