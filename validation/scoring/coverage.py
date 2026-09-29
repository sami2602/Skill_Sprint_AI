"""
SkillSprint AI — Coverage Scoring Calculator
Calculates mandatory requirement coverage statistics deterministically from database Role Requirement Matrix.
"""

from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from knowledge.roles.matrix_builder import RoleMatrixBuilder


class CoverageScorer:
    """Calculates mandatory requirement coverage without GenAI API calls (FR-32, FR-33)."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.matrix_builder = RoleMatrixBuilder(db_session)

    def calculate_coverage(self, role_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates coverage statistics for an onboarding plan against the role matrix.
        Returns:
            {
                "mandatory_total": int,
                "mandatory_covered": int,
                "mandatory_missing": List[str],
                "coverage_score": float,
                "optional_total": int,
                "optional_covered": int
            }
        """
        matrix = self.matrix_builder.build_matrix_for_role(role_id)
        mandatory_req_map = {item["requirement_id"]: item for item in matrix["mandatory_items"]}
        optional_req_map = {item["requirement_id"]: item for item in matrix["optional_items"]}

        # Extract covered requirement IDs from plan
        covered_ids = set()

        # 1. From top-level plan covered_requirement_ids
        top_level_covered = plan_data.get("covered_requirement_ids", [])
        if isinstance(top_level_covered, list):
            covered_ids.update(top_level_covered)

        # 2. Inspect modules, tasks, and quizzes deep
        modules = plan_data.get("modules", [])
        for mod in modules:
            # Module requirement mappings
            for req_map in mod.get("requirement_mappings", []):
                req_id = req_map.get("requirement_id") if isinstance(req_map, dict) else getattr(req_map, "requirement_id", None)
                if req_id:
                    covered_ids.add(req_id)

            # Module tasks
            for task in mod.get("tasks", []):
                for req_map in task.get("requirement_mappings", []):
                    req_id = req_map.get("requirement_id") if isinstance(req_map, dict) else getattr(req_map, "requirement_id", None)
                    if req_id:
                        covered_ids.add(req_id)
                for citation in task.get("source_citations", []):
                    req_id = citation.get("requirement_id") if isinstance(citation, dict) else getattr(citation, "requirement_id", None)
                    if req_id:
                        covered_ids.add(req_id)

            # Module quizzes
            for quiz in mod.get("quizzes", []):
                q_req_ids = quiz.get("requirement_ids", [])
                if isinstance(q_req_ids, list):
                    covered_ids.update(q_req_ids)
                for qst in quiz.get("questions", []):
                    req_id = qst.get("requirement_id") if isinstance(qst, dict) else getattr(qst, "requirement_id", None)
                    if req_id:
                        covered_ids.add(req_id)

        # Compute mandatory stats
        mandatory_total = len(mandatory_req_map)
        covered_mandatory_reqs = [r_id for r_id in mandatory_req_map if r_id in covered_ids]
        missing_mandatory_reqs = [r_id for r_id in mandatory_req_map if r_id not in covered_ids]
        mandatory_covered_count = len(covered_mandatory_reqs)

        if mandatory_total > 0:
            coverage_score = round((mandatory_covered_count / mandatory_total) * 100.0, 2)
        else:
            coverage_score = 100.0

        # Compute optional stats
        optional_total = len(optional_req_map)
        optional_covered_count = sum(1 for r_id in optional_req_map if r_id in covered_ids)

        return {
            "mandatory_total": mandatory_total,
            "mandatory_covered": mandatory_covered_count,
            "mandatory_missing": missing_mandatory_reqs,
            "coverage_score": coverage_score,
            "optional_total": optional_total,
            "optional_covered": optional_covered_count,
            "covered_requirement_ids": sorted(list(covered_ids))
        }
