"""
SkillSprint AI — Requirement Taxonomy Classifier
Classifies policy requirements across 9 dimensions required by SRS v1.0.
"""

from typing import List, Dict, Any
from backend.models.models import PolicyRequirement, RequirementCategoryEnum


class RequirementClassifier:
    """Classifies requirement entities across all 9 SRS taxonomy dimensions."""

    def classify_requirement(self, req: PolicyRequirement) -> Dict[str, Any]:
        """
        Returns full classification dictionary for a given requirement entity.
        """
        is_mandatory = req.is_mandatory or req.category in [
            RequirementCategoryEnum.MUST_KNOW,
            RequirementCategoryEnum.MUST_COMPLETE,
            RequirementCategoryEnum.MUST_DEMONSTRATE,
            RequirementCategoryEnum.MUST_ACKNOWLEDGE
        ]

        target_roles = req.target_roles or ["ALL"]
        is_company_wide = "ALL" in target_roles or len(target_roles) == 0
        is_role_specific = not is_company_wide

        text_lower = (req.requirement_text or "").lower()
        sub_cat = getattr(req, "sub_category", "policy")

        # Sub-category taxonomy determination
        is_procedural = "procedure" in text_lower or "sop" in text_lower or "step" in text_lower
        is_knowledge = req.category == RequirementCategoryEnum.MUST_KNOW or "understand" in text_lower
        is_task = req.category == RequirementCategoryEnum.MUST_COMPLETE or "complete" in text_lower or "submit" in text_lower
        is_compliance = "compliance" in text_lower or "regulation" in text_lower or "audit" in text_lower or "infosec" in text_lower
        is_policy = not (is_procedural or is_task)

        return {
            "requirement_id": req.requirement_id,
            "is_mandatory": is_mandatory,
            "is_optional": not is_mandatory,
            "is_role_specific": is_role_specific,
            "is_company_wide": is_company_wide,
            "is_policy_requirement": is_policy,
            "is_procedural_requirement": is_procedural,
            "is_knowledge_requirement": is_knowledge,
            "is_task_requirement": is_task,
            "is_compliance_requirement": is_compliance,
            "target_roles": target_roles
        }

    def summarize_taxonomy(self, requirements: List[PolicyRequirement]) -> Dict[str, int]:
        """Aggregates taxonomy metrics for a dataset of requirements."""
        summary = {
            "total_requirements": len(requirements),
            "mandatory_count": 0,
            "optional_count": 0,
            "role_specific_count": 0,
            "company_wide_count": 0,
            "policy_count": 0,
            "procedural_count": 0,
            "knowledge_count": 0,
            "task_count": 0,
            "compliance_count": 0
        }

        for req in requirements:
            classified = self.classify_requirement(req)
            if classified["is_mandatory"]: summary["mandatory_count"] += 1
            else: summary["optional_count"] += 1

            if classified["is_role_specific"]: summary["role_specific_count"] += 1
            else: summary["company_wide_count"] += 1

            if classified["is_policy_requirement"]: summary["policy_count"] += 1
            if classified["is_procedural_requirement"]: summary["procedural_count"] += 1
            if classified["is_knowledge_requirement"]: summary["knowledge_count"] += 1
            if classified["is_task_requirement"]: summary["task_count"] += 1
            if classified["is_compliance_requirement"]: summary["compliance_count"] += 1

        return summary
