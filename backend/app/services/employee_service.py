from sqlalchemy.orm import Session

from app.db.repositories.employee_repository import (
    get_all_employees,
    get_employee,
    create_employee,
    delete_employee,
)


def list_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return get_all_employees(
        db,
        skip=skip,
        limit=limit
    )


def find_employee(
    db: Session,
    employee_id: str
):
    return get_employee(
        db,
        employee_id
    )


def add_employee(
    db: Session,
    employee_data: dict
):
    return create_employee(
        db,
        employee_data
    )


def remove_employee(
    db: Session,
    employee_id: str
):
    return delete_employee(
        db,
        employee_id
    )