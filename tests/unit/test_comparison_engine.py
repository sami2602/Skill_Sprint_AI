"""
SkillSprint AI — Unit Tests for Requirement Comparison Engine (Phase 5)
Verifies itemized requirement-level comparison matrix generation (SRS FR-42).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Base, Document, PolicyRequirement, Role, RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum
)
from validation.reports.comparison_engine import RequirementComparisonEngine
from validation.schemas import ComparisonResultStatusEnum


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    doc = Document(
        id=1,
        doc_id="DOC-POL01",
        title="InfoSec Policy",
        category="Security",
        file_path="data/DOC-POL01.pdf",
        file_type=".pdf",
        file_size_bytes=1000,
        version="1.0",
        is_active=True,
        checksum="hash1",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    session.add(doc)
    session.commit()

    req1 = PolicyRequirement(
        id=1,
        requirement_id="REQ-101",
        document_id=1,
        section_ref="SEC-01",
        title="Mandatory Password Rule",
        requirement_text="Password must be strong.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ALL"]
    )
    req2 = PolicyRequirement(
        id=2,
        requirement_id="REQ-102",
        document_id=1,
        section_ref="SEC-02",
        title="Mandatory MFA Rule",
        requirement_text="MFA required.",
        category=RequirementCategoryEnum.MUST_KNOW,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-01"]
    )
    session.add_all([req1, req2])
    session.commit()

    role = Role(id=1, role_id="ROL-01", title="Engineer", department="Eng")
    session.add(role)
    session.commit()

    yield session
    session.close()


def test_comparison_report_generation(db):
    engine = RequirementComparisonEngine(db)
    plan_data = {
        "plan_id": "PLAN-COMP-01",
        "role_id": "ROL-01",
        "modules": [
            {
                "module_id": "MOD-01",
                "title": "Module 1",
                "stage": "Day 1",
                "tasks": [
                    {
                        "task_id": "TSK-01",
                        "title": "Set password",
                        "due_stage": "Day 1",
                        "requirement_mappings": [{"requirement_id": "REQ-101"}]
                    }
                ]
            }
        ]
    }

    report = engine.generate_comparison_report("ROL-01", plan_data)
    assert report.plan_id == "PLAN-COMP-01"
    assert len(report.items) == 2

    item_101 = next(i for i in report.items if i.requirement_id == "REQ-101")
    assert item_101.result_status in [ComparisonResultStatusEnum.COVERED, "COVERED", "MATCH"]

    item_102 = next(i for i in report.items if i.requirement_id == "REQ-102")
    assert item_102.result_status == ComparisonResultStatusEnum.MISSING
