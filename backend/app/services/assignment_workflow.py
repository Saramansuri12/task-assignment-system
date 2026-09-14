from sqlalchemy.orm import Session

from app.db.models import Assignment, Task

from app.services.id_service import generate_id

from app.services.assignment_validator import (
    AssignmentValidator,
)

from app.services.assignment_history_service import (
    AssignmentHistoryService,
)


class AssignmentWorkflow:

    def __init__(self, db: Session):

        self.db = db

        self.validator = AssignmentValidator(db)

        self.history_service = AssignmentHistoryService(db)

    # =========================================================
    # CREATE PENDING ASSIGNMENT
    # =========================================================

    def create_pending(
        self,
        task_id: str,
        employee_id: str,
    ):

        validation = (
            self.validator.validate_assignment(
                task_id=task_id,
                employee_id=employee_id,
            )
        )

        if not validation["valid"]:

            return {
                "success": False,
                "errors": validation["errors"],
            }

        task = (
            self.db.query(Task)
            .filter(Task.task_id == task_id)
            .first()
        )

        assignment = Assignment(
            assignment_id=generate_id(
                self.db,
                Assignment,
                Assignment.assignment_id,
                prefix="ASN",
            ),
            task_id=task_id,
            employee_id=employee_id,
            project_id=task.project_id if task else None,
            status="PENDING",
        )

        self.db.add(assignment)

        try:

            # Flush first so assignment_id is available
            self.db.flush()

            # Record creation in history
            self.history_service.record(
                assignment_id=assignment.assignment_id,
                old_status=None,
                new_status="PENDING",
                changed_by="system",
                reason="Assignment recommendation created",
            )

            self.db.commit()
            self.db.refresh(assignment)

        except Exception:

            self.db.rollback()

            raise

        return {
            "success": True,
            "assignment": assignment,
        }

    # =========================================================
    # APPROVE
    # =========================================================

    def approve(
        self,
        assignment_id: str,
    ):

        assignment = (
            self.db.query(Assignment)
            .filter(
                Assignment.assignment_id ==
                assignment_id
            )
            .first()
        )

        if not assignment:

            return {
                "success": False,
                "error": "Assignment not found",
            }

        if assignment.status != "PENDING":

            return {
                "success": False,
                "error": (
                    "Only PENDING assignments "
                    "can be approved"
                ),
            }

        # Revalidate immediately before approval.
        # Capacity may have changed since recommendation.

        validation = (
            self.validator.validate_assignment(
                task_id=assignment.task_id,
                employee_id=assignment.employee_id,
            )
        )

        if not validation["valid"]:

            return {
                "success": False,
                "error": "Assignment is no longer valid",
                "validation_errors":
                    validation["errors"],
            }

        # Store old status before changing it
        old_status = assignment.status

        assignment.status = "ACTIVE"

        # Record status change
        self.history_service.record(
            assignment_id=assignment.assignment_id,
            old_status=old_status,
            new_status="ACTIVE",
            changed_by="manager",
            reason="Assignment approved",
        )

        try:

            self.db.commit()
            self.db.refresh(assignment)

        except Exception:

            self.db.rollback()

            raise

        return {
            "success": True,
            "assignment": assignment,
        }

    # =========================================================
    # REJECT
    # =========================================================

    def reject(
        self,
        assignment_id: str,
    ):

        assignment = (
            self.db.query(Assignment)
            .filter(
                Assignment.assignment_id ==
                assignment_id
            )
            .first()
        )

        if not assignment:

            return {
                "success": False,
                "error": "Assignment not found",
            }

        if assignment.status != "PENDING":

            return {
                "success": False,
                "error": (
                    "Only PENDING assignments "
                    "can be rejected"
                ),
            }

        # Store old status before changing it
        old_status = assignment.status

        assignment.status = "REJECTED"

        # Record status change
        self.history_service.record(
            assignment_id=assignment.assignment_id,
            old_status=old_status,
            new_status="REJECTED",
            changed_by="manager",
            reason="Assignment rejected",
        )

        try:

            self.db.commit()
            self.db.refresh(assignment)

        except Exception:

            self.db.rollback()

            raise

        return {
            "success": True,
            "assignment": assignment,
        }

    # =========================================================
    # COMPLETE
    # =========================================================

    def complete(
        self,
        assignment_id: str,
    ):

        assignment = (
            self.db.query(Assignment)
            .filter(
                Assignment.assignment_id ==
                assignment_id
            )
            .first()
        )

        if not assignment:

            return {
                "success": False,
                "error": "Assignment not found",
            }

        if assignment.status != "ACTIVE":

            return {
                "success": False,
                "error": (
                    "Only ACTIVE assignments "
                    "can be completed"
                ),
            }

        # Store old status before changing it
        old_status = assignment.status

        assignment.status = "COMPLETED"

        # Record status change
        self.history_service.record(
            assignment_id=assignment.assignment_id,
            old_status=old_status,
            new_status="COMPLETED",
            changed_by="system",
            reason="Assignment completed",
        )

        try:

            self.db.commit()
            self.db.refresh(assignment)

        except Exception:

            self.db.rollback()

            raise

        return {
            "success": True,
            "assignment": assignment,
        }

    # =========================================================
    # CANCEL
    # =========================================================

    def cancel(
        self,
        assignment_id: str,
    ):

        assignment = (
            self.db.query(Assignment)
            .filter(
                Assignment.assignment_id ==
                assignment_id
            )
            .first()
        )

        if not assignment:

            return {
                "success": False,
                "error": "Assignment not found",
            }

        if assignment.status not in (
            "PENDING",
            "ACTIVE",
        ):

            return {
                "success": False,
                "error": (
                    "This assignment cannot "
                    "be cancelled"
                ),
            }

        # Store old status before changing it
        old_status = assignment.status

        assignment.status = "CANCELLED"

        # Record status change
        self.history_service.record(
            assignment_id=assignment.assignment_id,
            old_status=old_status,
            new_status="CANCELLED",
            changed_by="manager",
            reason="Assignment cancelled",
        )

        try:

            self.db.commit()
            self.db.refresh(assignment)

        except Exception:

            self.db.rollback()

            raise

        return {
            "success": True,
            "assignment": assignment,
        }