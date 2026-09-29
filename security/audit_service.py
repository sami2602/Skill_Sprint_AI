"""
SkillSprint AI — Append-Only Immutable Audit Trail Service
Records immutable audit logs for document changes, policy version updates, generation events, validation runs, comparisons, verification decisions, reviewer actions, overrides, and selective regenerations (SRS FR-45).
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models.models import AuditTrail


class AuditService:
    """Manages append-only immutable audit logging across the application."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def log_event(
        self,
        event_type: str,
        user_id: str,
        entity_type: str,
        entity_id: str,
        original_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None
    ) -> AuditTrail:
        """
        Creates and stores an immutable audit log record.
        Supported event types:
        - DOCUMENT_CHANGE
        - POLICY_VERSION_CHANGE
        - GENERATION_EVENT
        - VALIDATION_EVENT
        - COMPARISON_EVENT
        - VERIFICATION_DECISION
        - REVIEWER_ACTION
        - OVERRIDE
        - REGENERATION_EVENT
        """
        audit_entry = AuditTrail(
            audit_id=f"AUD-{uuid.uuid4().hex[:10].upper()}",
            event_type=event_type,
            user_id=user_id or "SYSTEM",
            entity_type=entity_type,
            entity_id=entity_id,
            original_value=original_value,
            new_value=new_value,
            reason=reason,
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(audit_entry)
        self.db.commit()
        self.db.refresh(audit_entry)
        return audit_entry

    def get_audit_history(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieves audit trail entries filtered by parameters in descending chronological order."""
        query = self.db.query(AuditTrail)
        if entity_id:
            query = query.filter(AuditTrail.entity_id == entity_id)
        if entity_type:
            query = query.filter(AuditTrail.entity_type == entity_type)
        if event_type:
            query = query.filter(AuditTrail.event_type == event_type)
        if user_id:
            query = query.filter(AuditTrail.user_id == user_id)

        records = query.order_by(AuditTrail.timestamp.desc()).limit(limit).all()
        return [
            {
                "audit_id": r.audit_id,
                "event_type": r.event_type,
                "user_id": r.user_id,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "original_value": r.original_value,
                "new_value": r.new_value,
                "reason": r.reason,
                "timestamp": r.timestamp.isoformat()
            }
            for r in records
        ]
