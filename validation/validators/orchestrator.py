"""
SkillSprint AI — Independent Ground-Truth Validation Orchestrator
Orchestrates all independent Python validators, measures performance, generates complete validation evidence, and records audit runs in DB.
"""

import time
import uuid
from typing import Dict, Any, Union
from sqlalchemy.orm import Session

from backend.models.models import ValidationRun
from genai.schemas.generation_schemas import OnboardingPlan
from validation.schemas import ValidationEvidenceSchema, VerificationStatusEnum
from validation.validators.coverage_validator import CoverageValidator
from validation.validators.traceability_validator import TraceabilityValidator
from validation.validators.unsupported_content_validator import UnsupportedContentValidator
from validation.validators.duplicate_validator import DuplicateValidator
from validation.validators.contradiction_validator import ContradictionValidator
from validation.validators.sequence_validator import SequenceValidator
from validation.validators.quiz_validator import QuizValidator
from validation.validators.role_relevance_validator import RoleRelevanceValidator
from validation.rules.decision_engine import VerificationDecisionEngine


class ValidationOrchestrator:
    """
    Independent Python Ground-Truth Validation Engine (Pipeline 2).
    STRICT REQUIREMENT: NO GenAI API calls. Completely deterministic.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.coverage_validator = CoverageValidator(db_session)
        self.traceability_validator = TraceabilityValidator(db_session)
        self.unsupported_validator = UnsupportedContentValidator(db_session)
        self.duplicate_validator = DuplicateValidator()
        self.contradiction_validator = ContradictionValidator(db_session)
        self.sequence_validator = SequenceValidator()
        self.quiz_validator = QuizValidator(db_session)
        self.role_relevance_validator = RoleRelevanceValidator(db_session)
        self.decision_engine = VerificationDecisionEngine()

    def validate_plan(self, plan: Union[OnboardingPlan, Dict[str, Any]]) -> ValidationEvidenceSchema:
        """
        Executes all validators sequentially on the plan data.
        Measures total execution time and constructs ValidationEvidenceSchema.
        """
        start_time = time.perf_counter()

        # Convert Pydantic plan object to dict if necessary
        if isinstance(plan, OnboardingPlan):
            plan_data = plan.model_dump()
        else:
            plan_data = plan

        plan_id = plan_data.get("plan_id", f"PLAN-{uuid.uuid4().hex[:8]}")
        role_id = plan_data.get("role_id", "ROL-01")

        # 1. Coverage Validation
        coverage_res = self.coverage_validator.validate(role_id, plan_data)

        # 2. Traceability Validation
        traceability_res = self.traceability_validator.validate(plan_data)

        # 3. Unsupported Content Validation
        unsupported_items = self.unsupported_validator.validate(plan_data)

        # 4. Duplicate Validation
        duplicate_items = self.duplicate_validator.validate(plan_data)

        # 5. Contradiction & Outdated Source Validation
        contradictions, outdated_sources = self.contradiction_validator.validate(plan_data)

        # 6. Sequence & Prerequisite Validation
        sequence_errors = self.sequence_validator.validate(plan_data)

        # 7. Quiz & Distractor Validation
        quiz_errors = self.quiz_validator.validate(plan_data)

        # 8. Role Relevance Validation
        role_irrelevance_flags = self.role_relevance_validator.validate(role_id, plan_data)

        # Combine evidence into dict for decision engine
        raw_evidence = {
            "plan_id": plan_id,
            "role_id": role_id,
            "mandatory_total": coverage_res["mandatory_total"],
            "mandatory_covered": coverage_res["mandatory_covered"],
            "mandatory_missing": coverage_res["mandatory_missing"],
            "coverage_score": coverage_res["coverage_score"],
            "traceable_items": traceability_res["traceable_items"],
            "untraceable_items": traceability_res["untraceable_items"],
            "traceability_score": traceability_res["traceability_score"],
            "unsupported_items": unsupported_items,
            "duplicate_items": duplicate_items,
            "contradictions": contradictions,
            "outdated_sources": outdated_sources,
            "role_irrelevance_flags": role_irrelevance_flags,
            "sequence_errors": sequence_errors,
            "quiz_errors": quiz_errors
        }

        # 9. Verification Decision
        status = self.decision_engine.decide_status(raw_evidence)
        raw_evidence["verification_status"] = status.value

        # Calculate execution time
        end_time = time.perf_counter()
        execution_time_ms = round((end_time - start_time) * 1000, 2)
        raw_evidence["execution_time_ms"] = execution_time_ms

        # Pydantic schema validation
        evidence_schema = ValidationEvidenceSchema(**raw_evidence)

        # Persist ValidationRun record in database
        run_record = ValidationRun(
            run_id=f"VAL-{uuid.uuid4().hex[:8].upper()}",
            plan_id=plan_id,
            role_id=role_id,
            verification_status=status.value,
            coverage_score=evidence_schema.coverage_score,
            traceability_score=evidence_schema.traceability_score,
            mandatory_total=evidence_schema.mandatory_total,
            mandatory_covered=evidence_schema.mandatory_covered,
            execution_time_ms=execution_time_ms,
            evidence_json=evidence_schema.model_dump()
        )
        self.db.add(run_record)
        self.db.commit()

        return evidence_schema
