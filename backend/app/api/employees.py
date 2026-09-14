from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
)
from app.services.employee_service import (
    list_employees,
    find_employee,
    add_employee,
    remove_employee,
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.get(
    "/",
    response_model=list[EmployeeResponse]
)
def get_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return list_employees(
        db,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee_by_id(
    employee_id: str,
    db: Session = Depends(get_db)
):
    employee = find_employee(
        db,
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=201
)
def create_new_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    return add_employee(
        db,
        employee.model_dump()
    )


@router.delete(
    "/{employee_id}"
)
def delete_employee_by_id(
    employee_id: str,
    db: Session = Depends(get_db)
):
    deleted = remove_employee(
        db,
        employee_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return {
        "message": "Employee deleted successfully"
    }