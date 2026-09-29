"""
SkillSprint AI — Conflict & Ambiguity Detection Engine
Detects contradictions, outdated sources, ambiguous clauses, duplicate requirements, and superseded policies.
(Does NOT silently swallow conflicts; persists full evidence in policy_conflict_flags table).
"""

import hashlib
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.models import (
    PolicyRequirement, Document, PolicyConflictFlag, ConflictTypeEnum
)
from knowledge.policies.precedence import PolicyPrecedenceEngine


class ConflictResolver:
    """Detects, logs, and resolves document/requirement conflicts (FR-36, HE-04, HE-05, HE-09)."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.precedence_engine = PolicyPrecedenceEngine(db_session)

    def scan_for_conflicts(self) -> Dict[str, Any]:
        """
        Executes full conflict scan across stored requirements and documents.
        Returns aggregate conflict summary counts.
        """
        contradictions = self._detect_contradictions()
        outdated_sources = self._detect_outdated_sources()
        ambiguous_clauses = self._detect_ambiguous_clauses()
        duplicates = self._detect_duplicate_requirements()
        superseded = self._detect_superseded_policies()

        total_conflicts = (
            len(contradictions) +
            len(outdated_sources) +
            len(ambiguous_clauses) +
            len(duplicates) +
            len(superseded)
        )

        return {
            "total_conflicts": total_conflicts,
            "contradictions_count": len(contradictions),
            "outdated_sources_count": len(outdated_sources),
            "ambiguous_clauses_count": len(ambiguous_clauses),
            "duplicate_requirements_count": len(duplicates),
            "superseded_policies_count": len(superseded),
            "conflict_records": contradictions + outdated_sources + ambiguous_clauses + duplicates + superseded
        }

    def _detect_contradictions(self) -> List[Dict[str, Any]]:
        """Detects contradicting rules between official Policies and FAQs/SOPs (e.g. Travel receipts required vs not required)."""
        conflicts = []

        # Query FAQ documents vs Policy documents
        faq_docs = self.db.query(Document).filter(Document.category == "FAQ").all()
        policy_docs = self.db.query(Document).filter(Document.category.in_(["Security", "Finance", "Policy", "Compliance"])).all()

        faq_ids = [d.id for d in faq_docs]
        policy_ids = [d.id for d in policy_docs]

        faq_reqs = self.db.query(PolicyRequirement).filter(PolicyRequirement.document_id.in_(faq_ids)).all() if faq_ids else []
        policy_reqs = self.db.query(PolicyRequirement).filter(PolicyRequirement.document_id.in_(policy_ids)).all() if policy_ids else []

        doc_map = {d.id: d for d in faq_docs + policy_docs}

        # Check for opposing keywords (e.g., 'not required' in FAQ vs 'required' in Policy)
        for freq in faq_reqs:
            f_text = (freq.requirement_text or "").lower()
            for preq in policy_reqs:
                p_text = (preq.requirement_text or "").lower()
                
                # Check keyword overlap in same topic (e.g., expense, receipt, travel)
                common_topics = set(f_text.split()) & set(p_text.split()) & {"expense", "receipt", "travel", "reimbursement", "passport"}
                if common_topics:
                    if ("not" in f_text or "don't" in f_text) != ("not" in p_text or "don't" in p_text):
                        c_id = f"CNF-CONTRAD-{freq.requirement_id}-{preq.requirement_id}"
                        
                        f_doc = doc_map.get(freq.document_id)
                        p_doc = doc_map.get(preq.document_id)
                        
                        res = self.precedence_engine.resolve_conflict(p_doc, f_doc) if (p_doc and f_doc) else {"reason": "Policy > FAQ"}

                        conflict_record = {
                            "conflict_id": c_id,
                            "conflict_type": ConflictTypeEnum.CONTRADICTION,
                            "requirement_id_1": preq.requirement_id,
                            "requirement_id_2": freq.requirement_id,
                            "doc_id_1": p_doc.doc_id if p_doc else "DOC-POL",
                            "doc_id_2": f_doc.doc_id if f_doc else "DOC-FAQ",
                            "section_ref_1": preq.section_ref,
                            "section_ref_2": freq.section_ref,
                            "description": f"Contradiction detected on topic '{list(common_topics)[0]}': Policy ({preq.requirement_id}) vs FAQ ({freq.requirement_id}). {res.get('reason')}",
                            "resolution_status": "RESOLVED_BY_PRECEDENCE" if "winner_doc_id" in res else "UNRESOLVED"
                        }
                        conflicts.append(conflict_record)
                        self._save_conflict_flag(conflict_record)

        return conflicts

    def _detect_outdated_sources(self) -> List[Dict[str, Any]]:
        """Identifies requirements referencing inactive or obsolete policy documents (HE-05)."""
        inactive_docs = self.db.query(Document).filter(Document.is_active == False).all()
        inactive_ids = [d.id for d in inactive_docs]

        if not inactive_ids:
            return []

        outdated_reqs = self.db.query(PolicyRequirement).filter(PolicyRequirement.document_id.in_(inactive_ids)).all()
        conflicts = []

        for req in outdated_reqs:
            doc = next((d for d in inactive_docs if d.id == req.document_id), None)
            doc_code = doc.doc_id if doc else f"DOC-{req.document_id}"
            c_id = f"CNF-OUTDATED-{req.requirement_id}"

            conflict_record = {
                "conflict_id": c_id,
                "conflict_type": ConflictTypeEnum.OUTDATED_SOURCE,
                "requirement_id_1": req.requirement_id,
                "requirement_id_2": None,
                "doc_id_1": doc_code,
                "doc_id_2": None,
                "section_ref_1": req.section_ref,
                "section_ref_2": None,
                "description": f"Outdated Source Referenced: Requirement {req.requirement_id} belongs to obsolete document version {doc_code} (v{doc.version if doc else '1.0'}).",
                "resolution_status": "UNRESOLVED"
            }
            conflicts.append(conflict_record)
            self._save_conflict_flag(conflict_record)

        return conflicts

    def _detect_ambiguous_clauses(self) -> List[Dict[str, Any]]:
        """Flags requirements with ambiguous modal verbs like 'should', 'normally', 'usually' (HE-09)."""
        ambiguous_reqs = self.db.query(PolicyRequirement).filter(
            PolicyRequirement.modal_verb.in_(["should", "advised", "encouraged", "usually", "normally"])
        ).all()

        conflicts = []
        for req in ambiguous_reqs:
            doc = self.db.query(Document).filter(Document.id == req.document_id).first()
            doc_code = doc.doc_id if doc else f"DOC-{req.document_id}"
            c_id = f"CNF-AMBIG-{req.requirement_id}"

            conflict_record = {
                "conflict_id": c_id,
                "conflict_type": ConflictTypeEnum.AMBIGUOUS_CLAUSE,
                "requirement_id_1": req.requirement_id,
                "requirement_id_2": None,
                "doc_id_1": doc_code,
                "doc_id_2": None,
                "section_ref_1": req.section_ref,
                "section_ref_2": None,
                "description": f"Ambiguous Clause Detected: Requirement {req.requirement_id} uses ambiguous modal verb '{req.modal_verb}'.",
                "resolution_status": "REVIEWER_ATTENTION_REQUIRED"
            }
            conflicts.append(conflict_record)
            self._save_conflict_flag(conflict_record)

        return conflicts

    def _detect_duplicate_requirements(self) -> List[Dict[str, Any]]:
        """Identifies substantially duplicate requirements across documents (FR-38)."""
        all_reqs = self.db.query(PolicyRequirement).all()
        seen_texts = {}
        conflicts = []

        for req in all_reqs:
            text_hash = hashlib.md5((req.requirement_text or "").strip().lower().encode("utf-8")).hexdigest()
            if text_hash in seen_texts:
                prev_req = seen_texts[text_hash]
                c_id = f"CNF-DUP-{prev_req.requirement_id}-{req.requirement_id}"
                
                doc_1 = self.db.query(Document).filter(Document.id == prev_req.document_id).first()
                doc_2 = self.db.query(Document).filter(Document.id == req.document_id).first()

                conflict_record = {
                    "conflict_id": c_id,
                    "conflict_type": ConflictTypeEnum.DUPLICATE_REQUIREMENT,
                    "requirement_id_1": prev_req.requirement_id,
                    "requirement_id_2": req.requirement_id,
                    "doc_id_1": doc_1.doc_id if doc_1 else "DOC-1",
                    "doc_id_2": doc_2.doc_id if doc_2 else "DOC-2",
                    "section_ref_1": prev_req.section_ref,
                    "section_ref_2": req.section_ref,
                    "description": f"Duplicate Requirement Detected: '{prev_req.requirement_id}' and '{req.requirement_id}' have identical content text.",
                    "resolution_status": "DUPLICATE_FLAGGED"
                }
                conflicts.append(conflict_record)
                self._save_conflict_flag(conflict_record)
            else:
                seen_texts[text_hash] = req

        return conflicts

    def _detect_superseded_policies(self) -> List[Dict[str, Any]]:
        """Flags superseded document versions."""
        inactive_docs = self.db.query(Document).filter(Document.is_active == False).all()
        conflicts = []

        for doc in inactive_docs:
            c_id = f"CNF-SUPERSEDE-{doc.doc_id}"
            conflict_record = {
                "conflict_id": c_id,
                "conflict_type": ConflictTypeEnum.SUPERSEDED_POLICY,
                "requirement_id_1": f"DOC-{doc.doc_id}",
                "requirement_id_2": None,
                "doc_id_1": doc.doc_id,
                "doc_id_2": None,
                "section_ref_1": "Document-Level",
                "section_ref_2": None,
                "description": f"Superseded Policy Version: Document {doc.doc_id} (v{doc.version}) is inactive.",
                "resolution_status": "SUPERSEDED"
            }
            conflicts.append(conflict_record)
            self._save_conflict_flag(conflict_record)

        return conflicts

    def _save_conflict_flag(self, record: Dict[str, Any]):
        """Persists conflict flag entry to database table `policy_conflict_flags`."""
        existing = self.db.query(PolicyConflictFlag).filter(
            PolicyConflictFlag.conflict_id == record["conflict_id"]
        ).first()

        if not existing:
            flag = PolicyConflictFlag(
                conflict_id=record["conflict_id"],
                conflict_type=record["conflict_type"],
                requirement_id_1=record["requirement_id_1"],
                requirement_id_2=record.get("requirement_id_2"),
                doc_id_1=record["doc_id_1"],
                doc_id_2=record.get("doc_id_2"),
                section_ref_1=record.get("section_ref_1"),
                section_ref_2=record.get("section_ref_2"),
                description=record["description"],
                resolution_status=record["resolution_status"]
            )
            self.db.add(flag)
            self.db.commit()
