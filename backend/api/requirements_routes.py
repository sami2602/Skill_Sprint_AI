"""
SkillSprint AI — Policy Requirements API Endpoints
Provides endpoints for searching, filtering, and retrieving extracted policy requirements and source traceability.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import PolicyRequirement, Document, User
from backend.schemas.schemas import RequirementSchema, RequirementDetailSchema, PaginatedResponse
from security.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/requirements", tags=["Requirements Catalog"])


@router.get("", response_model=PaginatedResponse[RequirementSchema])
def list_requirements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="MUST_KNOW, MUST_COMPLETE, MUST_DEMONSTRATE, MUST_ACKNOWLEDGE, RECOMMENDED, OPTIONAL"),
    priority: Optional[str] = Query(None, description="HIGH, MEDIUM, LOW"),
    is_mandatory: Optional[bool] = Query(None),
    role_id: Optional[str] = Query(None, description="Filter requirements applicable to specific role"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lists policy requirements with filtering by category, priority, mandatory status, role, search query, and pagination."""
    query = db.query(PolicyRequirement)
    if category:
        query = query.filter(PolicyRequirement.category == category.upper())
    if priority:
        query = query.filter(PolicyRequirement.priority == priority.upper())
    if is_mandatory is not None:
        query = query.filter(PolicyRequirement.is_mandatory == is_mandatory)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (PolicyRequirement.title.ilike(pattern)) |
            (PolicyRequirement.requirement_text.ilike(pattern)) |
            (PolicyRequirement.requirement_id.ilike(pattern))
        )

    all_reqs = query.all()
    if role_id:
        filtered_reqs = []
        for r in all_reqs:
            roles = r.target_roles or ["ALL"]
            if "ALL" in roles or role_id in roles:
                filtered_reqs.append(r)
        total = len(filtered_reqs)
        items = filtered_reqs[(page - 1) * page_size : page * page_size]
    else:
        total = len(all_reqs)
        items = all_reqs[(page - 1) * page_size : page * page_size]

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[RequirementSchema](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{requirement_id}", response_model=RequirementDetailSchema)
def get_requirement_detail(
    requirement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves requirement detail with source document traceability metadata."""
    req = db.query(PolicyRequirement).filter(PolicyRequirement.requirement_id == requirement_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement '{requirement_id}' not found.")

    doc = db.query(Document).filter(Document.id == req.document_id).first()
    resp = RequirementDetailSchema.model_validate(req)
    if doc:
        resp.doc_title = doc.title
        resp.doc_version = doc.version
    return resp
