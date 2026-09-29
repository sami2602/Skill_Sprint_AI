"""
SkillSprint AI — Requirement-Level Comparison Engine
Generates itemized requirement-level comparison matrix between Role Requirement Matrix, GenAI Output, and Independent Python Validator evidence (SRS FR-42).
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models.models import ComparisonResultModel, GeneratedPlan, ValidationRun, PolicyRequirement, Document
from knowledge.roles.matrix_builder import RoleMatrixBuilder
from validation.schemas import (
    RequirementComparisonReport,
    RequirementComparisonItem,
    ComparisonResultStatusEnum
)
from security.audit_service import AuditService


class RequirementComparisonEngine:
    """Compares GenAI plan output against ground-truth Role Requirement Matrix item-by-item (FR-42)."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.matrix_builder = RoleMatrixBuilder(db_session)
        self.audit_service = AuditService(db_session)

    def generate_comparison_report(
        self,
        role_id: str,
        plan_data: Dict[str, Any],
        validator_evidence: Optional[Dict[str, Any]] = None
    ) -> RequirementComparisonReport:
        """
        Generates itemized comparison for every requirement in role matrix.
        Includes Python validation findings, source metadata, evidence chain, and persistent DB storage.
        """
        matrix = self.matrix_builder.build_matrix_for_role(role_id)
        plan_id = plan_data.get("plan_id", f"PLAN-{uuid.uuid4().hex[:8].upper()}")

        # Build map of covered requirements from generated plan JSON structure
        covered_req_map: Dict[str, List[Dict[str, Any]]] = {}

        modules = plan_data.get("modules", [])
        for mod in modules:
            mod_title = mod.get("title", "")
            mod_stage = mod.get("stage", "Day 1")
            for task in mod.get("tasks", []):
                task_title = task.get("title", "")
                task_desc = task.get("description", "")
                for rm in task.get("requirement_mappings", []):
                    r_id = rm.get("requirement_id") if isinstance(rm, dict) else getattr(rm, "requirement_id", None)
                    if r_id:
                        if r_id not in covered_req_map:
                            covered_req_map[r_id] = []
                        covered_req_map[r_id].append({
                            "type": "TASK",
                            "title": task_title,
                            "description": task_desc,
                            "module": mod_title,
                            "stage": task.get("due_stage", mod_stage),
                            "source_doc_id": task.get("source_document_id") or mod.get("source_document_id"),
                            "source_version": task.get("source_version") or "1.0",
                            "is_mandatory": task.get("is_mandatory", True)
                        })
            quizzes_list = mod.get("quizzes", []) or mod.get("quiz", [])
            if isinstance(quizzes_list, dict):
                quizzes_list = [quizzes_list]
            if isinstance(quizzes_list, list):
                for quiz in quizzes_list:
                    if isinstance(quiz, dict):
                        for qst in quiz.get("questions", []):
                            r_id = qst.get("requirement_id") if isinstance(qst, dict) else getattr(qst, "requirement_id", None)
                            if r_id:
                                if r_id not in covered_req_map:
                                    covered_req_map[r_id] = []
                                covered_req_map[r_id].append({
                                    "type": "QUIZ_QUESTION",
                                    "title": qst.get("question_text", "")[:60] if isinstance(qst, dict) else "",
                                    "description": qst.get("question_text", "") if isinstance(qst, dict) else "",
                                    "module": mod_title,
                                    "stage": mod_stage,
                                    "source_doc_id": (qst.get("source_doc_id") if isinstance(qst, dict) else None) or mod.get("source_document_id"),
                                    "source_version": "1.0",
                                    "is_mandatory": True
                                })

        # Fetch validator evidence lists if provided
        evidence_data = validator_evidence or {}
        missing_mandatory_ids = set(evidence_data.get("mandatory_missing", []))
        unsupported_items = evidence_data.get("unsupported_items", [])
        contradictions = evidence_data.get("contradictions", [])
        outdated_sources = evidence_data.get("outdated_sources", [])
        role_irrelevance_flags = evidence_data.get("role_irrelevance_flags", [])

        unsupported_req_ids = {u.get("requirement_id") for u in unsupported_items if u.get("requirement_id")}
        contradiction_req_ids = {c.get("requirement_id") for c in contradictions if c.get("requirement_id")}
        outdated_req_ids = {o.get("requirement_id") for o in outdated_sources if o.get("requirement_id")}
        irrelevant_req_ids = {r.get("requirement_id") for r in role_irrelevance_flags if r.get("requirement_id")}

        all_matrix_items = matrix["mandatory_items"] + matrix["optional_items"]
        comparison_items: List[RequirementComparisonItem] = []

        covered_count = 0
        missing_count = 0
        partial_count = 0
        unsupported_count = 0
        contradiction_count = 0
        outdated_count = 0
        irrelevant_count = 0
        needs_review_count = 0

        for m_item in all_matrix_items:
            req_id = m_item["requirement_id"]
            req_text = m_item.get("text", m_item.get("title", ""))
            is_mandatory = m_item["is_mandatory"]
            source_doc = m_item.get("source_doc_id", "DOC-POL01")
            source_ver = m_item.get("source_version", "1.0")
            section_ref = m_item.get("section_ref", "SEC-01")

            expected_behavior = f"Ground truth requires '{req_id}' ({m_item['title']}) to be covered for role '{role_id}'."

            # Determine comparison state deterministically
            if req_id in contradiction_req_ids:
                res_status = ComparisonResultStatusEnum.CONTRADICTORY
                val_result = "FAILED"
                gen_desc = f"Generated content contains conflicting policy logic for {req_id}."
                evidence_str = f"Expected: Ground truth compliance for {req_id} -> Generated: Conflict with higher precedence rule -> Validated: FAILED -> Decision: CONTRADICTORY"
                contradiction_count += 1
            elif req_id in outdated_req_ids:
                res_status = ComparisonResultStatusEnum.OUTDATED_SOURCE
                val_result = "FAILED"
                gen_desc = f"Generated item references obsolete or superseded version of {source_doc}."
                evidence_str = f"Expected: Active document version -> Generated: Cited outdated version -> Validated: FAILED -> Decision: OUTDATED_SOURCE"
                outdated_count += 1
            elif req_id in unsupported_req_ids:
                res_status = ComparisonResultStatusEnum.UNSUPPORTED
                val_result = "FAILED"
                gen_desc = f"Generated statement for {req_id} has no supporting text in source documents."
                evidence_str = f"Expected: Verified citation in {source_doc} -> Generated: Ungrounded claim -> Validated: FAILED -> Decision: UNSUPPORTED"
                unsupported_count += 1
            elif req_id in irrelevant_req_ids:
                res_status = ComparisonResultStatusEnum.IRRELEVANT
                val_result = "WARNING"
                gen_desc = f"Requirement {req_id} is irrelevant to role scope '{role_id}'."
                evidence_str = f"Expected: Role-appropriate training -> Generated: Out-of-scope requirement -> Validated: WARNING -> Decision: IRRELEVANT"
                irrelevant_count += 1
            elif req_id in missing_mandatory_ids or (is_mandatory and req_id not in covered_req_map):
                res_status = ComparisonResultStatusEnum.MISSING
                val_result = "FAILED"
                gen_desc = f"Mandatory requirement '{req_id}' is completely missing from generated plan."
                evidence_str = f"Expected: Include {req_id} in plan -> Generated: Omitted -> Validated: FAILED -> Decision: MISSING"
                missing_count += 1
            elif req_id in covered_req_map:
                coverages = covered_req_map[req_id]
                gen_desc = f"Covered by {len(coverages)} item(s): " + ", ".join([f"{c['type']} '{c['title']}' ({c['stage']})" for c in coverages[:2]])
                res_status = ComparisonResultStatusEnum.COVERED
                val_result = "PASSED"
                evidence_str = f"Expected: Satisfy {req_id} -> Generated: {gen_desc} -> Validated: PASSED -> Decision: COVERED"
                covered_count += 1
            elif not is_mandatory:
                res_status = ComparisonResultStatusEnum.NEEDS_REVIEW
                val_result = "WARNING"
                gen_desc = f"Optional requirement '{req_id}' omitted."
                evidence_str = f"Expected: Optional inclusion -> Generated: Omitted -> Validated: WARNING -> Decision: NEEDS_REVIEW"
                needs_review_count += 1
            else:
                res_status = ComparisonResultStatusEnum.NEEDS_REVIEW
                val_result = "WARNING"
                gen_desc = f"Requirement '{req_id}' requires manual inspection."
                evidence_str = f"Expected: Standard coverage -> Generated: Pending review -> Validated: WARNING -> Decision: NEEDS_REVIEW"
                needs_review_count += 1

            # Check if there is an existing reviewer override in DB
            existing_model = self.db.query(ComparisonResultModel).filter(
                ComparisonResultModel.plan_id == plan_id,
                ComparisonResultModel.requirement_id == req_id
            ).first()

            rev_status = existing_model.reviewer_status if existing_model else None
            rev_id = existing_model.reviewer_id if existing_model else None
            rev_comment = existing_model.reviewer_comment if existing_model else None
            override_reason = existing_model.override_reason if existing_model else None

            comp_item = RequirementComparisonItem(
                requirement_id=req_id,
                title=m_item["title"],
                requirement_text=req_text,
                is_mandatory=is_mandatory,
                role_id=role_id,
                expected_behavior=expected_behavior,
                generated_behavior=gen_desc,
                generated_content=gen_desc,
                generated_coverage="FULL" if res_status == ComparisonResultStatusEnum.COVERED else "PARTIAL" if res_status == ComparisonResultStatusEnum.PARTIALLY_COVERED else "NONE",
                source_doc_id=source_doc,
                source_version=source_ver,
                source_location=section_ref,
                validation_rule="MandatoryCoverageRule" if is_mandatory else "OptionalCoverageRule",
                validation_result=val_result,
                result_status=res_status,
                evidence=evidence_str,
                reviewer_status=rev_status,
                reviewer_id=rev_id,
                reviewer_comment=rev_comment,
                override_reason=override_reason
            )
            comparison_items.append(comp_item)

            # Persist / update record in comparison_results table
            if existing_model:
                existing_model.expected_behavior = expected_behavior
                existing_model.generated_behavior = gen_desc
                existing_model.generated_content = gen_desc
                existing_model.validation_result = val_result
                existing_model.result_status = res_status.value
                existing_model.evidence = evidence_str
            else:
                db_record = ComparisonResultModel(
                    comparison_id=f"CMP-{uuid.uuid4().hex[:8].upper()}",
                    plan_id=plan_id,
                    role_id=role_id,
                    requirement_id=req_id,
                    requirement_text=req_text,
                    is_mandatory=is_mandatory,
                    expected_behavior=expected_behavior,
                    generated_behavior=gen_desc,
                    generated_content=gen_desc,
                    generated_coverage=comp_item.generated_coverage,
                    source_doc_id=source_doc,
                    source_version=source_ver,
                    source_location=section_ref,
                    validation_rule=comp_item.validation_rule,
                    validation_result=val_result,
                    result_status=res_status.value,
                    evidence=evidence_str,
                    reviewer_status=rev_status,
                    reviewer_id=rev_id,
                    reviewer_comment=rev_comment,
                    override_reason=override_reason
                )
                self.db.add(db_record)

        self.db.commit()

        summary = {
            "total_evaluated": len(all_matrix_items),
            "covered": covered_count,
            "missing_mandatory": missing_count,
            "partially_covered": partial_count,
            "unsupported": unsupported_count,
            "contradictory": contradiction_count,
            "outdated_sources": outdated_count,
            "irrelevant": irrelevant_count,
            "needs_review": needs_review_count,
            "coverage_percentage": round((covered_count / len(all_matrix_items) * 100.0), 2) if all_matrix_items else 100.0
        }

        # Write audit trail event
        self.audit_service.log_event(
            event_type="COMPARISON_EVENT",
            user_id="SYSTEM",
            entity_type="PLAN",
            entity_id=plan_id,
            original_value=None,
            new_value=summary,
            reason=f"Generated requirement-level comparison report for plan {plan_id}."
        )

        return RequirementComparisonReport(
            plan_id=plan_id,
            role_id=role_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            summary=summary,
            items=comparison_items
        )
