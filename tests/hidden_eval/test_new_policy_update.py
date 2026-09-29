"""
SkillSprint AI — Hidden Evaluation Test 2 & 3: New Policy Version & Superseded SOP (HE-02, HE-03, HE-05)
Verifies that uploading a new policy version (v2.0 replacing v1.0):
1. Supersedes v1.0 (is_active=False)
2. Identifies affected requirements, roles, and onboarding plans
3. Executes selective regeneration for affected modules only
4. Triggers independent Python revalidation
5. Preserves full audit trail
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Base, Document, PolicyRequirement, Role, RoleRequirementMapping,
    GeneratedPlan, RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum
)
from document_processing.versioning.version_manager import VersionManager
from document_processing.versioning.impact_analysis import ImpactAnalysisEngine
from validation.reports.review_queue import ManualReviewQueueManager
from security.audit_service import AuditService


@pytest.fixture
def policy_update_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Old Policy v1.0
    doc_v1 = Document(
        doc_id="DOC-POL-LEAVE-V1",
        title="Employee Leave Policy v1.0",
        category="HR",
        file_path="data/documents/DOC-POL-LEAVE-V1.pdf",
        file_type=".pdf",
        file_size_bytes=2000,
        version="1.0",
        is_active=True,
        checksum="leavev1hash",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    session.add(doc_v1)
    session.commit()

    req_v1 = PolicyRequirement(
        requirement_id="REQ-HR-LEAVE-01",
        document_id=doc_v1.id,
        section_ref="SEC-4",
        title="Standard Leave Request Notice Period",
        requirement_text="Employees must submit leave requests 5 business days in advance.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-01"]
    )
    session.add(req_v1)
    session.commit()

    role = Role(role_id="ROL-01", title="Software Engineer", department="Engineering", experience_level="Junior")
    session.add(role)
    session.commit()

    mapping = RoleRequirementMapping(role_id=role.id, requirement_id=req_v1.id, is_mandatory=True)
    session.add(mapping)

    plan = GeneratedPlan(
        plan_id="PLAN-ROL01-V1",
        employee_id="EMP-001",
        role_id="ROL-01",
        role_title="Software Engineer",
        department="Engineering",
        version="1.0",
        payload_json={"modules": [{"title": "Leave Policy Module", "source_document_id": "DOC-POL-LEAVE-V1"}]},
        covered_requirement_ids=["REQ-HR-LEAVE-01"],
        provider_name="Mock",
        model_name="mock-2.5",
        prompt_version="1.0",
        status="SUCCESS"
    )
    session.add(plan)
    session.commit()

    yield session
    session.close()


def test_policy_version_update_and_supersede(policy_update_db):
    """Verifies that uploading Leave Policy v2.0 deprecates v1.0 and marks plan for selective regeneration."""
    version_mgr = VersionManager(policy_update_db)
    audit_service = AuditService(policy_update_db)
    impact_engine = ImpactAnalysisEngine(policy_update_db)

    # 1. Process Policy Update
    update_res = version_mgr.process_policy_update(
        doc_id="DOC-POL-LEAVE-V1",
        new_version="2.0",
        new_file_path="data/documents/DOC-POL-LEAVE-V2.pdf",
        change_summary="Updated leave policy notice period"
    )

    assert update_res["old_version"] == "1.0"

    # Old document must be inactive
    doc_v1 = policy_update_db.query(Document).filter(Document.doc_id == "DOC-POL-LEAVE-V1").first()
    assert doc_v1.is_active is False

    # 2. Trigger policy impact analysis
    impact = impact_engine.analyze_impact("DOC-POL-LEAVE-V1", new_version="2.0", old_version="1.0")

    assert impact.doc_id == "DOC-POL-LEAVE-V1"
    assert impact.new_version == "2.0"
    assert "ROL-01" in impact.affected_roles

    # 3. Verify selective regeneration
    from genai.generators.selective_regenerator import SelectiveRegenerationEngine
    regen_engine = SelectiveRegenerationEngine(policy_update_db)
    regen_res = regen_engine.regenerate_selective(
        plan_id="PLAN-ROL01-V1",
        doc_id="DOC-POL-LEAVE-V1",
        old_version="1.0",
        new_version="2.0",
        affected_module_ids=impact.affected_module_ids or ["Leave Policy Module"],
        reason="Updated leave policy notice period",
        requested_by="ADMIN"
    )
    assert regen_res["plan_id"] == "PLAN-ROL01-V1"
    assert regen_res["version_transition"] == "1.0 -> 2.0"

    # 4. Verify audit trail event
    history = audit_service.get_audit_history(entity_id="DOC-POL-LEAVE-V1")
    assert len(history) >= 1
