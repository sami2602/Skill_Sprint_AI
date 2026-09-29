"""
SkillSprint AI — Human Review Queue & Override API Endpoints (Reviewer/Admin RBAC Protected)
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import User
from backend.schemas.schemas import ReviewerActionRequest, ReviewQueueItemResponse
from validation.reports.review_queue import ManualReviewQueueManager
from security.auth import get_current_active_user, require_permission, require_role

router = APIRouter(prefix="/api/v1/review", tags=["Human Review & Overrides"])


@router.get("/queue", response_model=List[ReviewQueueItemResponse])
def get_pending_review_queue(
    plan_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query("PENDING"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "REVIEWER"]))
):
    """Returns pending items in the manual review queue (Reviewer/Admin restricted - FR-44)."""
    manager = ManualReviewQueueManager(db)
    items = manager.get_pending_review_items(plan_id=plan_id)
    if status_filter and status_filter.upper() != "ALL":
        items = [i for i in items if i.get("status") == status_filter.upper()]
    return [ReviewQueueItemResponse.model_validate(i) for i in items]


@router.get("/inspect/{plan_id}/{item_id}")
def inspect_review_item(
    plan_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "REVIEWER"]))
):
    """Retrieves detailed itemized evidence for manual review inspection (FR-44)."""
    manager = ManualReviewQueueManager(db)
    inspection = manager.inspect_item(plan_id=plan_id, item_id=item_id)
    if "error" in inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=inspection["error"])
    return inspection


@router.post("/action")
def apply_reviewer_action(
    request: ReviewerActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "REVIEWER"]))
):
    """Applies reviewer action (APPROVE, REJECT, REQUEST_REVISION, OVERRIDE) with immutable audit logging (FR-45)."""
    if not request.reviewer_id or not request.comment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reviewer ID and commentary are required.")

    from backend.models.models import ManualReviewQueueItem
    from validation.schemas import ReviewerOverrideRequest

    plan_id = request.plan_id
    item_id = request.item_id

    if (not plan_id or not item_id) and request.review_id:
        queue_item = db.query(ManualReviewQueueItem).filter(
            (ManualReviewQueueItem.review_id == request.review_id) |
            (ManualReviewQueueItem.item_id == request.review_id)
        ).first()
        if queue_item:
            plan_id = plan_id or queue_item.plan_id
            item_id = item_id or queue_item.item_id

    req_dto = ReviewerOverrideRequest(
        plan_id=plan_id or "PLAN-DEFAULT",
        item_id=item_id or request.review_id,
        review_id=request.review_id,
        action=request.action,
        reviewer_id=request.reviewer_id,
        comment=request.comment,
        override_reason=request.override_reason
    )

    manager = ManualReviewQueueManager(db)
    result = manager.apply_reviewer_action(req_dto)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result
