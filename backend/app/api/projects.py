from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Project

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)

from app.services.id_service import generate_id


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# ---------------------------------------------------------
# CREATE PROJECT
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=201
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):

    payload = project_data.model_dump()

    payload["project_id"] = generate_id(
        db,
        Project,
        Project.project_id,
        prefix="PRJ",
        provided=payload.get("project_id"),
    )
    payload["project_name"] = payload.get("project_name") or payload["project_id"]

    existing = (
        db.query(Project)
        .filter(Project.project_id == payload["project_id"])
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="A project with this ID already exists",
        )

    project = Project(**payload)

    db.add(project)

    try:
        db.commit()
        db.refresh(project)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create project: {exc}",
        )

    return project


# ---------------------------------------------------------
# GET ALL PROJECTS
# ---------------------------------------------------------

@router.get(
    "/",
    response_model=list[ProjectResponse]
)
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):

    projects = (
        db.query(Project)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return projects


# ---------------------------------------------------------
# GET SINGLE PROJECT
# ---------------------------------------------------------

@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):

    project = (
        db.query(Project)
        .filter(
            Project.project_id == project_id
        )
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


# ---------------------------------------------------------
# UPDATE PROJECT
# ---------------------------------------------------------

@router.put(
    "/{project_id}",
    response_model=ProjectResponse
)
def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
):

    project = (
        db.query(Project)
        .filter(
            Project.project_id == project_id
        )
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    update_data = project_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            project,
            field,
            value
        )

    db.commit()
    db.refresh(project)

    return project


# ---------------------------------------------------------
# DELETE PROJECT
# ---------------------------------------------------------

@router.delete(
    "/{project_id}"
)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):

    project = (
        db.query(Project)
        .filter(
            Project.project_id == project_id
        )
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully",
        "project_id": project_id
    }