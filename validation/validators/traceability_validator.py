"""
SkillSprint AI — Traceability Validator
Validates source provenance and citation accuracy for a plan.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from validation.scoring.traceability import TraceabilityScorer


class TraceabilityValidator:
    """Validates item citations against active policy documents."""

    def __init__(self, db_session: Session):
        self.scorer = TraceabilityScorer(db_session)

    def validate(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.scorer.calculate_traceability(plan_data)
