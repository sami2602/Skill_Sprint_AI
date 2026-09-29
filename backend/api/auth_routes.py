"""
SkillSprint AI — Authentication API Endpoints
Handles user login, token issuance, credential verification, and user profile lookup.
"""

import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import User
from backend.schemas.schemas import UserLogin, TokenResponse, UserResponse, UserCreate, EmployeeSignupRequest
from security.auth import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_active_user,
    require_role
)
from security.audit_service import AuditService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login_for_access_token(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user with username and password, issuing a signed JWT Bearer token."""
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    token = create_access_token(data={"sub": user.username, "user_id": user.user_id, "role": user.role})
    
    # Audit log
    AuditService(db).log_event(
        event_type="USER_LOGIN",
        user_id=user.user_id,
        entity_type="USER",
        entity_id=user.user_id,
        reason="Successful user authentication login"
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        expires_in=86400
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Retrieves profile information for currently authenticated user."""
    return current_user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("/signup/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def employee_signup(
    signup_in: EmployeeSignupRequest,
    db: Session = Depends(get_db)
):
    """
    Public Employee Signup Endpoint.
    Enforces business rule: ONLY verified, active company employees can register.
    Validates work email against the Employee database record, verifies active employee status,
    prevents duplicate accounts, and derives role from employee record (no user self-assignment).
    """
    from backend.models.models import Employee, Role
    clean_email = signup_in.email.strip().lower()
    clean_username = signup_in.username.strip()

    # 1. Check if user account with email or username already exists
    existing_user = db.query(User).filter(
        (User.username.ilike(clean_username)) | (User.email.ilike(clean_email))
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address or username already exists."
        )

    # 2. Look up matching Employee in database
    emp_query = db.query(Employee).filter(Employee.email.ilike(clean_email))
    if signup_in.employee_id:
        emp_query = emp_query.filter(Employee.employee_id == signup_in.employee_id.strip())
    
    emp = emp_query.first()
    if not emp and signup_in.employee_id:
        emp = db.query(Employee).filter(Employee.employee_id == signup_in.employee_id.strip()).first()

    if not emp or emp.email.strip().lower() != clean_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration rejected: Email address is not recognized in official employee records."
        )

    # 3. Verify employee active status
    if hasattr(emp, "is_active") and not emp.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration rejected: Employee record is inactive/terminated."
        )

    # 4. Prevent duplicate registration for same employee
    existing_emp_user = db.query(User).filter(User.employee_id == emp.employee_id).first()
    if existing_emp_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account has already been registered for employee ID '{emp.employee_id}'."
        )

    # 5. Determine Role from Employee Record (DO NOT TRUST CLIENT)
    user_role = "EMPLOYEE"
    if emp.role_id:
        role_record = db.query(Role).filter(Role.id == emp.role_id).first()
        if role_record:
            rtitle = role_record.title.upper()
            if "ADMIN" in rtitle or "EXECUTIVE" in rtitle:
                user_role = "ADMIN"
            elif "REVIEW" in rtitle or "AUDITOR" in rtitle:
                user_role = "REVIEWER"
            elif "MANAGER" in rtitle or "LEAD" in rtitle:
                user_role = "MANAGER"
            else:
                user_role = "EMPLOYEE"

    new_user = User(
        user_id=f"USR-{uuid.uuid4().hex[:8].upper()}",
        username=clean_username,
        email=clean_email,
        hashed_password=hash_password(signup_in.password),
        role=user_role,
        department=emp.department,
        employee_id=emp.employee_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    AuditService(db).log_event(
        event_type="EMPLOYEE_REGISTERED",
        user_id=new_user.user_id,
        entity_type="USER",
        entity_id=new_user.user_id,
        new_value={"username": new_user.username, "email": new_user.email, "role": new_user.role, "employee_id": emp.employee_id}
    )

    return new_user
