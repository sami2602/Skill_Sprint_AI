"""
SkillSprint AI — Dynamic Analytics & System Metrics API Endpoints
All metrics are computed dynamically from actual database records and validation runs (NO hardcoding).
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.models.models import (
    Document,
    PolicyRequirement,
    Role,
    Employee,
    GeneratedPlan,
    ValidationRun,
    ManualReviewQueueItem,
    User
)
from backend.schemas.schemas import SystemMetricsResponse, OnboardingProgressAnalytics
from security.auth import get_current_active_user, require_role

router = APIRouter(prefix="/api/v1/analytics", tags=["System Analytics"])


@router.get("/system", response_model=SystemMetricsResponse)
def get_system_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Calculates and returns real-time organization-wide metrics from database state (FR-47, FR-58)."""
    doc_count = db.query(Document).count()
    req_count = db.query(PolicyRequirement).count()
    role_count = db.query(Role).count()
    emp_count = db.query(Employee).count()
    plan_count = db.query(GeneratedPlan).count()

    avg_coverage = db.query(func.avg(ValidationRun.coverage_score)).scalar() or 0.0
    avg_traceability = db.query(func.avg(ValidationRun.traceability_score)).scalar() or 0.0

    pending_reviews = db.query(ManualReviewQueueItem).filter(ManualReviewQueueItem.status == "PENDING").count()

    # Verification status distribution
    status_counts = db.query(ValidationRun.verification_status, func.count(ValidationRun.id)).\
        group_by(ValidationRun.verification_status).all()
    dist = {status_str: count for status_str, count in status_counts}

    return SystemMetricsResponse(
        document_count=doc_count,
        requirement_count=req_count,
        role_count=role_count,
        employee_count=emp_count,
        plan_count=plan_count,
        avg_coverage_score=round(float(avg_coverage), 2),
        avg_traceability_score=round(float(avg_traceability), 2),
        pending_reviews_count=pending_reviews,
        verification_status_distribution=dist
    )


@router.get("/onboarding", response_model=OnboardingProgressAnalytics)
def get_onboarding_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Calculates onboarding completion and velocity metrics across employees."""
    total_emp = db.query(Employee).count()
    
    # Calculate verified/completed plans
    completed_plans = db.query(ValidationRun).filter(ValidationRun.verification_status == "VERIFIED").count()
    on_track = db.query(ValidationRun).filter(ValidationRun.verification_status.in_(["VERIFIED_WITH_WARNING", "VERIFIED"])).count()
    behind = db.query(ValidationRun).filter(ValidationRun.verification_status == "INCOMPLETE").count()
    attention = db.query(ValidationRun).filter(ValidationRun.verification_status.in_(["UNSUPPORTED", "CONTRADICTORY", "MANUAL_REVIEW_REQUIRED"])).count()

    return OnboardingProgressAnalytics(
        total_enrolled=total_emp,
        completed_count=completed_plans,
        on_track_count=on_track,
        behind_schedule_count=behind,
        requires_attention_count=attention
    )


@router.get("/weak-areas", response_model=List[Dict[str, Any]])
def get_weak_areas_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Identifies topics or requirements where validation failures occur frequently (FR-51)."""
    # Query validation runs for missing mandatory requirements or ungrounded claims
    runs = db.query(ValidationRun).all()
    topic_failures: Dict[str, int] = {}
    for r in runs:
        ev = r.evidence_json or {}
        missing = ev.get("mandatory_missing", [])
        for req_id in missing:
            topic_failures[req_id] = topic_failures.get(req_id, 0) + 1

    result = [
        {"requirement_id": req_id, "failure_count": count, "severity": "HIGH" if count >= 2 else "MEDIUM"}
        for req_id, count in sorted(topic_failures.items(), key=lambda x: x[1], reverse=True)
    ]
    return result
