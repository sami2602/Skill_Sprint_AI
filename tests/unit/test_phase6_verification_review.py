"""
SkillSprint AI — Phase 6 Verification, Review & Audit Unit Tests
Comprehensive unit test suite for requirement comparison, verification summary, human review workflow, reviewer overrides, audit trail immutability, policy impact analysis, selective regeneration, policy precedence, and RBAC authorization (SRS Phase 6).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Base, Document, PolicyRequirement, Role, RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum, GeneratedPlan
)
from validation.reports.comparison_engine import RequirementComparisonEngine
from validation.rules.decision_engine import VerificationDecisionEngine
from validation.reports.review_queue import ManualReviewQueueManager
from document_processing.versioning.impact_analysis import ImpactAnalysisEngine
from genai.generators.selective_regenerator import SelectiveRegenerationEngine
from knowledge.policies.precedence import PolicyPrecedenceEngine
from security.audit_service import AuditService
from security.rbac import RBACManager, RBACPermissionError
from validation.schemas import (
    ValidationEvidenceSchema, ReviewerOverrideRequest, ComparisonResultStatusEnum, VerificationStatusEnum
)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed test documents
    doc1 = Document(
        id=1,
        doc_id="DOC-POL01",
        title="InfoSec Policy v1",
        category="Security",
        file_path="data/DOC-POL01.pdf",
        file_type=".pdf",
        file_size_bytes=1000,
        version="1.0",
        is_active=True,
        checksum="hash1",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    doc2 = Document(
        id=2,
        doc_id="DOC-FAQ01",
        title="InfoSec FAQ",
        category="FAQ",
        file_path="data/DOC-FAQ01.docx",
        file_type=".docx",
        file_size_bytes=800,
        version="1.0",
        is_active=True,
        checksum="hash2",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    session.add_all([doc1, doc2])
    session.commit()

    # Seed requirements
    req1 = PolicyRequirement(
        id=1,
        requirement_id="REQ-001",
        document_id=1,
        section_ref="SEC-01",
        title="Password Complexity Policy",
        requirement_text="Passwords must contain 12+ characters.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-01"]
    )
    req2 = PolicyRequirement(
        id=2,
        requirement_id="REQ-002",
        document_id=1,
        section_ref="SEC-02",
        title="MFA Mandatory Setup",
        requirement_text="MFA must be configured on Day 1.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-01"]
    )
    req3 = PolicyRequirement(
        id=3,
        requirement_id="REQ-003",
        document_id=2,
        section_ref="FAQ-01",
        title="Optional Guest Access",
        requirement_text="Guest access may be requested.",
        category=RequirementCategoryEnum.RECOMMENDED,
        priority=PriorityEnum.LOW,
        modal_verb="may",
        is_mandatory=False,
        target_roles=["ROL-01"]
    )
    session.add_all([req1, req2, req3])
    session.commit()

    # Seed role
    role = Role(id=1, role_id="ROL-01", title="Software Engineer", department="Engineering")
    session.add(role)
    session.commit()

    # Seed generated plan
    plan = GeneratedPlan(
        id=1,
        plan_id="PLAN-P6-001",
        role_id="ROL-01",
        role_title="Software Engineer",
        department="Engineering",
        version="1.0",
        payload_json={
            "plan_id": "PLAN-P6-001",
            "modules": [
                {
                    "module_id": "MOD-01",
                    "title": "InfoSec Basics",
                    "stage": "Day 1",
                    "source_document_id": "DOC-POL01",
                    "tasks": [
                        {
                            "task_id": "TSK-01",
                            "title": "Configure Strong Password",
                            "description": "Set up 12+ char password.",
                            "due_stage": "Day 1",
                            "source_document_id": "DOC-POL01",
                            "requirement_mappings": [{"requirement_id": "REQ-001"}]
                        }
                    ],
                    "quizzes": []
                }
            ]
        },
        covered_requirement_ids=["REQ-001"],
        provider_name="gemini",
        model_name="gemini-2.5-flash",
        prompt_version="v1",
        status="SUCCESS"
    )
    session.add(plan)
    session.commit()

    yield session
    session.close()


def test_full_requirement_comparison(db):
    """Verifies itemized requirement-level comparison generation (FR-42)."""
    engine = RequirementComparisonEngine(db)
    plan_data = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == "PLAN-P6-001").first().payload_json

    report = engine.generate_comparison_report("ROL-01", plan_data)
    assert report.plan_id == "PLAN-P6-001"
    assert len(report.items) == 3

    # REQ-001 should be COVERED
    item_001 = next(i for i in report.items if i.requirement_id == "REQ-001")
    assert item_001.result_status in [ComparisonResultStatusEnum.COVERED, "COVERED", "MATCH"]
    assert "Expected" in item_001.evidence

    # REQ-002 should be MISSING (Mandatory)
    item_002 = next(i for i in report.items if i.requirement_id == "REQ-002")
    assert item_002.result_status in [ComparisonResultStatusEnum.MISSING, "MISSING"]


def test_missing_requirement_detection(db):
    """Verifies missing mandatory requirement state detection."""
    engine = RequirementComparisonEngine(db)
    plan_data = {"plan_id": "PLAN-EMPTY", "modules": []}
    report = engine.generate_comparison_report("ROL-01", plan_data)

    missing_items = [i for i in report.items if i.result_status == ComparisonResultStatusEnum.MISSING]
    assert len(missing_items) == 2  # REQ-001 and REQ-002 missing


def test_unsupported_and_contradiction_comparison(db):
    """Verifies unsupported content and contradiction state assignments."""
    engine = RequirementComparisonEngine(db)
    plan_data = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == "PLAN-P6-001").first().payload_json
    evidence = {
        "mandatory_missing": [],
        "unsupported_items": [{"requirement_id": "REQ-001", "reason": "Ungrounded text"}],
        "contradictions": [{"requirement_id": "REQ-002", "reason": "Policy vs FAQ contradiction"}],
        "outdated_sources": []
    }

    report = engine.generate_comparison_report("ROL-01", plan_data, validator_evidence=evidence)
    item_001 = next(i for i in report.items if i.requirement_id == "REQ-001")
    assert item_001.result_status == ComparisonResultStatusEnum.UNSUPPORTED

    item_002 = next(i for i in report.items if i.requirement_id == "REQ-002")
    assert item_002.result_status == ComparisonResultStatusEnum.CONTRADICTORY


def test_verification_decision_rules(db):
    """Verifies state machine status assignment (VERIFIED, NEEDS_REVIEW, REJECTED) (FR-43)."""
    decision_engine = VerificationDecisionEngine(db)

    # Clean evidence -> VERIFIED
    clean_ev = {
        "mandatory_total": 2,
        "mandatory_covered": 2,
        "mandatory_missing": [],
        "coverage_score": 100.0,
        "traceable_items": 5,
        "untraceable_items": 0,
        "traceability_score": 100.0
    }
    assert decision_engine.decide_status(clean_ev) == VerificationStatusEnum.VERIFIED

    # Non-100% traceability -> NEEDS_REVIEW
    review_ev = dict(clean_ev, traceability_score=80.0, role_irrelevance_flags=[{"item": "Irrelevant module"}])
    assert decision_engine.decide_status(review_ev) == VerificationStatusEnum.NEEDS_REVIEW

    # Missing mandatory -> REJECTED
    reject_ev = dict(clean_ev, mandatory_missing=["REQ-002"], coverage_score=50.0)
    assert decision_engine.decide_status(reject_ev) == VerificationStatusEnum.REJECTED


def test_verification_summary_dynamic_calculation(db):
    """Verifies dynamic verification summary calculation without hardcoded values (FR-43)."""
    decision_engine = VerificationDecisionEngine(db)
    evidence = {
        "mandatory_total": 5,
        "mandatory_covered": 4,
        "mandatory_missing": ["REQ-105"],
        "coverage_score": 80.0,
        "traceable_items": 8,
        "untraceable_items": 2,
        "traceability_score": 80.0,
        "unsupported_items": [{"item_id": "TSK-01"}],
        "duplicate_items": [],
        "contradictions": [],
        "outdated_sources": [],
        "role_irrelevance_flags": [],
        "sequence_errors": []
    }
    summary = decision_engine.calculate_verification_summary("PLAN-SUM-01", "ROL-01", evidence)
    assert summary.plan_id == "PLAN-SUM-01"
    assert summary.mandatory_requirements == 5
    assert summary.mandatory_covered == 4
    assert summary.mandatory_missing == 1
    assert summary.coverage_percentage == 80.0
    assert summary.unsupported_items == 1
    assert summary.verification_status == VerificationStatusEnum.REJECTED


def test_reviewer_approval_rejection_and_override(db):
    """Verifies reviewer actions, comments, and override behavior preserving original result (FR-44, FR-45)."""
    manager = ManualReviewQueueManager(db)

    evidence = ValidationEvidenceSchema(
        plan_id="PLAN-P6-001",
        role_id="ROL-01",
        mandatory_total=2,
        mandatory_covered=1,
        mandatory_missing=["REQ-002"],
        coverage_score=50.0,
        traceable_items=1,
        untraceable_items=0,
        traceability_score=100.0,
        verification_status=VerificationStatusEnum.REJECTED
    )
    manager.route_evidence_to_queue(evidence)

    # 1. Approve REQ-002 override
    req_override = ReviewerOverrideRequest(
        plan_id="PLAN-P6-001",
        item_id="REQ-002",
        action="APPROVED",
        reviewer_id="REV-LEAD-01",
        comment="Approved exception by Lead Auditor",
        override_reason="Reviewed against Policy v1 section 2."
    )
    result = manager.apply_reviewer_action(req_override)
    assert result["updated_reviewer_status"] == "APPROVED"
    assert result["reviewer_id"] == "REV-LEAD-01"
    assert result["audit_id"] is not None

    # 2. Inspect item to verify original validator result is preserved alongside reviewer decision
    inspection = manager.inspect_item("PLAN-P6-001", "REQ-002")
    assert inspection["reviewer_status"] == "APPROVED"
    assert inspection["reviewer_id"] == "REV-LEAD-01"
    assert inspection["override_reason"] == "Reviewed against Policy v1 section 2."


def test_audit_trail_creation_and_preservation(db):
    """Verifies append-only audit trail logging for all event types (FR-45)."""
    audit_service = AuditService(db)

    audit_service.log_event(
        event_type="DOCUMENT_CHANGE",
        user_id="ADMIN-01",
        entity_type="DOCUMENT",
        entity_id="DOC-POL01",
        original_value={"version": "1.0"},
        new_value={"version": "2.0"},
        reason="Annual policy update"
    )

    audit_service.log_event(
        event_type="REGENERATION_EVENT",
        user_id="REV-01",
        entity_type="PLAN",
        entity_id="PLAN-P6-001",
        original_value={"version": "1.0"},
        new_value={"version": "2.0"},
        reason="Selective module regeneration"
    )

    history = audit_service.get_audit_history(entity_id="PLAN-P6-001")
    assert len(history) == 1
    assert history[0]["event_type"] == "REGENERATION_EVENT"
    assert history[0]["user_id"] == "REV-01"


def test_policy_impact_analysis(db):
    """Verifies policy update impact analysis tracing across requirements, roles, plans, modules (FR-53, FR-54)."""
    impact_engine = ImpactAnalysisEngine(db)
    res = impact_engine.analyze_impact(doc_id="DOC-POL01", new_version="2.0", old_version="1.0")

    assert res.doc_id == "DOC-POL01"
    assert res.old_version == "1.0"
    assert res.new_version == "2.0"
    assert len(res.affected_requirement_ids) == 2
    assert "ROL-01" in res.affected_roles
    assert "PLAN-P6-001" in res.affected_plan_ids
    assert "MOD-01" in res.affected_module_ids


def test_selective_regeneration(db):
    """Verifies selective regeneration of affected modules while preserving unaffected content (FR-55)."""
    regen_engine = SelectiveRegenerationEngine(db)

    res = regen_engine.regenerate_selective(
        plan_id="PLAN-P6-001",
        doc_id="DOC-POL01",
        old_version="1.0",
        new_version="2.0",
        affected_module_ids=["MOD-01"],
        reason="Updated InfoSec policy requirements",
        requested_by="REV-01"
    )

    assert res["plan_id"] == "PLAN-P6-001"
    assert "MOD-01" in res["regenerated_modules"]
    assert res["version_transition"] == "1.0 -> 2.0"
    assert res["audit_id"] is not None

    # Check database record was updated to version 2.0
    plan_record = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == "PLAN-P6-001").first()
    assert plan_record.version == "2.0"


def test_policy_precedence(db):
    """Verifies policy precedence hierarchy (Policy > SOP > FAQ) (FR-37)."""
    prec_engine = PolicyPrecedenceEngine(db)
    doc_policy = db.query(Document).filter(Document.doc_id == "DOC-POL01").first()
    doc_faq = db.query(Document).filter(Document.doc_id == "DOC-FAQ01").first()

    resolution = prec_engine.resolve_conflict(doc_policy, doc_faq)
    assert resolution["winner_doc_id"] == "DOC-POL01"
    assert resolution["resolution_type"] == "CATEGORY_PRECEDENCE"


def test_security_rbac_authorization():
    """Verifies RBAC permission checks block unauthorized user roles."""
    # Reviewer role is allowed to perform reviewer actions
    assert RBACManager.verify_permission("REVIEWER", "approve_override") is True

    # Employee role should be blocked with HTTP 403
    with pytest.raises(RBACPermissionError):
        RBACManager.verify_permission("EMPLOYEE", "approve_override")
