"""
SkillSprint AI — Verification Decision Engine
Determines final verification status (VERIFIED, NEEDS_REVIEW, REJECTED) and generates complete VerificationSummary dynamically based on validator evidence (SRS FR-43).
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from validation.schemas import VerificationStatusEnum, VerificationSummarySchema
from security.audit_service import AuditService


class VerificationDecisionEngine:
    """State machine evaluating validator evidence into a deterministic verification decision (FR-43)."""

    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.audit_service = AuditService(db_session) if db_session else None

    def decide_status(self, evidence: Dict[str, Any]) -> VerificationStatusEnum:
        """
        Evaluates evidence metrics and returns VerificationStatusEnum.
        Rules:
        - VERIFIED: 100% mandatory coverage, 100% traceability, 0 unsupported, 0 contradictions, 0 sequence errors, 0 quiz errors, 0 role irrelevancies.
        - NEEDS_REVIEW: 100% mandatory coverage, but has minor duplicate content, non-100% traceability, or role irrelevance warnings.
        - REJECTED: Missing mandatory requirements (<100% coverage), ungrounded claims, direct policy contradictions, outdated sources, sequence errors, or quiz errors.
        """
        coverage_score = evidence.get("coverage_score", 0.0)
        traceability_score = evidence.get("traceability_score", 0.0)
        mandatory_missing = evidence.get("mandatory_missing", [])
        unsupported_items = evidence.get("unsupported_items", [])
        contradictions = evidence.get("contradictions", [])
        outdated_sources = evidence.get("outdated_sources", [])
        sequence_errors = evidence.get("sequence_errors", [])
        quiz_errors = evidence.get("quiz_errors", [])
        role_irrelevance_flags = evidence.get("role_irrelevance_flags", [])
        duplicate_items = evidence.get("duplicate_items", [])

        # Critical rejection criteria
        if (
            len(mandatory_missing) > 0 or
            coverage_score < 100.0 or
            len(unsupported_items) > 0 or
            len(contradictions) > 0 or
            len(outdated_sources) > 0 or
            len(sequence_errors) > 0 or
            len(quiz_errors) > 0
        ):
            return VerificationStatusEnum.REJECTED

        # Major non-critical warning criteria -> NEEDS_REVIEW
        if (
            traceability_score < 100.0 or
            len(role_irrelevance_flags) > 0 or
            len(duplicate_items) > 0
        ):
            return VerificationStatusEnum.NEEDS_REVIEW

        # All criteria satisfied -> VERIFIED
        return VerificationStatusEnum.VERIFIED

    def calculate_verification_summary(
        self,
        plan_id: str,
        role_id: str,
        evidence: Dict[str, Any]
    ) -> VerificationSummarySchema:
        """
        Calculates exact numeric values for all verification metrics dynamically (FR-43).
        No hardcoded metrics.
        """
        status = self.decide_status(evidence)
        explanation = self.get_status_explanation(status, evidence)

        mandatory_total = evidence.get("mandatory_total", 0)
        mandatory_covered = evidence.get("mandatory_covered", 0)
        mandatory_missing_list = evidence.get("mandatory_missing", [])
        mandatory_missing = len(mandatory_missing_list)
        coverage_score = evidence.get("coverage_score", 0.0)

        traceable_items = evidence.get("traceable_items", 0)
        untraceable_items = evidence.get("untraceable_items", 0)
        traceability_score = evidence.get("traceability_score", 0.0)

        unsupported_count = len(evidence.get("unsupported_items", []))
        duplicate_count = len(evidence.get("duplicate_items", []))
        contradiction_count = len(evidence.get("contradictions", []))
        outdated_count = len(evidence.get("outdated_sources", []))
        irrelevance_count = len(evidence.get("role_irrelevance_flags", []))
        sequence_error_count = len(evidence.get("sequence_errors", []))

        total_reqs = mandatory_total + len(evidence.get("optional_items", [])) if "optional_items" in evidence else mandatory_total

        summary = VerificationSummarySchema(
            plan_id=plan_id,
            role_id=role_id,
            total_requirements=total_reqs,
            mandatory_requirements=mandatory_total,
            mandatory_covered=mandatory_covered,
            mandatory_missing=mandatory_missing,
            coverage_percentage=coverage_score,
            traceable_items=traceable_items,
            untraceable_items=untraceable_items,
            traceability_percentage=traceability_score,
            unsupported_items=unsupported_count,
            duplicate_items=duplicate_count,
            contradictions=contradiction_count,
            outdated_sources=outdated_count,
            role_irrelevance=irrelevance_count,
            sequence_errors=sequence_error_count,
            verification_status=status,
            explanation=explanation
        )

        if self.audit_service:
            self.audit_service.log_event(
                event_type="VERIFICATION_DECISION",
                user_id="SYSTEM",
                entity_type="PLAN",
                entity_id=plan_id,
                original_value=None,
                new_value={"status": status.value, "coverage": coverage_score, "traceability": traceability_score},
                reason=explanation
            )

        return summary

    def get_status_explanation(self, status: VerificationStatusEnum, evidence: Dict[str, Any]) -> str:
        """Provides detailed text explanation for assigned verification decision."""
        if status == VerificationStatusEnum.VERIFIED:
            return "100% Mandatory Coverage satisfied. All content items grounded in active policy sources with zero sequence, contradiction, or quiz errors."
        elif status == VerificationStatusEnum.NEEDS_REVIEW:
            reasons = []
            if evidence.get("traceability_score", 100.0) < 100.0:
                reasons.append(f"Traceability score is {evidence.get('traceability_score')}%.")
            if len(evidence.get("duplicate_items", [])) > 0:
                reasons.append(f"{len(evidence['duplicate_items'])} duplicate content items detected.")
            if len(evidence.get("role_irrelevance_flags", [])) > 0:
                reasons.append(f"{len(evidence['role_irrelevance_flags'])} role irrelevance flags detected.")
            return "Plan requires manual review: " + "; ".join(reasons)
        else: # REJECTED
            reasons = []
            if len(evidence.get("mandatory_missing", [])) > 0:
                reasons.append(f"Missing mandatory requirements: {evidence.get('mandatory_missing')}.")
            if len(evidence.get("unsupported_items", [])) > 0:
                reasons.append(f"{len(evidence['unsupported_items'])} ungrounded/hallucinated items detected.")
            if len(evidence.get("contradictions", [])) > 0:
                reasons.append(f"{len(evidence['contradictions'])} policy contradictions detected.")
            if len(evidence.get("outdated_sources", [])) > 0:
                reasons.append(f"{len(evidence['outdated_sources'])} outdated/superseded source references detected.")
            if len(evidence.get("sequence_errors", [])) > 0:
                reasons.append(f"{len(evidence['sequence_errors'])} sequence/prerequisite errors detected.")
            if len(evidence.get("quiz_errors", [])) > 0:
                reasons.append(f"{len(evidence['quiz_errors'])} quiz structure or answer validation errors detected.")
            return "Plan REJECTED: " + "; ".join(reasons)
