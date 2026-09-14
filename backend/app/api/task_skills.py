from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    Task,
    Skill,
    TaskSkill,
)

from app.schemas.task_skill import (
    TaskSkillCreate,
    TaskSkillResponse,
)


router = APIRouter(
    prefix="/task-skills",
    tags=["Task Skills"]
)


# ---------------------------------------------------------
# GET REQUIRED SKILLS FOR TASK
# ---------------------------------------------------------

@router.get(
    "/task/{task_id}",
    response_model=list[TaskSkillResponse]
)
def get_task_skills(
    task_id: str,
    db: Session = Depends(get_db)
):

    task = (
        db.query(Task)
        .filter(
            Task.task_id == task_id
        )
        .first()
    )

    if not task:

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    skills = (
        db.query(TaskSkill)
        .filter(
            TaskSkill.task_id == task_id
        )
        .all()
    )

    return skills


# ---------------------------------------------------------
# ADD REQUIRED SKILL TO TASK
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=TaskSkillResponse,
    status_code=201
)
def add_task_skill(
    skill_data: TaskSkillCreate,
    db: Session = Depends(get_db)
):

    task = (
        db.query(Task)
        .filter(
            Task.task_id ==
            skill_data.task_id
        )
        .first()
    )

    if not task:

        raise HTTPException(
            status_code=404,
            detail="Task not found"
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
        db.query(TaskSkill)
        .filter(
            TaskSkill.task_id ==
            skill_data.task_id,

            TaskSkill.skill_id ==
            skill_data.skill_id
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Skill already required for this task"
        )

    task_skill = TaskSkill(
        **skill_data.model_dump()
    )

    db.add(task_skill)
    db.commit()
    db.refresh(task_skill)

    return task_skill