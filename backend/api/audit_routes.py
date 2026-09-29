"""
SkillSprint AI — Immutable Audit Trail API Endpoints (Admin/Reviewer RBAC Protected)
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import AuditTrail, User
from backend.schemas.schemas import AuditLogResponse, PaginatedResponse
from security.auth import get_current_active_user, require_role
from security.audit_service import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["Immutable Audit Trail"])


@router.get("/history", response_model=PaginatedResponse[AuditLogResponse])
def get_audit_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    entity_id: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "REVIEWER", "TRAINING_MANAGER"]))
):
    """Retrieves immutable audit trail entries in descending chronological order (FR-45)."""
    query = db.query(AuditTrail)
    if entity_id:
        query = query.filter(AuditTrail.entity_id == entity_id)
    if entity_type:
        query = query.filter(AuditTrail.entity_type == entity_type)
    if event_type:
        query = query.filter(AuditTrail.event_type == event_type)
    if user_id:
        query = query.filter(AuditTrail.user_id == user_id)

    total = query.count()
    records = query.order_by(AuditTrail.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[AuditLogResponse](
        items=[AuditLogResponse.model_validate(r) for r in records],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
