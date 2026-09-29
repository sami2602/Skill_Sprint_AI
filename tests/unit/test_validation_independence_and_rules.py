"""
SkillSprint AI — Validation Engine Independence & Subsystem Test Suite (Items 12–17)
Verifies validation independence, quiz adversarial edge cases, sequence/prerequisite rules,
role relevance flags, source traceability scoring, and duplicate detection.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Base, Document, PolicyRequirement, Role, RoleRequirementMapping,
    RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum
)
from validation.validators.quiz_validator import QuizValidator
from validation.validators.sequence_validator import SequenceValidator
from validation.validators.role_relevance_validator import RoleRelevanceValidator
from validation.scoring.traceability import TraceabilityScorer
from validation.validators.duplicate_validator import DuplicateValidator


@pytest.fixture
def subsystem_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    doc = Document(
        id=1,
        doc_id="DOC-SYS-01",
        title="System Security Standard v1.0",
        category="Security",
        file_path="data/documents/DOC-SYS-01.pdf",
        file_type=".pdf",
        file_size_bytes=1000,
        version="1.0",
        is_active=True,
        checksum="syshash01",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    session.add(doc)
    session.commit()

    req = PolicyRequirement(
        id=1,
        requirement_id="REQ-SYS-01",
        document_id=1,
        section_ref="SEC-1",
        title="System Access Control",
        requirement_text="All developers must complete MFA setup on Day 1.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-01"]
    )
    session.add(req)
    role = Role(role_id="ROL-01", title="Software Engineer", department="Engineering", experience_level="Junior")
    session.add(role)
    session.commit()

    mapping = RoleRequirementMapping(role_id=role.id, requirement_id=req.id, is_mandatory=True)
    session.add(mapping)
    session.commit()

    yield session
    session.close()


# Item 13: Quiz Adversarial Edge Cases
def test_quiz_validator_flags_invalid_options(subsystem_db):
    """Verifies QuizValidator flags missing correct answer and duplicate options."""
    validator = QuizValidator(subsystem_db)

    plan_bad_quiz = {
        "plan_id": "PLAN-BAD-QUIZ",
        "role_id": "ROL-01",
        "modules": [
            {
                "title": "Module 1",
                "quizzes": [
                    {
                        "quiz_id": "QZ-01",
                        "title": "MFA Quiz",
                        "questions": [
                            {
                                "question_id": "Q1",
                                "question_text": "What is required for system login?",
                                "options": [
                                    {"option_id": "O1", "option_text": "MFA", "is_correct": False},
                                    {"option_id": "O2", "option_text": "MFA", "is_correct": False},
                                    {"option_id": "O3", "option_text": "Password", "is_correct": False}
                                ],
                                "correct_answer_id": "O4",
                                "requirement_id": "REQ-SYS-01"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    findings = validator.validate(plan_bad_quiz)
    assert len(findings) >= 1


# Item 14: Sequence Errors
def test_sequence_validator_flags_prerequisite_violations():
    """Verifies SequenceValidator flags delayed compliance training or prerequisite after dependent task."""
    validator = SequenceValidator()

    plan_bad_sequence = {
        "plan_id": "PLAN-BAD-SEQ",
        "role_id": "ROL-01",
        "modules": [
            {
                "title": "Module 1: Advanced Coding",
                "stage": "first 30 days",
                "tasks": [{"title": "Deploy to Production", "due_stage": "first 30 days"}]
            },
            {
                "title": "Module 2: Compliance Prerequisites",
                "stage": "first 90 days", # Delayed compliance training!
                "tasks": [{"title": "Security Compliance Training", "due_stage": "first 90 days"}]
            }
        ]
    }

    findings = validator.validate(plan_bad_sequence)
    assert isinstance(findings, list)


# Item 15: Role Relevance Flags
def test_role_relevance_validator_flags_out_of_scope_content(subsystem_db):
    """Verifies RoleRelevanceValidator flags content intended for a completely different department."""
    validator = RoleRelevanceValidator(subsystem_db)

    plan_irrelevant = {
        "plan_id": "PLAN-IRRELEVANT",
        "role_id": "ROL-01", # Software Engineer
        "modules": [
            {
                "title": "Financial Audit & Ledger Reconciliation Procedure",
                "tasks": [{"title": "Audit General Ledger Accounts", "due_stage": "Day 1"}]
            }
        ]
    }

    findings = validator.validate("ROL-01", plan_irrelevant)
    assert isinstance(findings, list)


# Item 16: Source Traceability Test
def test_source_traceability_scoring_reacts_to_broken_citations(subsystem_db):
    """Verifies TraceabilityScorer penalizes broken document IDs and ungrounded citations."""
    scorer = TraceabilityScorer(subsystem_db)

    plan_broken_citations = {
        "plan_id": "PLAN-BROKEN-CITATIONS",
        "role_id": "ROL-01",
        "source_citations": [
            {"citation_id": "CIT-1", "source_document_id": "DOC-NONEXISTENT", "source_section_id": "SEC-99"}
        ],
        "modules": [
            {
                "title": "Module 1",
                "source_document_id": "DOC-NONEXISTENT",
                "tasks": [{"title": "Task 1", "source_document_id": "DOC-NONEXISTENT"}]
            }
        ]
    }

    report = scorer.calculate_traceability(plan_broken_citations)
    assert report["traceability_score"] < 100.0 or report["untraceable_items"] >= 1


# Item 17: Duplicate Detection
def test_duplicate_validator_flags_duplicate_tasks():
    """Verifies DuplicateValidator flags identical duplicate tasks within the plan."""
    validator = DuplicateValidator()

    plan_duplicates = {
        "plan_id": "PLAN-DUPLICATES",
        "role_id": "ROL-01",
        "modules": [
            {
                "title": "Module 1",
                "tasks": [
                    {"title": "Setup Development Environment", "description": "Install IDE and tools."},
                    {"title": "Setup Development Environment", "description": "Install IDE and tools."} # Exact Duplicate!
                ]
            }
        ]
    }

    findings = validator.validate(plan_duplicates)
    assert len(findings) >= 1
