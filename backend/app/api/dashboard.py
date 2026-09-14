from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db

from app.db.models import (
    Employee,
    Task,
    Project,
    Assignment,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
):
    """
    Return summary statistics
    for the manager dashboard.
    """

    # =====================================================
    # TOTAL EMPLOYEES
    # =====================================================

    total_employees = (
        db.query(
            func.count(Employee.employee_id)
        )
        .scalar()
        or 0
    )

    # =====================================================
    # TOTAL TASKS
    # =====================================================

    total_tasks = (
        db.query(
            func.count(Task.task_id)
        )
        .scalar()
        or 0
    )

    # =====================================================
    # TOTAL PROJECTS
    # =====================================================

    total_projects = (
        db.query(
            func.count(Project.project_id)
        )
        .scalar()
        or 0
    )

    # =====================================================
    # TOTAL ASSIGNMENTS
    # =====================================================

    total_assignments = (
        db.query(
            func.count(Assignment.assignment_id)
        )
        .scalar()
        or 0
    )

    # =====================================================
    # ASSIGNMENT STATUS BREAKDOWN
    # =====================================================

    status_rows = (
        db.query(
            Assignment.status,
            func.count(
                Assignment.assignment_id
            ),
        )
        .group_by(
            Assignment.status
        )
        .all()
    )

    assignment_status = {}

    for status, count in status_rows:

        assignment_status[
            status or "Unknown"
        ] = count

    # =====================================================
    # ACTIVE ASSIGNMENTS
    # =====================================================

    active_assignments = (
        db.query(
            func.count(
                Assignment.assignment_id
            )
        )
        .filter(
            Assignment.status.in_(
                [
                    "ACTIVE",
                    "IN_PROGRESS",
                    "Assigned",
                    "In Progress",
                    "Active",
                ]
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # COMPLETED ASSIGNMENTS
    # =====================================================

    completed_assignments = (
        db.query(
            func.count(
                Assignment.assignment_id
            )
        )
        .filter(
            Assignment.status.in_(
                [
                    "COMPLETED",
                    "Completed",
                    "Completed On Time",
                    "Completed Early",
                    "Completed Late",
                ]
            )
        )
        .scalar()
        or 0
    )

    # =====================================================
    # SUCCESSFUL ASSIGNMENTS
    # =====================================================

    success_count = (
        db.query(
            func.count(
                Assignment.assignment_id
            )
        )
        .filter(
            Assignment.success_probability >= 0.5
        )
        .scalar()
        or 0
    )

    # =====================================================
    # SUCCESS RATE
    # =====================================================

    if total_assignments > 0:

        success_rate = round(
            (
                success_count
                / total_assignments
            )
            * 100,
            2,
        )

    else:

        success_rate = 0.0

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "employees": {
            "total": total_employees,
        },

        "tasks": {
            "total": total_tasks,
        },

        "projects": {
            "total": total_projects,
        },

        "assignments": {
            "total": total_assignments,
            "active": active_assignments,
            "completed": completed_assignments,
            "successful": success_count,
        },

        "success_rate": success_rate,

        "assignment_status": assignment_status,
    }