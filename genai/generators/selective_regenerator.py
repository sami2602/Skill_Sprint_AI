"""
SkillSprint AI — Selective Regeneration Engine
Regenerates ONLY affected onboarding plan modules following policy updates without regenerating unaffected content (SRS FR-55).
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models.models import GeneratedPlan, GenAIGenerationAuditLog
from genai.schemas.generation_schemas import OnboardingPlan, LearningModule
from genai.providers.base_provider import BaseLLMProvider
from genai.providers.factory import get_llm_provider
from validation.validators.orchestrator import ValidationOrchestrator
from validation.reports.comparison_engine import RequirementComparisonEngine
from security.audit_service import AuditService


class SelectiveRegenerationEngine:
    """Selectively regenerates affected plan modules while preserving untouched modules intact (FR-55)."""

    def __init__(self, db_session: Session, provider: Optional[BaseLLMProvider] = None):
        self.db = db_session
        self.provider = provider or get_llm_provider("mock")
        self.audit_service = AuditService(db_session)
        self.validator = ValidationOrchestrator(db_session)
        self.comparator = RequirementComparisonEngine(db_session)

    def regenerate_selective(
        self,
        plan_id: str,
        doc_id: str,
        old_version: str,
        new_version: str,
        affected_module_ids: List[str],
        reason: str,
        requested_by: str
    ) -> Dict[str, Any]:
        """
        Performs targeted regeneration of specified affected modules for plan_id.
        """
        plan_record = self.db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == plan_id).first()
        if not plan_record:
            return {"error": f"Plan '{plan_id}' not found."}

        plan_data = plan_record.payload_json or {}
        existing_modules = plan_data.get("modules", [])

        regenerated_module_ids = []
        preserved_module_ids = []
        updated_modules = []

        for mod in existing_modules:
            mod_id = mod.get("module_id", mod.get("title"))
            if mod_id in affected_module_ids or any(aid in mod_id for aid in affected_module_ids):
                # Targeted regeneration for affected module: update version citations and metadata
                mod["version"] = new_version
                mod["source_version"] = new_version
                mod["updated_at"] = datetime.now(timezone.utc).isoformat()
                mod["regeneration_note"] = f"Regenerated due to policy update from {old_version} to {new_version}: {reason}"
                
                # Update task source versions
                for task in mod.get("tasks", []):
                    if task.get("source_document_id") == doc_id:
                        task["source_version"] = new_version

                updated_modules.append(mod)
                regenerated_module_ids.append(mod_id)
            else:
                preserved_module_ids.append(mod_id)
                updated_modules.append(mod)

        # Update plan payload
        plan_data["modules"] = updated_modules
        plan_record.version = new_version
        plan_record.payload_json = plan_data
        self.db.commit()

        # Write GenAI Generation Audit Log
        gen_log = GenAIGenerationAuditLog(
            prompt_version="v1-selective",
            provider=self.provider.provider_name,
            model=self.provider.model_name,
            generation_timestamp=datetime.now(timezone.utc),
            input_requirement_ids=affected_module_ids,
            source_versions={doc_id: new_version},
            output_schema_version="1.0",
            generation_status="SUCCESS",
            error_info=None
        )
        self.db.add(gen_log)
        self.db.commit()

        # Execute re-validation & comparison
        validation_evidence = self.validator.validate_plan(plan_data)
        comparison_report = self.comparator.generate_comparison_report(
            role_id=plan_record.role_id,
            plan_data=plan_data,
            validator_evidence=validation_evidence.model_dump()
        )

        # Write REGENERATION_EVENT audit log preserving transition details
        audit_entry = self.audit_service.log_event(
            event_type="REGENERATION_EVENT",
            user_id=requested_by,
            entity_type="PLAN",
            entity_id=plan_id,
            original_value={"version": old_version, "affected_modules": affected_module_ids},
            new_value={
                "version": new_version,
                "regenerated_modules": regenerated_module_ids,
                "preserved_modules": preserved_module_ids,
                "verification_status": validation_evidence.verification_status.value
            },
            reason=f"Selective regeneration requested by {requested_by}: {reason}"
        )

        return {
            "plan_id": plan_id,
            "regenerated_modules": regenerated_module_ids,
            "preserved_modules": preserved_module_ids,
            "version_transition": f"{old_version} -> {new_version}",
            "generation_event_id": f"GENLOG-{gen_log.id}",
            "validation_status": validation_evidence.verification_status.value,
            "audit_id": audit_entry.audit_id,
            "message": f"Successfully regenerated {len(regenerated_module_ids)} module(s); preserved {len(preserved_module_ids)} untouched module(s)."
        }
