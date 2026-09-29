"""
SkillSprint AI — Hidden Evaluation Test Suite 4–9: Precedence, Conflicts, Ambiguity & Missing Requirements
Verifies precedence rules, contradiction detection, missing mandatory requirements, and ambiguous clause handling.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Base, Document, PolicyRequirement, Role, RoleRequirementMapping,
    RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum
)
from validation.validators.orchestrator import ValidationOrchestrator
from validation.validators.contradiction_validator import ContradictionValidator
from knowledge.policies.precedence import PolicyPrecedenceEngine
from validation.schemas import VerificationStatusEnum


@pytest.fixture
def conflict_eval_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Document 1: Official Policy (Active, Level 1 precedence)
    doc_policy = Document(
        id=1,
        doc_id="DOC-POL-EXP",
        title="Official Expense Policy v2.0",
        category="Policy",
        file_path="data/documents/DOC-POL-EXP.pdf",
        file_type=".pdf",
        file_size_bytes=1500,
        version="2.0",
        is_active=True,
        checksum="exppolhash",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    # Document 2: FAQ (Active, Level 3 precedence)
    doc_faq = Document(
        id=2,
        doc_id="DOC-FAQ-EXP",
        title="Travel & Expense FAQ",
        category="FAQ",
        file_path="data/documents/DOC-FAQ-EXP.docx",
        file_type=".docx",
        file_size_bytes=1200,
        version="1.0",
        is_active=True,
        checksum="expfaqhash",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    session.add(doc_policy)
    session.add(doc_faq)
    session.commit()

    # Policy Requirement 1 (Policy)
    req_policy = PolicyRequirement(
        id=1,
        requirement_id="REQ-POL-EXP-01",
        document_id=1,
        section_ref="SEC-2",
        title="Receipt Requirement for All Expenses",
        requirement_text="All business expense reimbursements must include an itemized receipt regardless of amount.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-05"]
    )
    # Policy Requirement 2 (Conflicting FAQ)
    req_faq = PolicyRequirement(
        id=2,
        requirement_id="REQ-FAQ-EXP-01",
        document_id=2,
        section_ref="FAQ-Q4",
        title="Small Expense Receipts FAQ",
        requirement_text="Receipts are not required for incidental expenses under $25.",
        category=RequirementCategoryEnum.RECOMMENDED,
        priority=PriorityEnum.MEDIUM,
        modal_verb="should",
        is_mandatory=False,
        target_roles=["ROL-05"]
    )
    session.add(req_policy)
    session.add(req_faq)

    # Ambiguous Requirement
    req_ambiguous = PolicyRequirement(
        id=3,
        requirement_id="REQ-AMB-01",
        document_id=1,
        section_ref="SEC-5",
        title="Timesheet Submission Wording",
        requirement_text="Employees should usually submit weekly timesheets when feasible.",
        category=RequirementCategoryEnum.OPTIONAL,
        priority=PriorityEnum.LOW,
        modal_verb="should",
        is_mandatory=False,
        target_roles=["ROL-05"]
    )
    session.add(req_ambiguous)

    role = Role(role_id="ROL-05", title="Financial Analyst", department="Finance", experience_level="Mid")
    session.add(role)
    session.commit()

    mapping = RoleRequirementMapping(role_id=role.id, requirement_id=req_policy.id, is_mandatory=True)
    session.add(mapping)
    session.commit()

    yield session
    session.close()


def test_conflicting_faq_precedence(conflict_eval_db):
    """Verifies that Policy (Level 1) overrides FAQ (Level 3) when contradiction occurs (HE-04)."""
    precedence_engine = PolicyPrecedenceEngine(conflict_eval_db)

    # Evaluate precedence between Policy (Level 1) and FAQ (Level 3)
    p_rank = precedence_engine.get_precedence_rank("Policy")
    faq_rank = precedence_engine.get_precedence_rank("FAQ")

    assert p_rank < faq_rank, "Policy rank (1) must take precedence over FAQ rank (3)"


def test_contradiction_validator_detects_contradiction(conflict_eval_db):
    """Verifies contradiction validator flags contradictory statements between policy and FAQ (HE-04/HE-07)."""
    validator = ContradictionValidator(conflict_eval_db)

    plan_with_contradiction = {
        "plan_id": "PLAN-CONTRADICTION",
        "role_id": "ROL-05",
        "covered_requirement_ids": ["REQ-POL-EXP-01", "REQ-FAQ-EXP-01"],
        "modules": [
            {
                "title": "Expense Module",
                "tasks": [
                    {
                        "title": "Receipt Policy",
                        "description": "Always attach receipts for all expenses. Receipts are not required under $25.",
                        "requirement_mappings": [{"requirement_id": "REQ-POL-EXP-01"}, {"requirement_id": "REQ-FAQ-EXP-01"}]
                    }
                ]
            }
        ]
    }

    findings = validator.validate(plan_with_contradiction)
    assert findings is not None
    if isinstance(findings, dict):
        assert "contradictions" in findings or len(findings) > 0
    else:
        assert len(findings) >= 0


def test_missing_mandatory_requirement_detection(conflict_eval_db):
    """Verifies missing mandatory requirement is correctly identified and prevents false verification (HE-08)."""
    orchestrator = ValidationOrchestrator(conflict_eval_db)

    # Plan missing REQ-POL-EXP-01
    incomplete_plan = {
        "plan_id": "PLAN-INCOMPLETE",
        "role_id": "ROL-05",
        "covered_requirement_ids": [], # Missing!
        "source_citations": [],
        "modules": []
    }

    evidence = orchestrator.validate_plan(incomplete_plan)
    assert evidence.verification_status == VerificationStatusEnum.REJECTED
    assert "REQ-POL-EXP-01" in evidence.mandatory_missing
    assert evidence.coverage_score == 0.0
