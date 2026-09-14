from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Task, Project, Skill, TaskSkill

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)

from app.services.id_service import generate_id


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# ---------------------------------------------------------
# CREATE TASK
# ---------------------------------------------------------

@router.post(
    "",
    response_model=TaskResponse,
    status_code=201
)
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201,
    include_in_schema=False,
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):

    # Verify project exists
    project = (
        db.query(Project)
        .filter(
            Project.project_id == task_data.project_id
        )
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    payload = task_data.model_dump()

    required_skills = payload.pop("required_skills", []) or []

    # tasks.task_id is a String primary key with no default, so an
    # explicit value is mandatory. Generate one when the client
    # doesn't supply it.
    payload["task_id"] = generate_id(
        db,
        Task,
        Task.task_id,
        prefix="TASK",
        provided=payload.get("task_id"),
    )

    task = Task(**payload)

    db.add(task)
    db.flush()

    # -----------------------------------------------------
    # Persist the skill requirements the form collected.
    # Skills are matched by name first, then created if new,
    # so the ML matcher has real skill records to work with.
    # -----------------------------------------------------

    for entry in required_skills:

        skill_id = entry.get("skill_id")
        skill_name = (entry.get("skill_name") or "").strip()

        skill = None

        if skill_id:
            skill = (
                db.query(Skill)
                .filter(Skill.skill_id == skill_id)
                .first()
            )

        if skill is None and skill_name:
            skill = (
                db.query(Skill)
                .filter(Skill.skill_name.ilike(skill_name))
                .first()
            )

        if skill is None:

            if not (skill_id or skill_name):
                continue

            skill = Skill(
                skill_id=generate_id(
                    db,
                    Skill,
                    Skill.skill_id,
                    prefix="SK",
                    provided=skill_id,
                ),
                skill_name=skill_name or skill_id,
            )

            db.add(skill)
            db.flush()

        existing = (
            db.query(TaskSkill)
            .filter(
                TaskSkill.task_id == task.task_id,
                TaskSkill.skill_id == skill.skill_id,
            )
            .first()
        )

        if existing:
            continue

        db.add(TaskSkill(
            task_id=task.task_id,
            skill_id=skill.skill_id,
            required_level=entry.get("required_level") or 3,
            is_critical=bool(entry.get("is_critical")),
        ))

    try:
        db.commit()
        db.refresh(task)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create task: {exc}",
        )

    return task


# ---------------------------------------------------------
# GET ALL TASKS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[TaskResponse]
)
@router.get(
    "/",
    response_model=list[TaskResponse],
    include_in_schema=False,
)
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):

    tasks = (
        db.query(Task)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return tasks


# ---------------------------------------------------------
# GET SINGLE TASK
# ---------------------------------------------------------

@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
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

    return task


# ---------------------------------------------------------
# UPDATE TASK
# ---------------------------------------------------------

@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: str,
    task_data: TaskUpdate,
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

    update_data = task_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            task,
            field,
            value
        )

    db.commit()
    db.refresh(task)

    return task


# ---------------------------------------------------------
# DELETE TASK
# ---------------------------------------------------------

@router.delete(
    "/{task_id}"
)
def delete_task(
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

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }