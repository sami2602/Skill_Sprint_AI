"""
SkillSprint AI — Rule-Based Requirement Extractor Engine
Extracts policy requirements deterministically from text chunks using modal verb analysis and structural heuristics.
(100% Python rule-based processing — NO GenAI calls used for ground-truth matrix extraction).
"""

import re
from typing import List, Dict, Any
from backend.schemas.schemas import RequirementSchema


class RuleBasedRequirementExtractor:
    """Extracts policy requirement entities from company document text chunks."""

    # Modal verb taxonomy for categorization
    MANDATORY_VERBS = {"must", "shall", "required", "mandatory", "is obligated to"}
    RECOMMENDED_VERBS = {"should", "recommended", "advised", "encouraged"}
    OPTIONAL_VERBS = {"may", "optional", "can", "permitted"}

    def extract_from_chunk(
        self,
        chunk_id: str,
        doc_id: str,
        section_ref: str,
        text_content: str,
        category: str = "General"
    ) -> List[RequirementSchema]:
        """
        Parses sentences in text chunk to identify actionable policy requirements.
        """
        requirements = []
        sentences = re.split(r'(?<=[.!?])\s+', text_content)

        req_num = 1
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if len(sentence_clean) < 15:
                continue

            sentence_lower = sentence_clean.lower()
            matched_verb = None
            is_mandatory = False
            cat = "RECOMMENDED"

            # Check mandatory verbs
            for verb in self.MANDATORY_VERBS:
                if verb in sentence_lower:
                    matched_verb = verb
                    is_mandatory = True
                    cat = "MUST_KNOW" if "understand" in sentence_lower or "know" in sentence_lower else "MUST_COMPLETE"
                    break

            # Check recommended verbs if not mandatory
            if not matched_verb:
                for verb in self.RECOMMENDED_VERBS:
                    if verb in sentence_lower:
                        matched_verb = verb
                        is_mandatory = False
                        cat = "RECOMMENDED"
                        break

            # Check optional verbs if not recommended
            if not matched_verb:
                for verb in self.OPTIONAL_VERBS:
                    if verb in sentence_lower:
                        matched_verb = verb
                        is_mandatory = False
                        cat = "OPTIONAL"
                        break

            if matched_verb:
                req_id = f"REQ-EXT-{doc_id}-{req_num:03d}"
                req_num += 1

                # Role applicability heuristic
                target_roles = ["ALL"]
                if "software engineer" in sentence_lower or "developer" in sentence_lower:
                    target_roles = ["ROL-01", "ROL-02"]
                elif "customer support" in sentence_lower or "support agent" in sentence_lower:
                    target_roles = ["ROL-03", "ROL-04"]
                elif "finance" in sentence_lower or "analyst" in sentence_lower:
                    target_roles = ["ROL-05"]

                requirements.append(RequirementSchema(
                    requirement_id=req_id,
                    doc_id=doc_id,
                    section_ref=section_ref,
                    title=f"Requirement {req_id} ({doc_id})",
                    requirement_text=sentence_clean,
                    category=cat,
                    priority="HIGH" if is_mandatory else "MEDIUM",
                    modal_verb=matched_verb,
                    is_mandatory=is_mandatory,
                    target_roles=target_roles
                ))

        return requirements
