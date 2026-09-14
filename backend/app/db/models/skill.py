from sqlalchemy import Column, String, Text
from app.db.database import Base


class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(
        String(200),
        primary_key=True,
        index=True
    )

    skill_name = Column(
        String(300),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )