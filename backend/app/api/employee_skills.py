from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    Employee,
    Skill,
    EmployeeSkill,
)

from app.schemas.employee_skill import (
    EmployeeSkillCreate,
    EmployeeSkillResponse,
)


router = APIRouter(
    prefix="/employee-skills",
    tags=["Employee Skills"]
)


# ---------------------------------------------------------
# GET EMPLOYEE SKILLS
# ---------------------------------------------------------

@router.get(
    "/employee/{employee_id}",
    response_model=list[EmployeeSkillResponse]
)
def get_employee_skills(
    employee_id: str,
    db: Session = Depends(get_db)
):

    employee = (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id
        )
        .first()
    )

    if not employee:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    skills = (
        db.query(EmployeeSkill)
        .filter(
            EmployeeSkill.employee_id == employee_id
        )
        .all()
    )

    return skills


# ---------------------------------------------------------
# ADD SKILL TO EMPLOYEE
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=EmployeeSkillResponse,
    status_code=201
)
def add_employee_skill(
    skill_data: EmployeeSkillCreate,
    db: Session = Depends(get_db)
):

    employee = (
        db.query(Employee)
        .filter(
            Employee.employee_id ==
            skill_data.employee_id
        )
        .first()
    )

    if not employee:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    skill = (
        db.query(Skill)
        .filter(
            Skill.skill_id ==
            skill_data.skill_id
        )
        .first()
    )

    if not skill:

        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    existing = (
        db.query(EmployeeSkill)
        .filter(
            EmployeeSkill.employee_id ==
            skill_data.employee_id,

            EmployeeSkill.skill_id ==
            skill_data.skill_id
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Employee already has this skill"
        )

    employee_skill = EmployeeSkill(
        **skill_data.model_dump()
    )

    db.add(employee_skill)
    db.commit()
    db.refresh(employee_skill)

    return employee_skill


# ---------------------------------------------------------
# UPDATE EMPLOYEE SKILL
# ---------------------------------------------------------

@router.put(
    "/{employee_id}/{skill_id}",
    response_model=EmployeeSkillResponse
)
def update_employee_skill(
    employee_id: str,
    skill_id: str,
    skill_level: float,
    db: Session = Depends(get_db)
):

    if not 1 <= skill_level <= 5:

        raise HTTPException(
            status_code=400,
            detail="Skill level must be between 1 and 5"
        )

    employee_skill = (
        db.query(EmployeeSkill)
        .filter(
            EmployeeSkill.employee_id == employee_id,
            EmployeeSkill.skill_id == skill_id
        )
        .first()
    )

    if not employee_skill:

        raise HTTPException(
            status_code=404,
            detail="Employee skill not found"
        )

    employee_skill.skill_level = skill_level

    db.commit()
    db.refresh(employee_skill)

    return employee_skill


# ---------------------------------------------------------
# DELETE EMPLOYEE SKILL
# ---------------------------------------------------------

@router.delete(
    "/{employee_id}/{skill_id}"
)
def delete_employee_skill(
    employee_id: str,
    skill_id: str,
    db: Session = Depends(get_db)
):

    employee_skill = (
        db.query(EmployeeSkill)
        .filter(
            EmployeeSkill.employee_id == employee_id,
            EmployeeSkill.skill_id == skill_id
        )
        .first()
    )

    if not employee_skill:

        raise HTTPException(
            status_code=404,
            detail="Employee skill not found"
        )

    db.delete(employee_skill)
    db.commit()

    return {
        "message": "Employee skill deleted successfully",
        "employee_id": employee_id,
        "skill_id": skill_id
    }