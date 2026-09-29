"""
SkillSprint AI — Policy Precedence Engine
Enforces configurable precedence hierarchy (Latest Approved Policy > Department SOP > FAQ > Informal Guidance).
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.models import PolicyPrecedenceRule, Document


class PolicyPrecedenceEngine:
    """Evaluates precedence between conflicting policy documents and requirements (FR-37)."""

    DEFAULT_RULES = [
        {"doc_category": "Policy", "precedence_rank": 1, "description": "Official company policies (Highest Precedence)"},
        {"doc_category": "Security", "precedence_rank": 1, "description": "Official security & compliance policies"},
        {"doc_category": "Compliance", "precedence_rank": 1, "description": "Legal & regulatory compliance policies"},
        {"doc_category": "HR", "precedence_rank": 1, "description": "Official HR policies"},
        {"doc_category": "SOP", "precedence_rank": 2, "description": "Departmental Standard Operating Procedures"},
        {"doc_category": "FAQ", "precedence_rank": 3, "description": "Frequently Asked Questions documents"},
        {"doc_category": "Informal Guidance", "precedence_rank": 4, "description": "Informal guidelines or notes (Lowest Precedence)"}
    ]

    def __init__(self, db_session: Session):
        self.db = db_session
        self._ensure_default_rules()

    def _ensure_default_rules(self):
        """Initializes default precedence rules in database if empty."""
        existing = self.db.query(PolicyPrecedenceRule).count()
        if existing == 0:
            for rule in self.DEFAULT_RULES:
                p_rule = PolicyPrecedenceRule(
                    doc_category=rule["doc_category"],
                    precedence_rank=rule["precedence_rank"],
                    description=rule["description"]
                )
                self.db.add(p_rule)
            self.db.commit()

    def get_precedence_rank(self, category: str) -> int:
        """Returns numeric precedence rank for a document category (lower number = higher precedence)."""
        rule = self.db.query(PolicyPrecedenceRule).filter(
            PolicyPrecedenceRule.doc_category.ilike(category)
        ).first()
        if rule:
            return rule.precedence_rank
        # Default fallback ranks
        category_lower = category.lower()
        if "policy" in category_lower or "security" in category_lower: return 1
        if "sop" in category_lower: return 2
        if "faq" in category_lower: return 3
        return 4

    def resolve_conflict(
        self,
        doc_1: Document,
        doc_2: Document,
        req_1_text: str = "",
        req_2_text: str = ""
    ) -> Dict[str, Any]:
        """
        Resolves conflict between two documents/requirements using configurable precedence:
        1. Compare active vs superseded status.
        2. Compare category rank (Policy > SOP > FAQ > Informal).
        3. Compare version numbers if same category.
        """
        # Active vs Superseded check
        if doc_1.is_active and not doc_2.is_active:
            return {
                "winner_doc_id": doc_1.doc_id,
                "winner_category": doc_1.category,
                "loser_doc_id": doc_2.doc_id,
                "loser_category": doc_2.category,
                "reason": f"Active policy version ({doc_1.doc_id} v{doc_1.version}) supersedes obsolete version ({doc_2.doc_id} v{doc_2.version}).",
                "resolution_type": "ACTIVE_VERSION_OVERRIDE"
            }
        elif doc_2.is_active and not doc_1.is_active:
            return {
                "winner_doc_id": doc_2.doc_id,
                "winner_category": doc_2.category,
                "loser_doc_id": doc_1.doc_id,
                "loser_category": doc_1.category,
                "reason": f"Active policy version ({doc_2.doc_id} v{doc_2.version}) supersedes obsolete version ({doc_1.doc_id} v{doc_1.version}).",
                "resolution_type": "ACTIVE_VERSION_OVERRIDE"
            }

        # Category Rank check
        rank_1 = self.get_precedence_rank(doc_1.category)
        rank_2 = self.get_precedence_rank(doc_2.category)

        if rank_1 < rank_2:
            return {
                "winner_doc_id": doc_1.doc_id,
                "winner_category": doc_1.category,
                "loser_doc_id": doc_2.doc_id,
                "loser_category": doc_2.category,
                "reason": f"Precedence Rule: {doc_1.category} (Rank {rank_1}) > {doc_2.category} (Rank {rank_2}).",
                "resolution_type": "CATEGORY_PRECEDENCE"
            }
        elif rank_2 < rank_1:
            return {
                "winner_doc_id": doc_2.doc_id,
                "winner_category": doc_2.category,
                "loser_doc_id": doc_1.doc_id,
                "loser_category": doc_1.category,
                "reason": f"Precedence Rule: {doc_2.category} (Rank {rank_2}) > {doc_1.category} (Rank {rank_1}).",
                "resolution_type": "CATEGORY_PRECEDENCE"
            }

        # Version Comparison check if same rank
        try:
            v1_float = float(doc_1.version.replace("v", ""))
            v2_float = float(doc_2.version.replace("v", ""))
            if v1_float > v2_float:
                return {
                    "winner_doc_id": doc_1.doc_id,
                    "winner_category": doc_1.category,
                    "loser_doc_id": doc_2.doc_id,
                    "loser_category": doc_2.category,
                    "reason": f"Higher version number: {doc_1.doc_id} (v{doc_1.version}) > {doc_2.doc_id} (v{doc_2.version}).",
                    "resolution_type": "VERSION_PRECEDENCE"
                }
            elif v2_float > v1_float:
                return {
                    "winner_doc_id": doc_2.doc_id,
                    "winner_category": doc_2.category,
                    "loser_doc_id": doc_1.doc_id,
                    "loser_category": doc_1.category,
                    "reason": f"Higher version number: {doc_2.doc_id} (v{doc_2.version}) > {doc_1.doc_id} (v{doc_1.version}).",
                    "resolution_type": "VERSION_PRECEDENCE"
                }
        except ValueError:
            pass

        return {
            "winner_doc_id": doc_1.doc_id,
            "winner_category": doc_1.category,
            "loser_doc_id": doc_2.doc_id,
            "loser_category": doc_2.category,
            "reason": f"Equal precedence rank ({rank_1}). Manual reviewer decision required.",
            "resolution_type": "MANUAL_REVIEW_REQUIRED"
        }
