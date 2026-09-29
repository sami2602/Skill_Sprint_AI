"""
SkillSprint AI — Unit Tests for Requirement Taxonomy Classifier
"""

import pytest
from backend.models.models import PolicyRequirement, RequirementCategoryEnum, PriorityEnum
from knowledge.requirements.classifier import RequirementClassifier


def test_classifier_taxonomy_dimensions():
    classifier = RequirementClassifier()

    mand_req = PolicyRequirement(
        requirement_id="REQ-001",
        document_id=1,
        section_ref="SEC-01",
        title="InfoSec Compliance",
        requirement_text="All developers must complete InfoSec compliance procedure.",
        category=RequirementCategoryEnum.MUST_COMPLETE,
        priority=PriorityEnum.HIGH,
        modal_verb="must",
        is_mandatory=True,
        target_roles=["ROL-01", "ROL-02"],
        sub_category="procedural"
    )

    result = classifier.classify_requirement(mand_req)

    assert result["is_mandatory"] is True
    assert result["is_optional"] is False
    assert result["is_role_specific"] is True
    assert result["is_company_wide"] is False
    assert result["is_task_requirement"] is True
    assert result["is_compliance_requirement"] is True
