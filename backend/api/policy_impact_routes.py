"""
SkillSprint AI — Policy Impact Analysis & Selective Regeneration API Endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import User
from document_processing.versioning.impact_analysis import ImpactAnalysisEngine
from genai.generators.selective_regenerator import SelectiveRegenerationEngine
from validation.schemas import (
    PolicyImpactAnalysisRequest,
    PolicyImpactAnalysisResponse,
    SelectiveRegenerationRequest,
    SelectiveRegenerationResponse
)
from security.auth import get_current_active_user, require_role, require_permission
from security.audit_service import AuditService

router = APIRouter(prefix="/api/v1/policy-impact", tags=["Policy Impact & Selective Regeneration"])


@router.post("/analyze", response_model=PolicyImpactAnalysisResponse)
def analyze_policy_impact(
    request: PolicyImpactAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "REVIEWER", "MANAGER", "TRAINING_MANAGER"]))
):
    """Analyzes impact chain across requirements, roles, plans, modules, tasks, and quizzes when a policy updates (FR-53, FR-54)."""
    engine = ImpactAnalysisEngine(db)
    result = engine.analyze_impact(
        doc_id=request.doc_id,
        new_version=request.new_version,
        old_version=request.old_version
    )
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])

    AuditService(db).log_event(
        event_type="POLICY_VERSION_CHANGE",
        user_id=current_user.user_id,
        entity_type="DOCUMENT",
        entity_id=request.doc_id,
        new_value={"new_version": request.new_version, "old_version": request.old_version}
    )

    return result


@router.post("/selective-regenerate", response_model=SelectiveRegenerationResponse)
def execute_selective_regeneration(
    request: SelectiveRegenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("selective_regenerate"))
):
    """Executes selective regeneration for affected modules while preserving untouched modules intact (FR-55)."""
    engine = SelectiveRegenerationEngine(db)
    result = engine.regenerate_selective(
        plan_id=request.plan_id,
        doc_id=request.doc_id,
        old_version=request.old_version,
        new_version=request.new_version,
        affected_module_ids=request.affected_module_ids,
        reason=request.reason,
        requested_by=request.requested_by or current_user.user_id
    )
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    AuditService(db).log_event(
        event_type="REGENERATION_EVENT",
        user_id=current_user.user_id,
        entity_type="PLAN",
        entity_id=request.plan_id,
        reason=request.reason or f"Selective regeneration for doc {request.doc_id}"
    )

    return result
