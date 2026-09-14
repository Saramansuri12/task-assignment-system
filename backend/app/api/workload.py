from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.workload_services import (
    WorkloadService,
)


router = APIRouter(
    prefix="/workload",
    tags=["Workload"],
)


# =========================================================
# EMPLOYEE WORKLOAD
# =========================================================

@router.get(
    "/employee/{employee_id}"
)
def get_employee_workload(
    employee_id: str,
    db: Session = Depends(get_db),
):

    service = WorkloadService(db)

    result = service.calculate_workload(
        employee_id
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    return result


# =========================================================
# CHECK TASK CAPACITY
# =========================================================

@router.get(
    "/employee/{employee_id}/task/{task_id}"
)
def check_task_capacity(
    employee_id: str,
    task_id: str,
    db: Session = Depends(get_db),
):

    service = WorkloadService(db)

    result = service.can_accept_task(
        employee_id,
        task_id,
    )

    if (
        result.get("reason")
        == "Employee not found"
    ):

        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    if (
        result.get("reason")
        == "Task not found"
    ):

        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return result