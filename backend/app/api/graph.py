from fastapi import APIRouter, HTTPException

from app.db.neo4j import neo4j_connection
from app.services.neo4j_service import Neo4jService


router = APIRouter(
    prefix="/graph",
    tags=["Skill Graph"]
)

graph_service = Neo4jService()


# =========================================================
# NEO4J HEALTH
# =========================================================

@router.get("/health")
def graph_health():

    try:

        neo4j_connection.verify_connection()

        return {
            "status": "healthy",
            "database": "neo4j"
        }

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail=f"Neo4j unavailable: {str(exc)}"
        )


# =========================================================
# TASK CANDIDATES FROM GRAPH
# =========================================================

@router.get("/task/{task_id}/candidates")
def get_task_candidates(task_id: str):

    try:

        candidates = graph_service.find_employees_for_task(
            task_id
        )

        return {
            "task_id": task_id,
            "candidate_count": len(candidates),
            "candidates": candidates
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )