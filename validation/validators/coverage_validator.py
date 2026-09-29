"""
SkillSprint AI — Coverage Validator
Validates mandatory requirement coverage for a plan against the ground-truth Role Requirement Matrix.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from validation.scoring.coverage import CoverageScorer


class CoverageValidator:
    """Validates mandatory requirement coverage."""

    def __init__(self, db_session: Session):
        self.scorer = CoverageScorer(db_session)

    def validate(self, role_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.scorer.calculate_coverage(role_id, plan_data)
