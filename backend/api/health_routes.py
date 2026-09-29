"""
SkillSprint AI — Health & Readiness Monitoring Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db

router = APIRouter(tags=["Health & Readiness"])


@router.get("/healthz")
@router.get("/health")
def health_check():
    """Application health endpoint returning system operational status."""
    return {
        "status": "UP",
        "app": "SkillSprint AI",
        "version": "1.0.0"
    }


@router.get("/readiness")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness endpoint verifying database connectivity and essential services."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "READY",
            "database": "CONNECTED",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_530_SITE_IS_FROZEN,
            detail=f"Database connection failure: {str(e)}"
        )
