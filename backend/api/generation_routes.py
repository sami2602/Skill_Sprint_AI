"""
SkillSprint AI — GenAI Generation API Endpoints
Provides routes for triggering onboarding plan generation, checking generation status, and inspecting generated modules, tasks, and quizzes.
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import Role, Employee, GeneratedPlan, ValidationRun, User
from backend.schemas.schemas import (
    GenerationRequest,
    GeneratedPlanResponse,
    GenerationStatusResponse,
    PaginatedResponse
)
from genai.generators.pipeline_runner import GenAIPipelineRunner
from validation.validators.orchestrator import ValidationOrchestrator
from security.auth import get_current_active_user, require_permission, require_role
from security.audit_service import AuditService

router = APIRouter(prefix="/api/v1/generation", tags=["GenAI Onboarding Generation"])


@router.post("/plan", response_model=GeneratedPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_onboarding_plan(
    request: GenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "REVIEWER", "MANAGER", "TRAINING_MANAGER"]))
):
    """
    Generates a personalized multi-stage onboarding plan for a role and/or employee.
    Executes GenAI generator pipeline, stores plan payload in DB, and runs independent Python validator.
    """
    role = db.query(Role).filter(Role.role_id == request.role_id).first()
    if not role and request.role_id.isdigit():
        role = db.query(Role).filter(Role.id == int(request.role_id)).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job Role '{request.role_id}' not found.")

    emp = None
    if request.employee_id:
        emp = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()

    pipeline = GenAIPipelineRunner()
    try:
        plan_obj = pipeline.generate_onboarding_plan(
            db_session=db,
            role_id=role.role_id,
            employee_id=emp.employee_id if emp else None,
            employee_name=emp.name if emp else None,
            experience_level=request.experience_level or (emp.experience_level if emp else "Junior"),
            assigned_responsibilities=f"Onboarding training for {role.title}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GenAI Plan Generation failed: {str(e)}"
        )

    plan_id = plan_obj.plan_id
    if db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first():
        plan_id = f"{plan_id}-{uuid.uuid4().hex[:6].upper()}"

    covered_ids = plan_obj.covered_requirement_ids or []
    
    # Save GeneratedPlan to database
    db_plan = GeneratedPlan(
        plan_id=plan_id,
        role_id=role.role_id,
        employee_id=emp.employee_id if emp else None,
        role_title=role.title,
        department=request.department or role.department,
        version="1.0",
        payload_json=plan_obj.model_dump(),
        covered_requirement_ids=covered_ids,
        provider_name="Google Gemini API",
        model_name="gemini-1.5-pro",
        prompt_version="v1",
        status="SUCCESS"
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    # Automatically trigger independent Python ground-truth validation
    python_validator = ValidationOrchestrator(db)
    val_evidence = python_validator.validate_plan(db_plan.payload_json)

    # Record Audit Event
    AuditService(db).log_event(
        event_type="GENERATION_EVENT",
        user_id=current_user.user_id,
        entity_type="PLAN",
        entity_id=db_plan.plan_id,
        new_value={
            "role_id": role.role_id,
            "employee_id": request.employee_id,
            "coverage_score": val_evidence.coverage_score,
            "verification_status": val_evidence.verification_status
        }
    )

    return db_plan


@router.get("/plans", response_model=PaginatedResponse[GeneratedPlanResponse])
def list_generated_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role_id: Optional[str] = Query(None),
    employee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lists generated onboarding plans with pagination and filters."""
    query = db.query(GeneratedPlan)
    if role_id:
        query = query.filter(GeneratedPlan.role_id == role_id)
    if employee_id:
        query = query.filter(GeneratedPlan.employee_id == employee_id)

    # Restriction for Employee role
    if current_user.role == "EMPLOYEE" and current_user.employee_id:
        query = query.filter(GeneratedPlan.employee_id == current_user.employee_id)

    total = query.count()
    plans = query.order_by(GeneratedPlan.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[GeneratedPlanResponse](
        items=plans,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/plans/{plan_id}", response_model=GeneratedPlanResponse)
def get_generated_plan_detail(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves full detail and payload JSON for a generated onboarding plan."""
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Generated Plan '{plan_id}' not found.")
    return plan


@router.get("/plans/{plan_id}/modules", response_model=List[Dict[str, Any]])
def get_plan_modules(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves all learning modules for a plan."""
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{plan_id}' not found.")

    payload = plan.payload_json or {}
    return payload.get("modules", [])


@router.get("/plans/{plan_id}/tasks", response_model=List[Dict[str, Any]])
def get_plan_tasks(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves all practical tasks for a plan."""
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{plan_id}' not found.")

    tasks = []
    payload = plan.payload_json or {}
    for mod in payload.get("modules", []):
        for tsk in mod.get("tasks", []):
            tasks.append(tsk)
    return tasks


@router.get("/plans/{plan_id}/quizzes", response_model=List[Dict[str, Any]])
def get_plan_quizzes(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves all quizzes for a plan."""
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{plan_id}' not found.")

    quizzes = []
    payload = plan.payload_json or {}
    for mod in payload.get("modules", []):
        for q in mod.get("quizzes", []):
            quizzes.append(q)
    return quizzes
