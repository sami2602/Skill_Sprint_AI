"""
SkillSprint AI — Ground-Truth Validation API Endpoints
Provides endpoints to trigger and inspect independent Python ground-truth validation runs and evidence.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import GeneratedPlan, ValidationRun, User
from validation.validators.orchestrator import ValidationOrchestrator
from security.auth import get_current_active_user, require_permission
from security.audit_service import AuditService

router = APIRouter(prefix="/api/v1/validation", tags=["Python Ground-Truth Validation"])


@router.post("/run", status_code=status.HTTP_200_OK)
def run_python_validation(
    plan_id: str = Query(..., description="Target onboarding plan ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Executes independent Python Ground-Truth Validation (Pipeline 2) for an onboarding plan.
    Calculates Coverage Score, Traceability Score, flags missing mandatory items, and updates verification status.
    """
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Onboarding Plan '{plan_id}' not found.")

    validator = ValidationOrchestrator(db)
    val_evidence = validator.validate_plan(plan.payload_json or {})

    # Fetch updated ValidationRun record
    val_run = db.query(ValidationRun).filter(ValidationRun.plan_id == plan_id).first()

    AuditService(db).log_event(
        event_type="VALIDATION_EVENT",
        user_id=current_user.user_id,
        entity_type="PLAN",
        entity_id=plan_id,
        new_value={
            "coverage_score": val_evidence.coverage_score,
            "traceability_score": val_evidence.traceability_score,
            "verification_status": val_evidence.verification_status
        }
    )

    return {
        "run_id": val_run.run_id if val_run else f"RUN-{plan_id}",
        "plan_id": plan_id,
        "role_id": plan.role_id,
        "verification_status": val_evidence.verification_status,
        "coverage_score": val_evidence.coverage_score,
        "traceability_score": val_evidence.traceability_score,
        "mandatory_total": val_evidence.mandatory_total,
        "mandatory_covered": val_evidence.mandatory_covered,
        "execution_time_ms": val_evidence.execution_time_ms,
        "created_at": val_run.created_at if val_run else plan.created_at
    }


@router.get("/results/{plan_id}")
def get_validation_results(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves stored validation run results for a plan."""
    val_run = db.query(ValidationRun).filter(ValidationRun.plan_id == plan_id).first()
    if not val_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run for plan '{plan_id}' not found.")

    return {
        "run_id": val_run.run_id,
        "plan_id": val_run.plan_id,
        "role_id": val_run.role_id,
        "verification_status": val_run.verification_status,
        "coverage_score": val_run.coverage_score,
        "traceability_score": val_run.traceability_score,
        "mandatory_total": val_run.mandatory_total,
        "mandatory_covered": val_run.mandatory_covered,
        "execution_time_ms": val_run.execution_time_ms,
        "created_at": val_run.created_at
    }


@router.get("/evidence/{plan_id}")
def get_validation_evidence(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves itemized validation evidence JSON for a plan (missing mandatory items, ungrounded claims, sequence warnings)."""
    val_run = db.query(ValidationRun).filter(ValidationRun.plan_id == plan_id).first()
    if not val_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation evidence for plan '{plan_id}' not found.")

    return val_run.evidence_json or {}
