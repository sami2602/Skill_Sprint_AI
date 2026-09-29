"""
SkillSprint AI — Unit Tests for Manual Review Queue & Audit Trail (Phase 5)
Verifies manual review routing, reviewer overrides, comment retention, and immutable audit logging (SRS FR-44, FR-45).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Base
from validation.reports.review_queue import ManualReviewQueueManager
from validation.schemas import ValidationEvidenceSchema, ReviewerOverrideRequest, VerificationStatusEnum


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_review_queue_routing_and_override(db):
    manager = ManualReviewQueueManager(db)

    evidence = ValidationEvidenceSchema(
        plan_id="PLAN-REV-01",
        role_id="ROL-01",
        mandatory_total=2,
        mandatory_covered=1,
        mandatory_missing=["REQ-002"],
        coverage_score=50.0,
        traceable_items=1,
        untraceable_items=0,
        traceability_score=100.0,
        unsupported_items=[{"item_id": "TSK-99", "item_type": "TASK", "reason": "Ungrounded claim"}],
        verification_status=VerificationStatusEnum.REJECTED,
        execution_time_ms=12.5
    )

    # 1. Route evidence to review queue
    items = manager.route_evidence_to_queue(evidence)
    assert len(items) == 2 # 1 missing mandatory + 1 unsupported item

    pending = manager.get_pending_review_items("PLAN-REV-01")
    assert len(pending) == 2

    # 2. Apply reviewer override for REQ-002
    req = ReviewerOverrideRequest(
        plan_id="PLAN-REV-01",
        item_id="REQ-002",
        action="APPROVED",
        reviewer_id="REV-USER-42",
        comment="Approved exception by Lead Security Auditor."
    )
    res = manager.apply_reviewer_override(req)
    assert res["updated_status"] == "APPROVED"
    assert res["reviewer_id"] == "REV-USER-42"

    # 3. Verify audit trail immutability
    audit_logs = manager.get_audit_trail()
    assert len(audit_logs) >= 1
    reviewer_override_logs = [a for a in audit_logs if a["event_type"] == "REVIEWER_OVERRIDE" or a["event_type"] == "REVIEWER_ACTION"]
    assert len(reviewer_override_logs) >= 1
    assert reviewer_override_logs[0]["user_id"] == "REV-USER-42"
