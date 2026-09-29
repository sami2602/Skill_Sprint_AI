"""
SkillSprint AI — Manual Review Queue & Reviewer Override Manager
Manages reviewer workflow for flagged validation items, preserving original validation results while maintaining an append-only audit trail (SRS FR-44, FR-45).
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models.models import ManualReviewQueueItem, ComparisonResultModel, ValidationRun
from validation.schemas import ValidationEvidenceSchema, ReviewerOverrideRequest, VerificationStatusEnum
from security.audit_service import AuditService


class ManualReviewQueueManager:
    """Handles manual review routing, approvals, rejections, revisions, overrides, and audit trails (FR-44, FR-45)."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.audit_service = AuditService(db_session)

    def route_evidence_to_queue(self, evidence: ValidationEvidenceSchema) -> List[ManualReviewQueueItem]:
        """
        Routes flagged items from a ValidationEvidenceSchema into the manual review queue table.
        Does not mutate the original deterministic evidence result.
        """
        created_items: List[ManualReviewQueueItem] = []

        # 1. Route missing mandatory requirements
        for req_id in evidence.mandatory_missing:
            item = ManualReviewQueueItem(
                review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
                plan_id=evidence.plan_id,
                item_id=req_id,
                item_type="REQUIREMENT",
                flag_type="MISSING_MANDATORY",
                evidence_data={"requirement_id": req_id, "role_id": evidence.role_id, "reason": "Mandatory requirement omitted from plan."},
                status="PENDING"
            )
            self.db.add(item)
            created_items.append(item)

        # 2. Route unsupported items
        for unsup in evidence.unsupported_items:
            item = ManualReviewQueueItem(
                review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
                plan_id=evidence.plan_id,
                item_id=unsup.get("item_id", unsup.get("requirement_id", "UNSUPPORTED_ITEM")),
                item_type=unsup.get("item_type", "TASK"),
                flag_type="UNGROUNDED",
                evidence_data=unsup,
                status="PENDING"
            )
            self.db.add(item)
            created_items.append(item)

        # 3. Route contradictions
        for contra in evidence.contradictions:
            item = ManualReviewQueueItem(
                review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
                plan_id=evidence.plan_id,
                item_id=contra.get("requirement_id", contra.get("generated_item", "CONTRADICTION_ITEM")),
                item_type=contra.get("item_type", "TASK"),
                flag_type="CONTRADICTION",
                evidence_data=contra,
                status="PENDING"
            )
            self.db.add(item)
            created_items.append(item)

        # 4. Route outdated sources
        for outdated in evidence.outdated_sources:
            item = ManualReviewQueueItem(
                review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
                plan_id=evidence.plan_id,
                item_id=outdated.get("requirement_id", outdated.get("doc_id", "OUTDATED_SOURCE")),
                item_type="DOCUMENT",
                flag_type="OUTDATED_SOURCE",
                evidence_data=outdated,
                status="PENDING"
            )
            self.db.add(item)
            created_items.append(item)

        # 5. Route duplicate items
        for dup in evidence.duplicate_items:
            item = ManualReviewQueueItem(
                review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
                plan_id=evidence.plan_id,
                item_id=dup.get("item_id", "DUPLICATE_ITEM"),
                item_type=dup.get("item_type", "TASK"),
                flag_type="DUPLICATE",
                evidence_data=dup,
                status="PENDING"
            )
            self.db.add(item)
            created_items.append(item)

        # 6. Route sequence errors
        for seq in evidence.sequence_errors:
            item = ManualReviewQueueItem(
                review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
                plan_id=evidence.plan_id,
                item_id=seq.get("affected_item", "SEQUENCE_ITEM"),
                item_type=seq.get("item_type", "MODULE"),
                flag_type="SEQUENCE_ERROR",
                evidence_data=seq,
                status="PENDING"
            )
            self.db.add(item)
            created_items.append(item)

        # 7. Route quiz errors
        for q_err in evidence.quiz_errors:
            item = ManualReviewQueueItem(
                review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
                plan_id=evidence.plan_id,
                item_id=q_err.get("question_id", "QUIZ_ITEM"),
                item_type="QUIZ_QUESTION",
                flag_type="QUIZ_ERROR",
                evidence_data=q_err,
                status="PENDING"
            )
            self.db.add(item)
            created_items.append(item)

        self.db.commit()

        # Audit trail logging
        self.audit_service.log_event(
            event_type="VALIDATION_EVENT",
            user_id="SYSTEM",
            entity_type="PLAN",
            entity_id=evidence.plan_id,
            original_value=None,
            new_value={"flagged_count": len(created_items), "status": evidence.verification_status.value},
            reason=f"Routed {len(created_items)} validation issues to manual review queue."
        )

        return created_items

    def apply_reviewer_action(self, request: ReviewerOverrideRequest) -> Dict[str, Any]:
        """
        Applies manual reviewer action (APPROVE, REJECT, REQUEST_REVISION, OVERRIDE).
        1. Updates review queue item status and records commentary.
        2. Updates reviewer fields in comparison_results table without erasing validator's original result.
        3. Appends an immutable AuditTrail record capturing reviewer ID, original value, new value, and justification.
        """
        review_item = self.db.query(ManualReviewQueueItem).filter(
            ManualReviewQueueItem.plan_id == request.plan_id,
            ManualReviewQueueItem.item_id == request.item_id
        ).first()

        if not review_item:
            review_item = ManualReviewQueueItem(
                review_id=f"REV-{uuid.uuid4().hex[:8].upper()}",
                plan_id=request.plan_id,
                item_id=request.item_id,
                item_type="REQUIREMENT",
                flag_type="REVIEWER_ACTION",
                evidence_data={"action": request.action},
                status="PENDING"
            )
            self.db.add(review_item)

        old_status = review_item.status
        action_upper = request.action.upper()
        
        if action_upper in ["APPROVE", "APPROVED"]:
            new_status = "APPROVED"
        elif action_upper in ["REJECT", "REJECTED"]:
            new_status = "REJECTED"
        elif action_upper in ["REQUEST_REVISION", "REVISION_REQUESTED"]:
            new_status = "REVISION_REQUESTED"
        elif action_upper in ["OVERRIDE", "OVERRIDDEN"]:
            new_status = "OVERRIDDEN"
        else:
            new_status = action_upper

        review_item.status = new_status
        review_item.reviewer_id = request.reviewer_id
        review_item.reviewer_comment = request.comment
        review_item.override_reason = request.override_reason or request.comment

        # Update comparison result model if present
        comp_result = self.db.query(ComparisonResultModel).filter(
            ComparisonResultModel.plan_id == request.plan_id,
            ComparisonResultModel.requirement_id == request.item_id
        ).first()

        if comp_result:
            comp_result.reviewer_status = new_status
            comp_result.reviewer_id = request.reviewer_id
            comp_result.reviewer_comment = request.comment
            comp_result.override_reason = request.override_reason or request.comment

        # Log immutable audit trail entry
        event_type = "OVERRIDE" if action_upper == "OVERRIDE" else "REVIEWER_ACTION"
        audit_entry = self.audit_service.log_event(
            event_type=event_type,
            user_id=request.reviewer_id,
            entity_type="REQUIREMENT" if comp_result else "MANUAL_REVIEW_ITEM",
            entity_id=request.item_id,
            original_value={"status": old_status, "validator_status": comp_result.result_status if comp_result else None},
            new_value={
                "status": new_status,
                "reviewer_id": request.reviewer_id,
                "comment": request.comment,
                "override_reason": request.override_reason
            },
            reason=request.comment
        )

        self.db.commit()

        return {
            "review_id": review_item.review_id,
            "plan_id": request.plan_id,
            "item_id": request.item_id,
            "validator_result": comp_result.result_status if comp_result else "NEEDS_REVIEW",
            "previous_reviewer_status": old_status,
            "updated_reviewer_status": new_status,
            "updated_status": new_status,
            "reviewer_id": request.reviewer_id,
            "reviewer_comment": request.comment,
            "override_reason": request.override_reason or request.comment,
            "audit_id": audit_entry.audit_id,
            "message": f"Reviewer action '{new_status}' successfully applied and recorded in immutable audit trail."
        }

    def apply_reviewer_override(self, request: ReviewerOverrideRequest) -> Dict[str, Any]:
        """Alias for apply_reviewer_action for backward compatibility."""
        return self.apply_reviewer_action(request)

    def get_audit_trail(self, entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Delegates audit retrieval to AuditService for backward compatibility."""
        return self.audit_service.get_audit_history(entity_id=entity_id)

    def inspect_item(self, plan_id: str, item_id: str) -> Dict[str, Any]:
        """
        Retrieves complete evidence for a reviewer to inspect:
        Expected -> Generated -> Validated -> Decision
        """
        comp = self.db.query(ComparisonResultModel).filter(
            ComparisonResultModel.plan_id == plan_id,
            ComparisonResultModel.requirement_id == item_id
        ).first()

        queue_item = self.db.query(ManualReviewQueueItem).filter(
            ManualReviewQueueItem.plan_id == plan_id,
            ManualReviewQueueItem.item_id == item_id
        ).first()

        if not comp and not queue_item:
            return {"error": f"Item '{item_id}' in plan '{plan_id}' not found."}

        return {
            "plan_id": plan_id,
            "item_id": item_id,
            "requirement_id": comp.requirement_id if comp else item_id,
            "title": comp.expected_behavior if comp else "Flagged Item Inspection",
            "requirement_text": comp.requirement_text if comp else None,
            "is_mandatory": comp.is_mandatory if comp else True,
            "expected_behavior": comp.expected_behavior if comp else None,
            "generated_content": comp.generated_content if comp else None,
            "generated_coverage": comp.generated_coverage if comp else None,
            "source_doc_id": comp.source_doc_id if comp else None,
            "source_version": comp.source_version if comp else None,
            "source_location": comp.source_location if comp else None,
            "validator_result": comp.result_status if comp else "NEEDS_REVIEW",
            "validator_evidence": comp.evidence if comp else (queue_item.evidence_data if queue_item else None),
            "reviewer_status": comp.reviewer_status if comp else (queue_item.status if queue_item else None),
            "reviewer_id": comp.reviewer_id if comp else (queue_item.reviewer_id if queue_item else None),
            "reviewer_comment": comp.reviewer_comment if comp else (queue_item.reviewer_comment if queue_item else None),
            "override_reason": comp.override_reason if comp else (queue_item.override_reason if queue_item else None),
        }

    def get_pending_review_items(self, plan_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns pending items in manual review queue."""
        query = self.db.query(ManualReviewQueueItem).filter(ManualReviewQueueItem.status == "PENDING")
        if plan_id:
            query = query.filter(ManualReviewQueueItem.plan_id == plan_id)

        items = query.all()
        return [
            {
                "review_id": i.review_id,
                "plan_id": i.plan_id,
                "item_id": i.item_id,
                "item_type": i.item_type,
                "flag_type": i.flag_type,
                "evidence_data": i.evidence_data,
                "status": i.status,
                "created_at": i.created_at.isoformat()
            }
            for i in items
        ]
