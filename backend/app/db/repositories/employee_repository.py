from sqlalchemy.orm import Session

from app.db.models.employee import Employee


def get_all_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(Employee)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_employee(
    db: Session,
    employee_id: str
):
    return (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id
        )
        .first()
    )


def create_employee(
    db: Session,
    employee_data: dict
):
    employee = Employee(
        **employee_data
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def update_employee(
    db: Session,
    employee_id: str,
    employee_data: dict
):
    employee = get_employee(
        db,
        employee_id
    )

    if employee is None:
        return None

    for key, value in employee_data.items():

        if value is not None:
            setattr(
                employee,
                key,
                value
            )

    db.commit()
    db.refresh(employee)

    return employee


def delete_employee(
    db: Session,
    employee_id: str
):
    employee = get_employee(
        db,
        employee_id
    )

    if employee is None:
        return False

    db.delete(employee)
    db.commit()

    return True