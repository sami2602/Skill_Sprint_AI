"""
SkillSprint AI — Unsupported Content (Hallucination) Validator
Detects generated claims, tasks, modules, or quiz answers that are ungrounded or lack backing in the Role Requirement Matrix and approved documents.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.models import PolicyRequirement, Document


class UnsupportedContentValidator:
    """Detects ungrounded generated claims and hallucinations (FR-31, FR-35)."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def validate(self, plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans all modules, tasks, and quizzes in the plan.
        Returns a list of unsupported item flags:
            [
                {
                    "item_id": str,
                    "item_type": str, # TASK, MODULE, QUIZ_QUESTION
                    "title": str,
                    "reason": str,
                    "evidence": str
                }
            ]
        """
        # Active requirements and active document maps
        active_docs = {d.id: d for d in self.db.query(Document).filter(Document.is_active == True).all()}
        all_reqs = {r.requirement_id: r for r in self.db.query(PolicyRequirement).all()}

        unsupported_items: List[Dict[str, Any]] = []

        modules = plan_data.get("modules", [])
        for mod in modules:
            mod_id = mod.get("module_id", "MOD-UNKNOWN")
            mod_title = mod.get("title", "Untitled Module")

            # Check module requirement mappings
            req_mappings = mod.get("requirement_mappings", [])
            for rm in req_mappings:
                req_id = rm.get("requirement_id") if isinstance(rm, dict) else getattr(rm, "requirement_id", None)
                if req_id and req_id not in all_reqs:
                    unsupported_items.append({
                        "item_id": mod_id,
                        "item_type": "MODULE",
                        "title": mod_title,
                        "reason": f"Module maps to non-existent requirement ID '{req_id}'.",
                        "evidence": f"Requirement '{req_id}' does not exist in company database."
                    })

            # Check tasks
            for task in mod.get("tasks", []):
                task_id = task.get("task_id", "TSK-UNKNOWN")
                task_title = task.get("title", "Untitled Task")
                task_reqs = task.get("requirement_mappings", [])
                task_cits = task.get("source_citations", [])

                if not task_reqs and not task_cits and task.get("is_mandatory", True):
                    unsupported_items.append({
                        "item_id": task_id,
                        "item_type": "TASK",
                        "title": task_title,
                        "reason": f"Mandatory task '{task_title}' has no requirement mappings or source citations.",
                        "evidence": "Mandatory content must be anchored to a policy requirement and source document."
                    })

                for rm in task_reqs:
                    req_id = rm.get("requirement_id") if isinstance(rm, dict) else getattr(rm, "requirement_id", None)
                    if req_id and req_id not in all_reqs:
                        unsupported_items.append({
                            "item_id": task_id,
                            "item_type": "TASK",
                            "title": task_title,
                            "reason": f"Task maps to non-existent requirement ID '{req_id}'.",
                            "evidence": f"Requirement '{req_id}' does not exist in company database."
                        })

                for cit in task_cits:
                    doc_id = cit.get("doc_id") if isinstance(cit, dict) else getattr(cit, "doc_id", None)
                    req_id = cit.get("requirement_id") if isinstance(cit, dict) else getattr(cit, "requirement_id", None)

                    if req_id and req_id not in all_reqs:
                        unsupported_items.append({
                            "item_id": task_id,
                            "item_type": "TASK",
                            "title": task_title,
                            "reason": f"Task citation references invalid requirement ID '{req_id}'.",
                            "evidence": f"Requirement '{req_id}' is missing from requirement matrix."
                        })

            # Check quizzes
            for quiz in mod.get("quizzes", []):
                quiz_id = quiz.get("quiz_id", "QZ-UNKNOWN")

                for qst in quiz.get("questions", []):
                    qst_id = qst.get("question_id", "QST-UNKNOWN")
                    q_req_id = qst.get("requirement_id") if isinstance(qst, dict) else getattr(qst, "requirement_id", None)
                    cit = qst.get("source_citation")

                    if not q_req_id or q_req_id not in all_reqs:
                        unsupported_items.append({
                            "item_id": f"{quiz_id}/{qst_id}",
                            "item_type": "QUIZ_QUESTION",
                            "title": qst.get("question_text", "Untitled Question")[:60],
                            "reason": f"Quiz question references ungrounded requirement ID '{q_req_id}'.",
                            "evidence": f"Requirement '{q_req_id}' not found in database."
                        })

                    if not cit:
                        unsupported_items.append({
                            "item_id": f"{quiz_id}/{qst_id}",
                            "item_type": "QUIZ_QUESTION",
                            "title": qst.get("question_text", "Untitled Question")[:60],
                            "reason": "Quiz question lacks source policy citation.",
                            "evidence": "Every quiz question must be grounded in an official policy citation."
                        })

        return unsupported_items
