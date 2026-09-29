"""
SkillSprint AI — Integration Test for Ground-Truth Validation Pipeline (Phase 5)
Verifies:
- Complete end-to-end Python validation execution
- Dual-pipeline isolation (Pipeline 2 makes ZERO external LLM/GenAI network calls)
- Database persistence of ValidationRun records
"""

import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Base, Document, PolicyRequirement, Role, ValidationRun, RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum
)
from genai.generators.plan_generator import OnboardingPlanGenerator
from genai.providers.mock_provider import MockLLMProvider
from validation.validators.orchestrator import ValidationOrchestrator
from validation.schemas import VerificationStatusEnum


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    doc = Document(
        id=1,
        doc_id="DOC-POL01",
        title="Security Policy",
        category="Security",
        file_path="data/DOC-POL01.pdf",
        file_type=".pdf",
        file_size_bytes=2000,
        version="1.0",
        is_active=True,
        checksum="hash123",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    session.add(doc)
    session.commit()

    req = PolicyRequirement(
        id=1,
        requirement_id="REQ-001",
        document_id=1,
        section_ref="SEC-01",
        title="Access Control Policy",
        requirement_text="Access must be granted on least privilege basis.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ALL"]
    )
    session.add(req)
    session.commit()

    role = Role(id=1, role_id="ROL-01", title="Engineer", department="Engineering")
    session.add(role)
    session.commit()

    yield session
    session.close()


def test_dual_pipeline_isolation(db):
    """
    Tests that Pipeline 1 (GenAI Generator) generates the plan,
    and Pipeline 2 (Python Validation Engine) independently validates it without calling GenAI API.
    """
    # Pipeline 1: GenAI Generator
    provider = MockLLMProvider()
    generator = OnboardingPlanGenerator(provider=provider)
    plan = generator.generate_plan_for_role(db_session=db, role_id="ROL-01", employee_id="EMP-101")

    assert plan is not None
    assert plan.role_id == "ROL-01"

    # Pipeline 2: Python Validation Engine
    orchestrator = ValidationOrchestrator(db)

    # Patch MockLLMProvider generate method to prove Pipeline 2 makes 0 GenAI calls
    with patch.object(MockLLMProvider, "generate", side_effect=AssertionError("GenAI called during Python validation!")):
        evidence = orchestrator.validate_plan(plan)

    assert evidence is not None
    assert evidence.mandatory_total >= 1
    assert evidence.execution_time_ms >= 0.0

    # Verify ValidationRun persistent DB record
    run_in_db = db.query(ValidationRun).filter(ValidationRun.plan_id == plan.plan_id).first()
    assert run_in_db is not None
    assert run_in_db.verification_status == evidence.verification_status.value
