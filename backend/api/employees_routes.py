"""
SkillSprint AI — Employee Management & Onboarding Status API Endpoints
"""

import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import Employee, Role, GeneratedPlan, ValidationRun, User
from backend.schemas.schemas import (
    EmployeeResponse,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeOnboardingStatusResponse,
    PaginatedResponse
)
from security.auth import get_current_active_user, require_role
from security.audit_service import AuditService

router = APIRouter(prefix="/api/v1/employees", tags=["Employees Management"])


@router.get("", response_model=PaginatedResponse[EmployeeResponse])
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    department: Optional[str] = Query(None),
    role_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lists employee profiles with filtering and pagination."""
    query = db.query(Employee)

    # Manager view restriction (FR-02)
    if current_user.role == "MANAGER" and current_user.department:
        query = query.filter(Employee.department == current_user.department)
    elif current_user.role == "EMPLOYEE" and current_user.employee_id:
        query = query.filter(Employee.employee_id == current_user.employee_id)

    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    if role_id:
        if str(role_id).isdigit():
            query = query.filter(Employee.role_id == int(role_id))
        else:
            role_obj = db.query(Role).filter(Role.role_id == role_id).first()
            if role_obj:
                query = query.filter(Employee.role_id == role_obj.id)
    if search:
        pattern = f"%{search}%"
        query = query.filter((Employee.name.ilike(pattern)) | (Employee.employee_id.ilike(pattern)) | (Employee.email.ilike(pattern)))

    total = query.count()
    emp_list = query.order_by(Employee.employee_id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    result_items = []
    for emp in emp_list:
        role = db.query(Role).filter(Role.id == emp.role_id).first()
        res = EmployeeResponse.model_validate(emp)
        res.role_title = role.title if role else None
        result_items.append(res)

    return PaginatedResponse[EmployeeResponse](
        items=result_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    emp_in: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER", "TRAINING_MANAGER"]))
):
    """Creates a new employee profile (FR-03)."""
    existing = db.query(Employee).filter(
        (Employee.employee_id == emp_in.employee_id) | (Employee.email == emp_in.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with ID '{emp_in.employee_id}' or email '{emp_in.email}' already exists."
        )

    role = db.query(Role).filter(Role.id == emp_in.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role ID '{emp_in.role_id}' not found.")

    new_emp = Employee(
        employee_id=emp_in.employee_id,
        name=emp_in.name,
        email=emp_in.email,
        role_id=emp_in.role_id,
        department=emp_in.department,
        experience_level=emp_in.experience_level,
        joining_date=emp_in.joining_date,
        manager_id=emp_in.manager_id
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)

    AuditService(db).log_event(
        event_type="EMPLOYEE_CREATED",
        user_id=current_user.user_id,
        entity_type="EMPLOYEE",
        entity_id=new_emp.employee_id,
        new_value={"name": new_emp.name, "role_id": new_emp.role_id, "department": new_emp.department}
    )

    res = EmployeeResponse.model_validate(new_emp)
    res.role_title = role.title
    return res


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee_detail(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves employee profile detail."""
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee '{employee_id}' not found.")

    role = db.query(Role).filter(Role.id == emp.role_id).first()
    res = EmployeeResponse.model_validate(emp)
    res.role_title = role.title if role else None
    return res


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    update_in: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER", "TRAINING_MANAGER"]))
):
    """Updates employee profile fields or role assignment."""
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee '{employee_id}' not found.")

    if update_in.name:
        emp.name = update_in.name
    if update_in.email:
        emp.email = update_in.email
    if update_in.role_id:
        role = db.query(Role).filter(Role.id == update_in.role_id).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role ID '{update_in.role_id}' not found.")
        emp.role_id = update_in.role_id
    if update_in.department:
        emp.department = update_in.department
    if update_in.experience_level:
        emp.experience_level = update_in.experience_level
    if update_in.manager_id:
        emp.manager_id = update_in.manager_id

    db.commit()
    db.refresh(emp)

    AuditService(db).log_event(
        event_type="EMPLOYEE_UPDATED",
        user_id=current_user.user_id,
        entity_type="EMPLOYEE",
        entity_id=emp.employee_id,
        new_value={"name": emp.name, "department": emp.department, "role_id": emp.role_id}
    )

    role = db.query(Role).filter(Role.id == emp.role_id).first()
    res = EmployeeResponse.model_validate(emp)
    res.role_title = role.title if role else None
    return res


@router.get("/{employee_id}/status", response_model=EmployeeOnboardingStatusResponse)
def get_employee_onboarding_status(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves employee onboarding status, active plan ID, verification status, and completion metrics."""
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee '{employee_id}' not found.")

    role = db.query(Role).filter(Role.id == emp.role_id).first()

    # Find latest plan for employee or role
    plan = db.query(GeneratedPlan).filter(
        (GeneratedPlan.employee_id == employee_id) | (GeneratedPlan.role_id == role.role_id if role else False)
    ).order_by(GeneratedPlan.created_at.desc()).first()

    val_run = db.query(ValidationRun).filter(ValidationRun.plan_id == plan.plan_id).first() if plan else None

    return EmployeeOnboardingStatusResponse(
        employee_id=emp.employee_id,
        name=emp.name,
        email=emp.email,
        department=emp.department,
        role_id=role.role_id if role else str(emp.role_id),
        role_title=role.title if role else "Unknown Role",
        plan_id=plan.plan_id if plan else None,
        verification_status=val_run.verification_status if val_run else ("GENERATED" if plan else "NOT_STARTED"),
        coverage_score=val_run.coverage_score if val_run else (100.0 if plan else 0.0),
        traceability_score=val_run.traceability_score if val_run else (100.0 if plan else 0.0),
        overall_progress_pct=100.0 if val_run and val_run.verification_status == "VERIFIED" else (50.0 if plan else 0.0),
        onboarding_status="COMPLETED" if val_run and val_run.verification_status == "VERIFIED" else ("IN_PROGRESS" if plan else "NOT_STARTED")
    )
