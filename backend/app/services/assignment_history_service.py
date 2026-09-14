from sqlalchemy.orm import Session

from app.db.models import AssignmentHistory


class AssignmentHistoryService:

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # RECORD STATUS CHANGE
    # =========================================================

    def record(
        self,
        assignment_id,
        old_status,
        new_status,
        changed_by=None,
        reason=None,
    ):

        history = AssignmentHistory(
            assignment_id=assignment_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason,
        )

        self.db.add(history)

        return history

    # =========================================================
    # GET HISTORY
    # =========================================================

    def get_history(
        self,
        assignment_id,
    ):

        return (
            self.db.query(AssignmentHistory)
            .filter(
                AssignmentHistory.assignment_id
                == assignment_id
            )
            .order_by(
                AssignmentHistory.changed_at.asc()
            )
            .all()
        )