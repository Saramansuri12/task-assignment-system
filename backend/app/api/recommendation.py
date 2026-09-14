from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
)

from app.services.recommendation_engine import (
    RecommendationEngine,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


# =========================================================
# POST - RECOMMEND EMPLOYEES
# =========================================================

@router.post(
    "",
    response_model=RecommendationResponse,
)
def recommend_employees(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # Recommendation engine
    # -----------------------------------------------------

    engine = RecommendationEngine(db)

    recommendations = engine.recommend(
        task_id=request.task_id,
        top_k=request.top_k,
    )

    # -----------------------------------------------------
    # Task not found
    # -----------------------------------------------------

    if recommendations is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "task_id": request.task_id,
        "recommendations": recommendations,
    }


# =========================================================
# GET - RECOMMEND EMPLOYEES
# =========================================================

@router.get(
    "/{task_id}",
    response_model=RecommendationResponse,
)
def get_recommendations(
    task_id: str,
    top_k: int = 5,
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # Validate top_k
    # -----------------------------------------------------

    if top_k < 1:
        raise HTTPException(
            status_code=400,
            detail="top_k must be at least 1",
        )

    if top_k > 20:
        raise HTTPException(
            status_code=400,
            detail="top_k cannot be greater than 20",
        )

    # -----------------------------------------------------
    # Recommendation engine
    # -----------------------------------------------------

    engine = RecommendationEngine(db)

    recommendations = engine.recommend(
        task_id=task_id,
        top_k=top_k,
    )

    # -----------------------------------------------------
    # Task not found
    # -----------------------------------------------------

    if recommendations is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "task_id": task_id,
        "recommendations": recommendations,
    }