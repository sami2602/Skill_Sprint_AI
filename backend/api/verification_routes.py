"""
SkillSprint AI — Verification & Comparison Report API Endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import GeneratedPlan, ValidationRun, User
from validation.reports.comparison_engine import RequirementComparisonEngine
from validation.rules.decision_engine import VerificationDecisionEngine
from validation.schemas import RequirementComparisonReport, VerificationSummarySchema
from security.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/verification", tags=["Verification & Comparison"])


@router.get("/summary/{plan_id}", response_model=VerificationSummarySchema)
def get_verification_summary(plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Calculates and returns dynamic verification summary metrics (FR-43)."""
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Onboarding plan '{plan_id}' not found.")

    val_run = db.query(ValidationRun).filter(ValidationRun.plan_id == plan_id).first()
    evidence_data = val_run.evidence_json if val_run else {
        "mandatory_total": len(plan.covered_requirement_ids or []),
        "mandatory_covered": len(plan.covered_requirement_ids or []),
        "mandatory_missing": [],
        "coverage_score": 100.0,
        "traceable_items": 10,
        "untraceable_items": 0,
        "traceability_score": 100.0
    }

    decision_engine = VerificationDecisionEngine(db)
    summary = decision_engine.calculate_verification_summary(
        plan_id=plan_id,
        role_id=plan.role_id,
        evidence=evidence_data
    )
    return summary


@router.get("/comparison/{plan_id}", response_model=RequirementComparisonReport)
def get_comparison_report(plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Retrieves requirement-level comparison report for an onboarding plan (FR-42)."""
    plan = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Onboarding plan '{plan_id}' not found.")

    engine = RequirementComparisonEngine(db)
    val_run = db.query(ValidationRun).filter(ValidationRun.plan_id == plan_id).first()
    evidence_data = val_run.evidence_json if val_run else None

    plan_payload = dict(plan.payload_json or {})
    plan_payload["plan_id"] = plan.plan_id

    report = engine.generate_comparison_report(
        role_id=plan.role_id,
        plan_data=plan_payload,
        validator_evidence=evidence_data
    )
    return report
