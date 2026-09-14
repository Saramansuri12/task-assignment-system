from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.db.database import Base


class AssignmentHistory(Base):

    __tablename__ = "assignment_history"

    history_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    assignment_id = Column(
        String(100),
        ForeignKey(
            "assignments.assignment_id"
        ),
        nullable=False,
        index=True,
    )

    old_status = Column(
        String(30),
        nullable=True,
    )

    new_status = Column(
        String(30),
        nullable=False,
    )

    changed_by = Column(
        String(100),
        nullable=True,
    )

    reason = Column(
        Text,
        nullable=True,
    )

    changed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )