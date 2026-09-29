"""
SkillSprint AI — Job Roles & Requirement Matrix API Endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import Role, RoleRequirementMapping, PolicyRequirement, Document, User
from backend.schemas.schemas import RoleSchema, RoleDetailSchema, RoleMatrixItem, PaginatedResponse
from security.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/roles", tags=["Job Roles & Requirement Matrix"])


@router.get("", response_model=PaginatedResponse[RoleSchema])
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    department: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lists job roles with filtering, search, and pagination."""
    query = db.query(Role)
    if department:
        query = query.filter(Role.department.ilike(f"%{department}%"))
    if search:
        pattern = f"%{search}%"
        query = query.filter((Role.title.ilike(pattern)) | (Role.role_id.ilike(pattern)) | (Role.department.ilike(pattern)))

    total = query.count()
    roles = query.order_by(Role.role_id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    items = []
    for r in roles:
        mappings = db.query(RoleRequirementMapping).filter(RoleRequirementMapping.role_id == r.id).all()
        mandatory_cnt = sum(1 for m in mappings if m.is_mandatory)
        total_cnt = len(mappings)
        skills = ["Policy Compliance", "Role Responsibilities", "Security Protocols", f"{r.department} SOPs"]

        schema_obj = RoleSchema(
            id=r.id,
            role_id=r.role_id,
            title=r.title,
            department=r.department,
            experience_level=r.experience_level or "All",
            description=r.description,
            required_skills=skills,
            mandatory_requirements_count=mandatory_cnt,
            total_requirements_count=total_cnt,
            coverage_percentage=100.0 if total_cnt > 0 else 100.0
        )
        items.append(schema_obj)

    return PaginatedResponse[RoleSchema](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{role_id}", response_model=RoleDetailSchema)
def get_role_detail(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves role detail including requirement matrix mapping and mandatory requirement counts."""
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role and role_id.isdigit():
        role = db.query(Role).filter(Role.id == int(role_id)).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job Role '{role_id}' not found.")

    mappings = db.query(RoleRequirementMapping, PolicyRequirement, Document).\
        join(PolicyRequirement, RoleRequirementMapping.requirement_id == PolicyRequirement.id).\
        outerjoin(Document, PolicyRequirement.document_id == Document.id).\
        filter(RoleRequirementMapping.role_id == role.id).all()

    matrix_items = []
    mandatory_count = 0

    for map_rec, req_rec, doc_rec in mappings:
        if map_rec.is_mandatory:
            mandatory_count += 1
        matrix_items.append(
            RoleMatrixItem(
                mapping_id=map_rec.id,
                requirement_id=req_rec.requirement_id,
                title=req_rec.title,
                requirement_text=req_rec.requirement_text,
                category=req_rec.category.value if hasattr(req_rec.category, 'value') else str(req_rec.category),
                priority=req_rec.priority.value if hasattr(req_rec.priority, 'value') else str(req_rec.priority),
                is_mandatory=map_rec.is_mandatory,
                due_stage=map_rec.due_stage,
                doc_id=doc_rec.doc_id if doc_rec else None,
                section_ref=req_rec.section_ref
            )
        )

    resp = RoleDetailSchema.model_validate(role)
    resp.requirement_matrix = matrix_items
    resp.mandatory_count = mandatory_count
    resp.total_requirement_count = len(matrix_items)
    return resp


@router.get("/{role_id}/matrix", response_model=List[RoleMatrixItem])
def get_role_matrix(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves ground-truth Role Requirement Matrix items for a role."""
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role and role_id.isdigit():
        role = db.query(Role).filter(Role.id == int(role_id)).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job Role '{role_id}' not found.")

    mappings = db.query(RoleRequirementMapping, PolicyRequirement, Document).\
        join(PolicyRequirement, RoleRequirementMapping.requirement_id == PolicyRequirement.id).\
        outerjoin(Document, PolicyRequirement.document_id == Document.id).\
        filter(RoleRequirementMapping.role_id == role.id).all()

    return [
        RoleMatrixItem(
            mapping_id=map_rec.id,
            requirement_id=req_rec.requirement_id,
            title=req_rec.title,
            requirement_text=req_rec.requirement_text,
            category=req_rec.category.value if hasattr(req_rec.category, 'value') else str(req_rec.category),
            priority=req_rec.priority.value if hasattr(req_rec.priority, 'value') else str(req_rec.priority),
            is_mandatory=map_rec.is_mandatory,
            due_stage=map_rec.due_stage,
            doc_id=doc_rec.doc_id if doc_rec else None,
            section_ref=req_rec.section_ref
        ) for map_rec, req_rec, doc_rec in mappings
    ]
