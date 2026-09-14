from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Skill

from app.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillResponse,
)

from app.services.id_service import generate_id


router = APIRouter(
    prefix="/skills",
    tags=["Skills"]
)


# ---------------------------------------------------------
# GET ALL SKILLS
# ---------------------------------------------------------

@router.get(
    "/",
    response_model=list[SkillResponse]
)
def get_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):

    skills = (
        db.query(Skill)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return skills


# ---------------------------------------------------------
# GET SINGLE SKILL
# ---------------------------------------------------------

@router.get(
    "/{skill_id}",
    response_model=SkillResponse
)
def get_skill(
    skill_id: str,
    db: Session = Depends(get_db)
):

    skill = (
        db.query(Skill)
        .filter(
            Skill.skill_id == skill_id
        )
        .first()
    )

    if not skill:

        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    return skill


# ---------------------------------------------------------
# CREATE SKILL
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=SkillResponse,
    status_code=201
)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db)
):

    payload = skill_data.model_dump()

    payload["skill_id"] = generate_id(
        db,
        Skill,
        Skill.skill_id,
        prefix="SK",
        provided=payload.get("skill_id"),
    )

    skill = Skill(**payload)

    db.add(skill)

    try:
        db.commit()
        db.refresh(skill)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create skill: {exc}",
        )

    return skill


# ---------------------------------------------------------
# UPDATE SKILL
# ---------------------------------------------------------

@router.put(
    "/{skill_id}",
    response_model=SkillResponse
)
def update_skill(
    skill_id: str,
    skill_data: SkillUpdate,
    db: Session = Depends(get_db)
):

    skill = (
        db.query(Skill)
        .filter(
            Skill.skill_id == skill_id
        )
        .first()
    )

    if not skill:

        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    update_data = skill_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            skill,
            field,
            value
        )

    db.commit()
    db.refresh(skill)

    return skill


# ---------------------------------------------------------
# DELETE SKILL
# ---------------------------------------------------------

@router.delete(
    "/{skill_id}"
)
def delete_skill(
    skill_id: str,
    db: Session = Depends(get_db)
):

    skill = (
        db.query(Skill)
        .filter(
            Skill.skill_id == skill_id
        )
        .first()
    )

    if not skill:

        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    db.delete(skill)
    db.commit()

    return {
        "message": "Skill deleted successfully",
        "skill_id": skill_id
    }