from sqlalchemy.orm import Session

from app.db.models import Employee, Assignment, Task


class WorkloadService:

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # GET EMPLOYEE
    # =========================================================

    def get_employee(self, employee_id: str):

        return (
            self.db.query(Employee)
            .filter(
                Employee.employee_id == employee_id
            )
            .first()
        )

    # =========================================================
    # GET ACTIVE ASSIGNMENTS
    # =========================================================

    def get_active_assignments(
        self,
        employee_id: str
    ):

        return (
            self.db.query(Assignment)
            .filter(
                Assignment.employee_id == employee_id,
                Assignment.status == "ACTIVE"
            )
            .all()
        )

    # =========================================================
    # GET TASK HOURS
    # =========================================================

    def get_task_hours(self, task):

        # We support several possible column names
        # so the service remains compatible with
        # different versions of the Task model.

        possible_fields = [
            "estimated_hours",
            "effort_hours",
            "task_hours",
            "duration_hours",
        ]

        for field in possible_fields:

            if hasattr(task, field):

                value = getattr(task, field)

                if value is not None:

                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        pass

        # If no effort field exists yet,
        # return zero instead of inventing effort.

        return 0.0

    # =========================================================
    # CALCULATE ASSIGNED HOURS
    # =========================================================

    def calculate_assigned_hours(
        self,
        employee_id: str
    ):

        assignments = self.get_active_assignments(
            employee_id
        )

        total_hours = 0.0

        for assignment in assignments:

            task = (
                self.db.query(Task)
                .filter(
                    Task.task_id ==
                    assignment.task_id
                )
                .first()
            )

            if task:

                total_hours += self.get_task_hours(
                    task
                )

        return total_hours

    # =========================================================
    # CALCULATE WORKLOAD
    # =========================================================

    def calculate_workload(
        self,
        employee_id: str
    ):

        employee = self.get_employee(
            employee_id
        )

        if not employee:
            return None

        assigned_hours = (
            self.calculate_assigned_hours(
                employee_id
            )
        )

        # -----------------------------------------------------
        # Read available capacity from employee record
        # -----------------------------------------------------

        availability = getattr(
            employee,
            "availability_pct",
            None
        )

        current_workload = getattr(
            employee,
            "current_workload_pct",
            None
        )

        try:
            availability = (
                float(availability)
                if availability is not None
                else 100.0
            )
        except (TypeError, ValueError):
            availability = 100.0

        try:
            current_workload = (
                float(current_workload)
                if current_workload is not None
                else 0.0
            )
        except (TypeError, ValueError):
            current_workload = 0.0

        # -----------------------------------------------------
        # Remaining capacity
        # -----------------------------------------------------

        remaining_capacity = max(
            0.0,
            availability - current_workload
        )

        return {
            "employee_id": str(
                employee.employee_id
            ),
            "assigned_hours": round(
                assigned_hours,
                2
            ),
            "availability_pct": round(
                availability,
                2
            ),
            "current_workload_pct": round(
                current_workload,
                2
            ),
            "remaining_capacity_pct": round(
                remaining_capacity,
                2
            ),
        }

    # =========================================================
    # CHECK WHETHER EMPLOYEE CAN TAKE TASK
    # =========================================================

    def can_accept_task(
        self,
        employee_id: str,
        task_id: str
    ):

        employee = self.get_employee(
            employee_id
        )

        if not employee:

            return {
                "allowed": False,
                "reason": "Employee not found"
            }

        task = (
            self.db.query(Task)
            .filter(
                Task.task_id == task_id
            )
            .first()
        )

        if not task:

            return {
                "allowed": False,
                "reason": "Task not found"
            }

        workload = self.calculate_workload(
            employee_id
        )

        if workload is None:

            return {
                "allowed": False,
                "reason": "Unable to calculate workload"
            }

        # -----------------------------------------------------
        # Employee unavailable
        # -----------------------------------------------------

        if workload["remaining_capacity_pct"] <= 0:

            return {
                "allowed": False,
                "reason": "Employee has no remaining capacity",
                "workload": workload
            }

        return {
            "allowed": True,
            "reason": None,
            "workload": workload
        }