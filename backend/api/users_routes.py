"""
SkillSprint AI — User Management API Endpoints (Admin RBAC Protected)
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import User
from backend.schemas.schemas import UserResponse, UserUpdate, PaginatedResponse
from security.auth import get_current_active_user, require_role, hash_password
from security.audit_service import AuditService

router = APIRouter(prefix="/api/v1/users", tags=["Users Management"])


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """Lists system users with pagination, role filtering, and search (Admin restricted)."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role.upper())
    if search:
        search_pattern = f"%{search}%"
        query = query.filter((User.username.ilike(search_pattern)) | (User.email.ilike(search_pattern)))

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[UserResponse](
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user_detail(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves user detail. Users can access their own profile; Admins can access any user."""
    if current_user.role != "ADMIN" and current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found.")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    update_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """Updates user fields (role, active status, email) with audit logging (Admin restricted)."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found.")

    original_val = {"email": user.email, "role": user.role, "is_active": user.is_active}
    
    if update_in.email:
        user.email = update_in.email
    if update_in.role:
        user.role = update_in.role.upper()
    if update_in.is_active is not None:
        user.is_active = update_in.is_active
    if update_in.department:
        user.department = update_in.department
    if update_in.employee_id:
        user.employee_id = update_in.employee_id
    if update_in.password:
        user.hashed_password = hash_password(update_in.password)

    db.commit()
    db.refresh(user)

    AuditService(db).log_event(
        event_type="USER_UPDATED",
        user_id=current_user.user_id,
        entity_type="USER",
        entity_id=user.user_id,
        original_value=original_val,
        new_value={"email": user.email, "role": user.role, "is_active": user.is_active}
    )

    return user
