"""
SkillSprint AI — Policy Update Impact Analysis Engine
Identifies affected requirements, job roles, onboarding plans, learning modules, tasks, and quizzes following document updates (SRS FR-53, FR-54).
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models.models import Document, PolicyRequirement, GeneratedPlan, PolicyChangeImpact
from validation.schemas import PolicyImpactAnalysisResponse
from security.audit_service import AuditService


class ImpactAnalysisEngine:
    """Analyzes system impact when a company policy or SOP is updated (FR-53, FR-54)."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.audit_service = AuditService(db_session)

    def analyze_impact(
        self,
        doc_id: str,
        new_version: str,
        old_version: Optional[str] = None
    ) -> PolicyImpactAnalysisResponse:
        """
        Executes policy impact trace:
        Old Policy Version -> New Policy Version -> Affected Requirements -> Affected Roles -> Affected Onboarding Plans -> Affected Modules -> Affected Tasks -> Affected Quizzes
        """
        doc = self.db.query(Document).filter(Document.doc_id == doc_id).first()
        prev_version = old_version or (doc.version if doc else "1.0")

        # 1. Affected Requirements
        requirements = []
        if doc:
            requirements = self.db.query(PolicyRequirement).filter(
                PolicyRequirement.document_id == doc.id
            ).all()

        affected_req_ids = [r.requirement_id for r in requirements]

        # 2. Affected Roles
        affected_roles = set()
        for req in requirements:
            if req.target_roles:
                for role in req.target_roles:
                    affected_roles.add(role)
        affected_roles_list = list(affected_roles)

        # 3. Affected Plans
        plans = self.db.query(GeneratedPlan).all()
        affected_plans = []
        affected_modules = set()
        affected_tasks = set()
        affected_quizzes = set()

        for plan in plans:
            # Check if plan belongs to an affected role or references affected requirement IDs / doc_id
            payload = plan.payload_json or {}
            plan_req_ids = set(plan.covered_requirement_ids or [])
            is_plan_affected = False

            if plan.role_id in affected_roles_list or plan_req_ids.intersection(affected_req_ids):
                is_plan_affected = True

            modules = payload.get("modules", [])
            for mod in modules:
                mod_id = mod.get("module_id", f"MOD-{mod.get('title', '')}")
                mod_doc_id = mod.get("source_document_id")

                # Check tasks inside module
                for task in mod.get("tasks", []):
                    task_id = task.get("task_id")
                    task_reqs = {rm.get("requirement_id") for rm in task.get("requirement_mappings", []) if isinstance(rm, dict)}
                    if task.get("source_document_id") == doc_id or task_reqs.intersection(affected_req_ids):
                        affected_tasks.add(task_id or task.get("title"))
                        affected_modules.add(mod_id)
                        is_plan_affected = True

                # Check quizzes inside module
                for quiz in mod.get("quizzes", []):
                    if isinstance(quiz, dict):
                        quiz_id = quiz.get("quiz_id")
                        for qst in quiz.get("questions", []):
                            if qst.get("requirement_id") in affected_req_ids or qst.get("source_doc_id") == doc_id:
                                affected_quizzes.add(quiz_id or qst.get("question_id"))
                                affected_modules.add(mod_id)
                                is_plan_affected = True
                    elif isinstance(quiz, str):
                        affected_quizzes.add(quiz)
                        affected_modules.add(mod_id)
                        is_plan_affected = True

                if mod_doc_id == doc_id:
                    affected_modules.add(mod_id)
                    is_plan_affected = True

            if is_plan_affected:
                affected_plans.append(plan.plan_id)

        affected_plan_ids = list(set(affected_plans))
        affected_module_ids = list(affected_modules)
        affected_task_ids = list(affected_tasks)
        affected_quiz_ids = list(affected_quizzes)

        # Save PolicyChangeImpact DB record
        impact_entry = PolicyChangeImpact(
            doc_id=doc_id,
            old_version=prev_version,
            new_version=new_version,
            affected_roles=affected_roles_list,
            affected_requirement_count=len(affected_req_ids),
            affected_plans=affected_plan_ids,
            affected_modules=affected_module_ids,
            affected_tasks=affected_task_ids,
            affected_quizzes=affected_quiz_ids,
            impact_timestamp=datetime.now(timezone.utc)
        )
        self.db.add(impact_entry)
        self.db.commit()

        # Audit trail entry for policy version update & impact calculation
        self.audit_service.log_event(
            event_type="POLICY_VERSION_CHANGE",
            user_id="SYSTEM",
            entity_type="DOCUMENT",
            entity_id=doc_id,
            original_value={"version": prev_version},
            new_value={
                "version": new_version,
                "affected_requirements": len(affected_req_ids),
                "affected_roles": len(affected_roles_list),
                "affected_plans": len(affected_plan_ids),
                "affected_modules": len(affected_module_ids)
            },
            reason=f"Policy version update from {prev_version} to {new_version} for document {doc_id}."
        )

        return PolicyImpactAnalysisResponse(
            doc_id=doc_id,
            old_version=prev_version,
            new_version=new_version,
            affected_requirement_ids=affected_req_ids,
            affected_roles=affected_roles_list,
            affected_plan_ids=affected_plan_ids,
            affected_module_ids=affected_module_ids,
            affected_task_ids=affected_task_ids,
            affected_quiz_ids=affected_quiz_ids,
            impact_timestamp=datetime.now(timezone.utc).isoformat()
        )
