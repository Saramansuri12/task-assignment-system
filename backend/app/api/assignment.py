from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.db.models import (
    Assignment,
    Employee,
    Task,
)

from app.services.assignment_engine import AssignmentEngine
from app.services.ml_assignment_service import MLAssignmentService
from app.services.id_service import generate_id
from app.services.assignment_validator import AssignmentValidator
from app.services.assignment_workflow import AssignmentWorkflow
from app.services.assignment_history_service import (
    AssignmentHistoryService,
)

from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentStatusUpdate,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"],
)


# =========================================================
# 1. RECOMMEND EMPLOYEES FOR TASK
# =========================================================

@router.get("/task/{task_id}/recommend")
def recommend_for_task(
    task_id: str,
    top_k: int = 10,
    db: Session = Depends(get_db),
):
    if top_k < 1:
        raise HTTPException(
            status_code=400,
            detail="top_k must be at least 1",
        )

    if top_k > 50:
        raise HTTPException(
            status_code=400,
            detail="top_k cannot be greater than 50",
        )

    try:
        # Primary path: the trained XGBoost pipeline.
        service = MLAssignmentService(db)

        result = service.rank_employees_for_task(
            task_id=task_id,
            top_k=top_k,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        # Never leave the UI with nothing: fall back to the original
        # rule-based engine if the ML path fails at runtime.
        print(f"[ML] Falling back to rule-based engine: {exc}")

        try:
            fallback = AssignmentEngine(db).recommend_for_task(
                task_id=task_id,
                top_k=top_k,
            )

            if fallback is None:
                raise HTTPException(
                    status_code=404,
                    detail="Task not found",
                )

            fallback["scoring_method"] = "rule_based_fallback"
            fallback["model_available"] = False
            fallback["model_error"] = str(exc)

            return fallback

        except HTTPException:
            raise

        except Exception as inner:
            raise HTTPException(
                status_code=500,
                detail=f"Recommendation failed: {inner}",
            )


# =========================================================
# 2. RECOMMEND COMPLETE TEAM
# =========================================================

@router.get("/task/{task_id}/recommend-team")
def recommend_team(
    task_id: str,
    db: Session = Depends(get_db),
):
    try:
        service = MLAssignmentService(db)

        result = service.build_team_for_task(
            task_id=task_id,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        print(f"[ML] Team fallback to rule-based engine: {exc}")

        try:
            fallback = AssignmentEngine(db).build_team_for_task(
                task_id=task_id,
            )

            if fallback is None:
                raise HTTPException(
                    status_code=404,
                    detail="Task not found",
                )

            fallback["scoring_method"] = "rule_based_fallback"
            fallback["model_available"] = False

            return fallback

        except HTTPException:
            raise

        except Exception as inner:
            raise HTTPException(
                status_code=500,
                detail=f"Team recommendation failed: {inner}",
            )


# =========================================================
# 3. VALIDATE ASSIGNMENT
# =========================================================

@router.get(
    "/validate/{task_id}/{employee_id}",
)
def validate_assignment(
    task_id: str,
    employee_id: str,
    db: Session = Depends(get_db),
):
    validator = AssignmentValidator(db)

    try:
        return validator.validate_assignment(
            task_id=task_id,
            employee_id=employee_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Assignment validation failed: "
                f"{str(exc)}"
            ),
        )


# =========================================================
# 4. CREATE PENDING ASSIGNMENT
# =========================================================

@router.post(
    "/pending",
    status_code=201,
)
def create_pending_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
):
    workflow = AssignmentWorkflow(db)

    result = workflow.create_pending(
        task_id=assignment_data.task_id,
        employee_id=assignment_data.employee_id,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=409,
            detail=result,
        )

    return result


# =========================================================
# 5. CREATE ACTIVE ASSIGNMENT
# =========================================================

@router.post(
    "",
    response_model=AssignmentResponse,
    status_code=201,
)
@router.post(
    "/",
    response_model=AssignmentResponse,
    status_code=201,
    include_in_schema=False,
)
def create_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # Check task
    # -----------------------------------------------------

    task = (
        db.query(Task)
        .filter(
            Task.task_id == assignment_data.task_id
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    # -----------------------------------------------------
    # Check employee
    # -----------------------------------------------------

    employee = (
        db.query(Employee)
        .filter(
            Employee.employee_id
            == assignment_data.employee_id
        )
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    # -----------------------------------------------------
    # Check duplicate assignment
    # -----------------------------------------------------

    existing = (
        db.query(Assignment)
        .filter(
            Assignment.task_id
            == assignment_data.task_id,
            Assignment.employee_id
            == assignment_data.employee_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Employee is already assigned to this task",
        )

    # -----------------------------------------------------
    # Validate assignment
    # -----------------------------------------------------

    validator = AssignmentValidator(db)

    validation = validator.validate_assignment(
        task_id=assignment_data.task_id,
        employee_id=assignment_data.employee_id,
    )

    if not validation["valid"]:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Assignment rejected",
                "errors": validation.get(
                    "errors",
                    [],
                ),
            },
        )

    # -----------------------------------------------------
    # Create assignment
    # -----------------------------------------------------

    # assignments.assignment_id is a String primary key with no
    # default, and project_id is NOT NULL - both were previously
    # omitted, so every insert failed.
    success_probability = None

    try:
        success_probability = MLAssignmentService(db).score_pair(
            task_id=assignment_data.task_id,
            employee_id=assignment_data.employee_id,
        )

    except Exception as exc:
        print(f"[ML] Could not score assignment: {exc}")

    assignment = Assignment(
        assignment_id=generate_id(
            db,
            Assignment,
            Assignment.assignment_id,
            prefix="ASN",
        ),
        task_id=assignment_data.task_id,
        employee_id=assignment_data.employee_id,
        project_id=task.project_id,
        success_probability=success_probability,
        status="ACTIVE",
    )

    db.add(assignment)

    try:
        db.commit()
        db.refresh(assignment)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to create assignment: "
                f"{str(exc)}"
            ),
        )

    return assignment


# =========================================================
# 6. GET ALL ASSIGNMENTS
# =========================================================

@router.get(
    "",
    response_model=list[AssignmentResponse],
)
@router.get(
    "/",
    response_model=list[AssignmentResponse],
    include_in_schema=False,
)
def get_assignments(
    db: Session = Depends(get_db),
):
    assignments = (
        db.query(Assignment)
        .order_by(
            Assignment.assignment_id.desc()
        )
        .all()
    )

    return assignments


# =========================================================
# 7. GET ASSIGNMENTS FOR TASK
# =========================================================

@router.get(
    "/task/{task_id}",
    response_model=list[AssignmentResponse],
)
def get_task_assignments(
    task_id: str,
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # Check task
    # -----------------------------------------------------

    task = (
        db.query(Task)
        .filter(
            Task.task_id == task_id
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    # -----------------------------------------------------
    # Get assignments
    # -----------------------------------------------------

    assignments = (
        db.query(Assignment)
        .filter(
            Assignment.task_id == task_id
        )
        .order_by(
            Assignment.assignment_id.desc()
        )
        .all()
    )

    return assignments


# =========================================================
# 8. GET ASSIGNMENTS FOR EMPLOYEE
# =========================================================

@router.get(
    "/employee/{employee_id}",
    response_model=list[AssignmentResponse],
)
def get_employee_assignments(
    employee_id: str,
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # Check employee
    # -----------------------------------------------------

    employee = (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id
        )
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    # -----------------------------------------------------
    # Get assignments
    # -----------------------------------------------------

    assignments = (
        db.query(Assignment)
        .filter(
            Assignment.employee_id == employee_id
        )
        .order_by(
            Assignment.assignment_id.desc()
        )
        .all()
    )

    return assignments


# =========================================================
# 9. APPROVE ASSIGNMENT
# =========================================================

@router.post(
    "/{assignment_id}/approve",
)
def approve_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    workflow = AssignmentWorkflow(db)

    result = workflow.approve(
        assignment_id,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=409,
            detail=result,
        )

    return result


# =========================================================
# 10. REJECT ASSIGNMENT
# =========================================================

@router.post(
    "/{assignment_id}/reject",
)
def reject_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    workflow = AssignmentWorkflow(db)

    result = workflow.reject(
        assignment_id,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=409,
            detail=result,
        )

    return result


# =========================================================
# 11. COMPLETE ASSIGNMENT
# =========================================================

@router.post(
    "/{assignment_id}/complete",
)
def complete_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    workflow = AssignmentWorkflow(db)

    result = workflow.complete(
        assignment_id,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=409,
            detail=result,
        )

    return result


# =========================================================
# 12. CANCEL THROUGH WORKFLOW
# =========================================================

@router.post(
    "/{assignment_id}/cancel",
)
def cancel_assignment_workflow(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    workflow = AssignmentWorkflow(db)

    result = workflow.cancel(
        assignment_id,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=409,
            detail=result,
        )

    return result


# =========================================================
# 13. GET SINGLE ASSIGNMENT
# =========================================================

@router.get(
    "/{assignment_id}",
    response_model=AssignmentResponse,
)
def get_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.assignment_id
            == assignment_id
        )
        .first()
    )

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    return assignment


# =========================================================
# 14. UPDATE ASSIGNMENT STATUS
# =========================================================

@router.put(
    "/{assignment_id}/status",
)
def update_assignment_status(
    assignment_id: str,
    data: AssignmentStatusUpdate,
    db: Session = Depends(get_db),
):
    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.assignment_id
            == assignment_id
        )
        .first()
    )

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    allowed_statuses = [
        "ACTIVE",
        "PENDING",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED",
        "REJECTED",
    ]

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid assignment status",
                "allowed_statuses": allowed_statuses,
            },
        )

    assignment.status = data.status

    try:
        db.commit()
        db.refresh(assignment)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to update assignment status: "
                f"{str(exc)}"
            ),
        )

    return {
        "message": "Assignment status updated",
        "assignment_id": assignment.assignment_id,
        "status": assignment.status,
    }


# =========================================================
# 15. DELETE / CANCEL ASSIGNMENT
# =========================================================

@router.delete(
    "/{assignment_id}",
)
def delete_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.assignment_id
            == assignment_id
        )
        .first()
    )

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    # -----------------------------------------------------
    # Soft delete
    # -----------------------------------------------------

    assignment.status = "CANCELLED"

    try:
        db.commit()
        db.refresh(assignment)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to cancel assignment: "
                f"{str(exc)}"
            ),
        )

    return {
        "message": "Assignment cancelled successfully",
        "assignment_id": str(
            assignment.assignment_id
        ),
        "status": assignment.status,
    }


# =========================================================
# 16. ASSIGNMENT HISTORY
# =========================================================

@router.get(
    "/{assignment_id}/history",
)
def get_assignment_history(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # Check assignment
    # -----------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.assignment_id
            == assignment_id
        )
        .first()
    )

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    # -----------------------------------------------------
    # Get history
    # -----------------------------------------------------

    service = AssignmentHistoryService(db)

    history = service.get_history(
        assignment_id
    )

    return {
        "assignment_id": str(
            assignment_id
        ),
        "history": [
            {
                "history_id": item.history_id,
                "old_status": item.old_status,
                "new_status": item.new_status,
                "changed_by": item.changed_by,
                "reason": item.reason,
                "changed_at": item.changed_at,
            }
            for item in history
        ],
    }