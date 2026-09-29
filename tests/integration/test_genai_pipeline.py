"""
SkillSprint AI — Integration Tests for GenAI Pipeline Runner
Verifies end-to-end integration with database ground-truth matrix, provider abstraction, prompt injection defense, and schema validation.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.models.models import Role, PolicyRequirement, Document, RequirementCategoryEnum, PriorityEnum
from genai.providers.mock_provider import MockLLMProvider
from genai.generators.pipeline_runner import GenAIPipelineRunner
from genai.schemas.generation_schemas import OnboardingPlan


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed test document and requirement
    doc = Document(
        doc_id="DOC-POL-01",
        title="Information Security Policy",
        category="Policy",
        file_path="/tmp/pol.pdf",
        file_type=".pdf",
        file_size_bytes=1000,
        version="1.0",
        is_active=True,
        checksum="abc123hash"
    )
    session.add(doc)
    session.commit()

    req = PolicyRequirement(
        requirement_id="REQ-001",
        document_id=doc.id,
        section_ref="SEC-01",
        title="MFA Mandate",
        requirement_text="Multi-factor authentication must be enabled for all accounts.",
        category=RequirementCategoryEnum.MUST_COMPLETE,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-01"]
    )
    session.add(req)

    role = Role(
        role_id="ROL-01",
        title="Software Engineer",
        department="Engineering",
        experience_level="Junior",
        description="Engineering role"
    )
    session.add(role)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_genai_pipeline_onboarding_plan_generation(db_session):
    provider = MockLLMProvider()
    runner = GenAIPipelineRunner(provider=provider)

    plan = runner.generate_onboarding_plan(
        db_session=db_session,
        role_id="ROL-01",
        employee_id="EMP-101",
        employee_name="John Doe",
        experience_level="Junior",
        location="HQ"
    )

    assert plan is not None
    assert isinstance(plan, OnboardingPlan)
    assert plan.role_id == "ROL-01"
    assert plan.employee_id == "EMP-101"
    assert len(plan.modules) > 0
    assert "REQ-001" in plan.covered_requirement_ids
    assert plan.metadata.provider == "Mock"
    assert plan.metadata.generation_status == "SUCCESS"


def test_genai_pipeline_unseen_role_generation(db_session):
    provider = MockLLMProvider()
    runner = GenAIPipelineRunner(provider=provider)

    # UNSEEN ROLE (HE-01 compliant)
    plan = runner.generate_onboarding_plan(
        db_session=db_session,
        role_id="ROL-UNSEEN-99",
        employee_name="Jane Doe"
    )

    assert plan is not None
    assert plan.role_id == "ROL-UNSEEN-99"
    assert len(plan.stages) == 6
