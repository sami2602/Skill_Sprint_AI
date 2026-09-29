"""
SkillSprint AI — Traceability Scoring Calculator
Verifies source citations against stored database documents, sections, and active versions deterministically.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.models import Document, PolicyRequirement


class TraceabilityScorer:
    """Calculates traceability score for generated onboarding plans (FR-30, FR-34)."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def calculate_traceability(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates traceability score by auditing source citations across modules, tasks, and quizzes.
        Returns:
            {
                "traceable_items": int,
                "untraceable_items": int,
                "traceability_score": float,
                "untraceable_details": List[Dict[str, Any]],
                "outdated_sources": List[Dict[str, Any]]
            }
        """
        # Load active documents and requirements mapping into memory for fast deterministic checking
        active_docs = {d.doc_id: d for d in self.db.query(Document).filter(Document.is_active == True).all()}
        all_docs = {d.doc_id: d for d in self.db.query(Document).all()}
        all_reqs = {r.requirement_id: r for r in self.db.query(PolicyRequirement).all()}

        citations_to_check: List[Dict[str, Any]] = []

        # Gather citations from plan top-level
        for cit in plan_data.get("source_citations", []):
            citations_to_check.append({
                "context": "PLAN_CITATION",
                "citation": cit
            })

        # Gather citations from modules, tasks, quizzes
        modules = plan_data.get("modules", [])
        for mod in modules:
            mod_id = mod.get("module_id", "UNKNOWN_MOD")
            for cit in mod.get("source_citations", []):
                citations_to_check.append({
                    "context": f"MODULE ({mod_id})",
                    "citation": cit
                })
            for task in mod.get("tasks", []):
                task_id = task.get("task_id", "UNKNOWN_TSK")
                for cit in task.get("source_citations", []):
                    citations_to_check.append({
                        "context": f"TASK ({task_id})",
                        "citation": cit
                    })
            for quiz in mod.get("quizzes", []):
                quiz_id = quiz.get("quiz_id", "UNKNOWN_QZ")
                for qst in quiz.get("questions", []):
                    qst_id = qst.get("question_id", "UNKNOWN_QST")
                    cit = qst.get("source_citation")
                    if cit:
                        citations_to_check.append({
                            "context": f"QUIZ_QUESTION ({quiz_id}/{qst_id})",
                            "citation": cit
                        })

        if not citations_to_check:
            return {
                "traceable_items": 0,
                "untraceable_items": 0,
                "traceability_score": 100.0,
                "untraceable_details": [],
                "outdated_sources": []
            }

        traceable_count = 0
        untraceable_count = 0
        untraceable_details = []
        outdated_sources = []

        for item in citations_to_check:
            ctx = item["context"]
            cit = item["citation"]

            doc_id = cit.get("doc_id") if isinstance(cit, dict) else getattr(cit, "doc_id", None)
            doc_version = cit.get("doc_version") if isinstance(cit, dict) else getattr(cit, "doc_version", None)
            section_id = cit.get("section_id") if isinstance(cit, dict) else getattr(cit, "section_id", None)
            req_id = cit.get("requirement_id") if isinstance(cit, dict) else getattr(cit, "requirement_id", None)
            page_num = cit.get("page_number") if isinstance(cit, dict) else getattr(cit, "page_number", None)
            para_ref = cit.get("paragraph_ref") if isinstance(cit, dict) else getattr(cit, "paragraph_ref", None)

            is_valid = True
            reasons = []

            # 1. Requirement ID exists check
            if not req_id or req_id not in all_reqs:
                is_valid = False
                reasons.append(f"Requirement ID '{req_id}' does not exist in policy matrix.")

            # 2. Document exists check
            if not doc_id or doc_id not in all_docs:
                is_valid = False
                reasons.append(f"Source document ID '{doc_id}' does not exist in database.")
            else:
                doc = all_docs[doc_id]
                # 3. Active document version check
                if not doc.is_active:
                    is_valid = False
                    reasons.append(f"Document '{doc_id}' is obsolete/superseded (active version is {active_docs.get(doc_id, doc).version}).")
                    outdated_sources.append({
                        "context": ctx,
                        "doc_id": doc_id,
                        "cited_version": doc_version,
                        "active_version": doc.version,
                        "reason": f"Cited version {doc_version} of {doc_id} is inactive."
                    })
                elif doc_version and str(doc.version) != str(doc_version):
                    is_valid = False
                    reasons.append(f"Document '{doc_id}' version mismatch: cited v{doc_version} vs active v{doc.version}.")
                    outdated_sources.append({
                        "context": ctx,
                        "doc_id": doc_id,
                        "cited_version": doc_version,
                        "active_version": doc.version,
                        "reason": f"Version mismatch: cited v{doc_version} vs active v{doc.version}."
                    })

                # 4. Location ref check
                if not section_id and not page_num and not para_ref:
                    is_valid = False
                    reasons.append(f"No section, page, or paragraph reference provided for document '{doc_id}'.")

                # 5. Requirement-Document correspondence check
                if req_id in all_reqs:
                    db_req = all_reqs[req_id]
                    if db_req.document_id != doc.id:
                        is_valid = False
                        reasons.append(f"Requirement '{req_id}' belongs to document ID {db_req.document_id}, not cited '{doc_id}'.")

            if is_valid:
                traceable_count += 1
            else:
                untraceable_count += 1
                untraceable_details.append({
                    "context": ctx,
                    "requirement_id": req_id,
                    "doc_id": doc_id,
                    "cited_version": doc_version,
                    "reasons": reasons
                })

        total_candidates = traceable_count + untraceable_count
        score = round((traceable_count / total_candidates) * 100.0, 2) if total_candidates > 0 else 100.0

        return {
            "traceable_items": traceable_count,
            "untraceable_items": untraceable_count,
            "traceability_score": score,
            "untraceable_details": untraceable_details,
            "outdated_sources": outdated_sources
        }
