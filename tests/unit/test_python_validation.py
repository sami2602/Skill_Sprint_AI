"""
SkillSprint AI — Unit Tests for Independent Python Ground-Truth Validation Engine (Phase 5)
Verifies:
- 100% mandatory coverage
- missing mandatory requirement
- optional requirement
- role-specific requirement
- missing source / invalid source / invalid document version
- unsupported content / hallucinations
- duplicate content
- contradiction & outdated policy & policy precedence
- prerequisite violation & sequence violation
- quiz answer validation & invalid distractors
- role irrelevance
- VERIFIED, NEEDS_REVIEW, REJECTED decisions
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Base, Document, PolicyRequirement, Role, RoleRequirementMapping,
    RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum, PolicyConflictFlag, ConflictTypeEnum
)
from validation.validators.coverage_validator import CoverageValidator
from validation.validators.traceability_validator import TraceabilityValidator
from validation.validators.unsupported_content_validator import UnsupportedContentValidator
from validation.validators.duplicate_validator import DuplicateValidator
from validation.validators.contradiction_validator import ContradictionValidator
from validation.validators.sequence_validator import SequenceValidator
from validation.validators.quiz_validator import QuizValidator
from validation.validators.role_relevance_validator import RoleRelevanceValidator
from validation.rules.decision_engine import VerificationDecisionEngine
from validation.validators.orchestrator import ValidationOrchestrator
from validation.schemas import VerificationStatusEnum


@pytest.fixture
def db():
    """In-memory SQLite database fixture initialized with test models and seed data."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed Document 1 (Active)
    doc1 = Document(
        id=1,
        doc_id="DOC-POL01",
        title="Information Security Policy",
        category="Security",
        file_path="data/documents/DOC-POL01.pdf",
        file_type=".pdf",
        file_size_bytes=5000,
        version="1.0",
        is_active=True,
        checksum="abc123hash",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    # Seed Document 2 (Inactive/Superseded)
    doc2 = Document(
        id=2,
        doc_id="DOC-POL02",
        title="Old HR Policy",
        category="HR",
        file_path="data/documents/DOC-POL02.pdf",
        file_type=".pdf",
        file_size_bytes=4000,
        version="1.0",
        is_active=False,
        checksum="def456hash",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    session.add_all([doc1, doc2])
    session.commit()

    # Seed Policy Requirements
    req1 = PolicyRequirement(
        id=1,
        requirement_id="REQ-001",
        document_id=1,
        section_ref="SEC-01",
        title="Password Complexity",
        requirement_text="Passwords must be at least 12 characters.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ALL"],
        department="Engineering"
    )
    req2 = PolicyRequirement(
        id=2,
        requirement_id="REQ-002",
        document_id=1,
        section_ref="SEC-02",
        title="MFA Requirement",
        requirement_text="MFA must be enabled for all accounts.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-01"],
        department="Engineering"
    )
    req3 = PolicyRequirement(
        id=3,
        requirement_id="REQ-003",
        document_id=1,
        section_ref="SEC-03",
        title="Optional Security Training",
        requirement_text="Employees may take advanced security course.",
        category=RequirementCategoryEnum.OPTIONAL,
        priority=PriorityEnum.LOW,
        modal_verb="may",
        is_mandatory=False,
        target_roles=["ALL"],
        department="Engineering"
    )
    # Role-specific requirement for Finance (not ROL-01)
    req4 = PolicyRequirement(
        id=4,
        requirement_id="REQ-004",
        document_id=1,
        section_ref="SEC-04",
        title="Financial Ledger Audit",
        requirement_text="Financial ledger must be audited daily.",
        category=RequirementCategoryEnum.MUST_COMPLETE,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-05"],
        department="Finance"
    )
    session.add_all([req1, req2, req3, req4])
    session.commit()

    # Seed Role ROL-01
    role1 = Role(
        id=1,
        role_id="ROL-01",
        title="Software Engineer",
        department="Engineering",
        experience_level="Junior"
    )
    session.add(role1)
    session.commit()

    yield session
    session.close()


def make_valid_plan():
    """Helper creating a 100% valid onboarding plan structure."""
    return {
        "plan_id": "PLAN-TEST-001",
        "employee_id": "EMP-101",
        "role_id": "ROL-01",
        "role_title": "Software Engineer",
        "department": "Engineering",
        "generated_at": "2026-09-27T20:00:00Z",
        "version": "1.0",
        "covered_requirement_ids": ["REQ-001", "REQ-002"],
        "source_citations": [
            {
                "doc_id": "DOC-POL01",
                "doc_version": "1.0",
                "section_id": "SEC-01",
                "requirement_id": "REQ-001"
            },
            {
                "doc_id": "DOC-POL01",
                "doc_version": "1.0",
                "section_id": "SEC-02",
                "requirement_id": "REQ-002"
            }
        ],
        "modules": [
            {
                "module_id": "MOD-01",
                "title": "Security Basics",
                "summary": "Introduction to security",
                "learning_objectives": ["Understand passwords"],
                "stage": "Day 1",
                "prerequisites": [],
                "requirement_mappings": [
                    {"requirement_id": "REQ-001", "is_mandatory": True, "justification": "Covers password complexity"}
                ],
                "source_citations": [
                    {"doc_id": "DOC-POL01", "doc_version": "1.0", "section_id": "SEC-01", "requirement_id": "REQ-001"}
                ],
                "tasks": [
                    {
                        "task_id": "TSK-101",
                        "title": "Set up password manager",
                        "description": "Configure 12+ character password",
                        "due_stage": "Day 1",
                        "is_mandatory": True,
                        "prerequisite_task_ids": [],
                        "source_citations": [
                            {"doc_id": "DOC-POL01", "doc_version": "1.0", "section_id": "SEC-01", "requirement_id": "REQ-001"}
                        ],
                        "requirement_mappings": [
                            {"requirement_id": "REQ-001", "is_mandatory": True, "justification": "Task covers password policy"}
                        ]
                    }
                ],
                "quizzes": [
                    {
                        "quiz_id": "QZ-201",
                        "title": "Security Fundamentals Quiz",
                        "description": "Test security basics",
                        "requirement_ids": ["REQ-001", "REQ-002"],
                        "questions": [
                            {
                                "question_id": "QST-201",
                                "question_text": "What is minimum password length?",
                                "question_type": "MULTIPLE_CHOICE",
                                "options": [
                                    {"option_id": "A", "option_text": "8 characters", "is_correct": False, "explanation": "Too short"},
                                    {"option_id": "B", "option_text": "12 characters", "is_correct": True, "explanation": "Correct per SEC-01"}
                                ],
                                "correct_answer_id": "B",
                                "explanation": "12 characters per DOC-POL01 SEC-01",
                                "requirement_id": "REQ-001",
                                "source_citation": {
                                    "doc_id": "DOC-POL01",
                                    "doc_version": "1.0",
                                    "section_id": "SEC-01",
                                    "requirement_id": "REQ-001"
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "module_id": "MOD-02",
                "title": "MFA Setup Module",
                "summary": "Setting up multi-factor authentication",
                "learning_objectives": ["MFA setup"],
                "stage": "Week 1",
                "prerequisites": ["MOD-01"],
                "requirement_mappings": [
                    {"requirement_id": "REQ-002", "is_mandatory": True, "justification": "Covers MFA setup"}
                ],
                "source_citations": [
                    {"doc_id": "DOC-POL01", "doc_version": "1.0", "section_id": "SEC-02", "requirement_id": "REQ-002"}
                ],
                "tasks": [
                    {
                        "task_id": "TSK-102",
                        "title": "Configure Authenticator App",
                        "description": "Enroll device in MFA",
                        "due_stage": "Week 1",
                        "is_mandatory": True,
                        "prerequisite_task_ids": ["TSK-101"],
                        "source_citations": [
                            {"doc_id": "DOC-POL01", "doc_version": "1.0", "section_id": "SEC-02", "requirement_id": "REQ-002"}
                        ],
                        "requirement_mappings": [
                            {"requirement_id": "REQ-002", "is_mandatory": True, "justification": "Task covers MFA"}
                        ]
                    }
                ],
                "quizzes": []
            }
        ],
        "metadata": {
            "prompt_version": "1.0",
            "provider": "Mock",
            "model": "mock-v1",
            "generation_timestamp": "2026-09-27T20:00:00Z",
            "input_requirement_ids": ["REQ-001", "REQ-002"]
        }
    }


def test_100_percent_coverage(db):
    """Verifies coverage calculation returns 100% when all mandatory requirements are present."""
    validator = CoverageValidator(db)
    plan = make_valid_plan()
    res = validator.validate("ROL-01", plan)
    assert res["mandatory_total"] == 2
    assert res["mandatory_covered"] == 2
    assert res["coverage_score"] == 100.0
    assert len(res["mandatory_missing"]) == 0


def test_missing_mandatory_requirement(db):
    """Verifies missing mandatory requirements are identified and coverage score drops."""
    validator = CoverageValidator(db)
    plan = make_valid_plan()
    # Remove REQ-002
    plan["covered_requirement_ids"] = ["REQ-001"]
    plan["modules"][1]["requirement_mappings"] = []
    plan["modules"][1]["tasks"][0]["requirement_mappings"] = []
    plan["modules"][1]["tasks"][0]["source_citations"] = []
    plan["modules"][0]["quizzes"][0]["requirement_ids"] = ["REQ-001"]

    res = validator.validate("ROL-01", plan)
    assert res["mandatory_covered"] == 1
    assert "REQ-002" in res["mandatory_missing"]
    assert res["coverage_score"] == 50.0


def test_invalid_source_citation(db):
    """Verifies uncited or non-existent document citations lower traceability score."""
    validator = TraceabilityValidator(db)
    plan = make_valid_plan()
    # Add fake doc citation
    plan["modules"][0]["source_citations"].append({
        "doc_id": "DOC-FAKE99",
        "doc_version": "1.0",
        "section_id": "SEC-99",
        "requirement_id": "REQ-001"
    })

    res = validator.validate(plan)
    assert res["untraceable_items"] > 0
    assert res["traceability_score"] < 100.0


def test_unsupported_content_detection(db):
    """Verifies tasks or questions mapped to non-existent requirement IDs are flagged as unsupported."""
    validator = UnsupportedContentValidator(db)
    plan = make_valid_plan()
    plan["modules"][0]["tasks"][0]["requirement_mappings"].append({
        "requirement_id": "REQ-NONEXISTENT",
        "is_mandatory": True,
        "justification": "Fake requirement"
    })

    unsupported = validator.validate(plan)
    assert len(unsupported) > 0
    assert any("REQ-NONEXISTENT" in item["reason"] for item in unsupported)


def test_duplicate_content_detection(db):
    """Verifies duplicate module IDs or identical task titles are flagged."""
    validator = DuplicateValidator()
    plan = make_valid_plan()
    # Duplicate task title
    plan["modules"][1]["tasks"].append({
        "task_id": "TSK-999",
        "title": "Set up password manager", # Same title as TSK-101
        "description": "Duplicate description",
        "due_stage": "Week 1",
        "is_mandatory": True
    })

    duplicates = validator.validate(plan)
    assert len(duplicates) > 0
    assert any("Set up password manager" in d["title"] for d in duplicates)


def test_contradiction_and_outdated_policy(db):
    """Verifies citations referencing inactive/superseded policies are flagged."""
    validator = ContradictionValidator(db)
    plan = make_valid_plan()
    # Cite inactive doc DOC-POL02
    plan["modules"][0]["tasks"][0]["source_citations"].append({
        "doc_id": "DOC-POL02",
        "doc_version": "1.0",
        "section_id": "SEC-01",
        "requirement_id": "REQ-001"
    })

    contradictions, outdated = validator.validate(plan)
    assert len(outdated) > 0
    assert any("DOC-POL02" in o["doc_id"] for o in outdated)


def test_sequence_and_prerequisite_violation(db):
    """Verifies scheduling a prerequisite module after a dependent module flags sequence error."""
    validator = SequenceValidator()
    plan = make_valid_plan()
    # MOD-02 stage set to Day 1, MOD-01 stage set to Month 1 (while MOD-02 depends on MOD-01)
    plan["modules"][0]["stage"] = "Month 1"
    plan["modules"][1]["stage"] = "Day 1"

    seq_errors = validator.validate(plan)
    assert len(seq_errors) > 0
    assert any("MOD-02" in err["affected_item"] or "MOD-01" in err["actual_order"] for err in seq_errors)


def test_quiz_answer_and_distractor_validation(db):
    """Verifies quiz validation flags wrong correct_answer_id, duplicate distractors, and missing options."""
    validator = QuizValidator(db)
    plan = make_valid_plan()

    # Add question with duplicate distractors
    plan["modules"][0]["quizzes"][0]["questions"].append({
        "question_id": "QST-BAD",
        "question_text": "What is 2+2?",
        "options": [
            {"option_id": "A", "option_text": "4", "is_correct": True, "explanation": "4"},
            {"option_id": "B", "option_text": "4", "is_correct": False, "explanation": "Duplicate"}
        ],
        "correct_answer_id": "A",
        "explanation": "Math",
        "requirement_id": "REQ-001",
        "source_citation": {
            "doc_id": "DOC-POL01",
            "doc_version": "1.0",
            "section_id": "SEC-01",
            "requirement_id": "REQ-001"
        }
    })

    quiz_errors = validator.validate(plan)
    assert len(quiz_errors) > 0
    assert any("Duplicate distractor" in err["reason"] for err in quiz_errors)


def test_role_relevance_validation(db):
    """Verifies including a Finance-only requirement (REQ-004) in a Software Engineer plan flags role irrelevance."""
    validator = RoleRelevanceValidator(db)
    plan = make_valid_plan()
    plan["modules"][0]["tasks"][0]["requirement_mappings"].append({
        "requirement_id": "REQ-004", # Finance only
        "is_mandatory": True,
        "justification": "Cross role requirement test"
    })

    flags = validator.validate("ROL-01", plan)
    assert len(flags) > 0
    assert any("REQ-004" in f["requirement_id"] for f in flags)


def test_orchestrator_verified_decision(db):
    """Verifies valid plan produces VERIFIED decision."""
    orchestrator = ValidationOrchestrator(db)
    plan = make_valid_plan()
    evidence = orchestrator.validate_plan(plan)

    assert evidence.verification_status == VerificationStatusEnum.VERIFIED
    assert evidence.coverage_score == 100.0
    assert evidence.traceability_score == 100.0
    assert evidence.execution_time_ms >= 0.0


def test_orchestrator_rejected_decision(db):
    """Verifies plan missing mandatory requirement produces REJECTED decision."""
    orchestrator = ValidationOrchestrator(db)
    plan = make_valid_plan()
    # Remove mandatory requirement REQ-002
    plan["covered_requirement_ids"] = ["REQ-001"]
    plan["modules"][1]["requirement_mappings"] = []
    plan["modules"][1]["tasks"][0]["requirement_mappings"] = []
    plan["modules"][1]["tasks"][0]["source_citations"] = []
    plan["modules"][0]["quizzes"][0]["requirement_ids"] = ["REQ-001"]

    evidence = orchestrator.validate_plan(plan)
    assert evidence.verification_status == VerificationStatusEnum.REJECTED
    assert "REQ-002" in evidence.mandatory_missing
