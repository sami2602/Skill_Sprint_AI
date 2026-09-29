"""
SkillSprint AI — Hidden Evaluation Test 1: Unseen Role Scenario (HE-01)
Verifies that a brand new, unseen role (e.g. Cybersecurity Specialist ROL-11) added dynamically at evaluation time
can be represented, mapped, generated, validated by Python ground-truth engine, and compared without code changes.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Base, Role, Document, PolicyRequirement, RoleRequirementMapping,
    RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum
)
from genai.providers.mock_provider import MockLLMProvider
from genai.generators.plan_generator import OnboardingPlanGenerator
from validation.validators.orchestrator import ValidationOrchestrator
from validation.reports.comparison_engine import RequirementComparisonEngine


@pytest.fixture
def hidden_role_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Create unseen Role dynamically
    new_role = Role(
        role_id="ROL-11",
        title="Cybersecurity Specialist",
        department="Security & Compliance",
        experience_level="Senior",
        description="Responsible for enterprise threat hunting, incident response, and SOC monitoring."
    )
    session.add(new_role)

    # 2. Add source document
    doc = Document(
        doc_id="DOC-SEC-NEW",
        title="Advanced Cybersecurity Operations Policy v1.0",
        category="Security",
        file_path="data/documents/DOC-SEC-NEW.pdf",
        file_type=".pdf",
        file_size_bytes=4000,
        version="1.0",
        is_active=True,
        checksum="sechash111",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    session.add(doc)
    session.commit()

    # 3. Add policy requirement for new role
    req = PolicyRequirement(
        requirement_id="REQ-SEC-099",
        document_id=doc.id,
        section_ref="SEC-3.1",
        title="Enterprise SOC Threat Hunting Protocol",
        requirement_text="Senior Cybersecurity Specialists must complete daily SOC threat hunting triage.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-11"]
    )
    session.add(req)
    session.commit()

    # 4. Map role to requirement
    mapping = RoleRequirementMapping(
        role_id=new_role.id,
        requirement_id=req.id,
        is_mandatory=True
    )
    session.add(mapping)
    session.commit()

    yield session
    session.close()


def test_unseen_role_end_to_end(hidden_role_db):
    """Verifies that ROL-11 (Cybersecurity Specialist) is fully handled dynamically."""
    provider = MockLLMProvider()
    generator = OnboardingPlanGenerator(provider=provider)
    orchestrator = ValidationOrchestrator(hidden_role_db)
    comparison_engine = RequirementComparisonEngine(hidden_role_db)

    # Step 1: Generate plan for unseen role
    plan = generator.generate_plan_for_role(
        db_session=hidden_role_db,
        role_id="ROL-11",
        employee_id="EMP-ROL11-001"
    )

    assert plan is not None
    assert plan.role_id == "ROL-11"
    assert len(plan.modules) > 0

    # Step 2: Validate plan with Python validator
    evidence = orchestrator.validate_plan(plan.model_dump())
    assert evidence is not None
    assert evidence.role_id == "ROL-11"

    # Step 3: Run Itemized Comparison
    report = comparison_engine.generate_comparison_report("ROL-11", plan.model_dump())
    assert report.role_id == "ROL-11"
    assert report.summary["total_evaluated"] >= 1
