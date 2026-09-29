"""
SkillSprint AI — Phase 6 Complete End-to-End Integration Test
Executes complete backend pipeline using actual project data:
Company Documents -> Requirements -> Role Matrix -> GenAI Output -> Python Validation -> Comparison -> Verification -> Human Review -> Approved Result -> Audit Record.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.models import Base, GeneratedPlan
from scripts.seed_dataset import seed_database
from knowledge.roles.matrix_builder import RoleMatrixBuilder
from genai.generators.plan_generator import OnboardingPlanGenerator
from genai.providers.mock_provider import MockLLMProvider
from validation.validators.orchestrator import ValidationOrchestrator
from validation.reports.comparison_engine import RequirementComparisonEngine
from validation.rules.decision_engine import VerificationDecisionEngine
from validation.reports.review_queue import ManualReviewQueueManager
from document_processing.versioning.impact_analysis import ImpactAnalysisEngine
from genai.generators.selective_regenerator import SelectiveRegenerationEngine
from security.audit_service import AuditService
from validation.schemas import ReviewerOverrideRequest, VerificationStatusEnum


@pytest.fixture
def seeded_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed actual project dataset into memory DB
    seed_database(session)
    yield session
    session.close()


def test_phase6_end_to_end_backend_pipeline(seeded_db):
    """
    Executes full Phase 6 integration pipeline:
    1. Company Documents -> Extracted Requirements -> Ground-Truth Role Matrix
    2. GenAI Output Generation
    3. Independent Python Validation Engine
    4. Requirement-Level Comparison Engine
    5. Dynamic Verification Summary
    6. Human Review Workflow & Reviewer Override
    7. Policy Impact Analysis
    8. Selective Regeneration
    9. Immutable Audit Log Verification
    """
    role_id = "ROL-01"

    # Step 1: Verify Role Matrix built from actual dataset requirements
    matrix_builder = RoleMatrixBuilder(seeded_db)
    matrix = matrix_builder.build_matrix_for_role(role_id)
    assert len(matrix["mandatory_items"]) > 0

    # Step 2: Generate Onboarding Plan via GenAI Plan Generator
    provider = MockLLMProvider()
    plan_generator = OnboardingPlanGenerator(provider=provider)
    plan = plan_generator.generate_plan_for_role(
        db_session=seeded_db,
        role_id=role_id,
        employee_id="EMP-TEST-E2E",
        employee_name="Jane Doe"
    )
    assert plan.plan_id is not None
    assert len(plan.modules) > 0

    plan_dict = plan.model_dump()

    # Save GeneratedPlan record to database
    db_plan = GeneratedPlan(
        plan_id=plan.plan_id,
        role_id=role_id,
        role_title="Software Engineer",
        department="Engineering",
        version="1.0",
        payload_json=plan_dict,
        covered_requirement_ids=plan.covered_requirement_ids or [],
        provider_name="mock",
        model_name="mock",
        prompt_version="v1",
        status="SUCCESS"
    )
    seeded_db.add(db_plan)
    seeded_db.commit()

    # Step 3: Run Independent Python Validator (NO GenAI API calls)
    validator = ValidationOrchestrator(seeded_db)
    evidence = validator.validate_plan(plan_dict)
    assert evidence.coverage_score >= 0.0

    # Step 4: Run Requirement-Level Comparison Engine
    comparator = RequirementComparisonEngine(seeded_db)
    comp_report = comparator.generate_comparison_report(
        role_id=role_id,
        plan_data=plan_dict,
        validator_evidence=evidence.model_dump()
    )
    assert comp_report.plan_id == plan.plan_id
    assert len(comp_report.items) >= len(matrix["mandatory_items"])

    # Step 5: Dynamic Verification Decision Engine
    decision_engine = VerificationDecisionEngine(seeded_db)
    summary = decision_engine.calculate_verification_summary(
        plan_id=plan.plan_id,
        role_id=role_id,
        evidence=evidence.model_dump()
    )
    assert summary.verification_status in [
        VerificationStatusEnum.VERIFIED,
        VerificationStatusEnum.NEEDS_REVIEW,
        VerificationStatusEnum.REJECTED
    ]

    # Step 6: Route to Manual Review Queue and apply Reviewer Override
    review_manager = ManualReviewQueueManager(seeded_db)
    routed_items = review_manager.route_evidence_to_queue(evidence)
    
    # Apply Reviewer Override for first item or test requirement
    target_req_id = comp_report.items[0].requirement_id
    override_req = ReviewerOverrideRequest(
        plan_id=plan.plan_id,
        item_id=target_req_id,
        action="APPROVED",
        reviewer_id="REV-E2E-CHIEF",
        comment="E2E manual verification override against policy v1.0",
        override_reason="Audited and approved by Chief Security Officer"
    )
    override_res = review_manager.apply_reviewer_action(override_req)
    assert override_res["updated_reviewer_status"] == "APPROVED"
    assert override_res["reviewer_id"] == "REV-E2E-CHIEF"

    # Step 7: Execute Policy Update Impact Analysis
    doc_id = comp_report.items[0].source_doc_id
    impact_engine = ImpactAnalysisEngine(seeded_db)
    impact_res = impact_engine.analyze_impact(doc_id=doc_id, new_version="2.0", old_version="1.0")
    assert impact_res.doc_id == doc_id
    assert len(impact_res.affected_requirement_ids) > 0

    # Step 8: Execute Selective Regeneration for affected modules
    regen_engine = SelectiveRegenerationEngine(seeded_db)
    affected_mods = impact_res.affected_module_ids or ["MOD-01"]
    regen_res = regen_engine.regenerate_selective(
        plan_id=plan.plan_id,
        doc_id=doc_id,
        old_version="1.0",
        new_version="2.0",
        affected_module_ids=affected_mods,
        reason="Selective update following Policy v2.0 update",
        requested_by="REV-E2E-CHIEF"
    )
    assert regen_res["plan_id"] == plan.plan_id
    assert regen_res["version_transition"] == "1.0 -> 2.0"

    # Step 9: Verify Immutable Audit Trail Records
    audit_service = AuditService(seeded_db)
    audit_history = audit_service.get_audit_history(entity_id=plan.plan_id)
    assert len(audit_history) >= 2
    event_types = [a["event_type"] for a in audit_history]
    assert "REGENERATION_EVENT" in event_types
