"""
SkillSprint AI — Multi-Stage Personalized Onboarding Plan Generator
Generates structured onboarding plans grounded in the Role Requirement Matrix.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from genai.providers.base_provider import BaseLLMProvider
from genai.prompts.prompt_engine import PromptEngine
from genai.schemas.generation_schemas import OnboardingPlan, GeneratedContentMetadata, SourceCitation
from genai.utils.retry_handler import RetryHandler
from genai.security.prompt_injection import PromptInjectionDefender
from knowledge.roles.matrix_builder import RoleMatrixBuilder

logger = logging.getLogger(__name__)


class OnboardingPlanGenerator:
    """Generates structured, multi-stage, personalized onboarding plans for job roles."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        prompt_engine: Optional[PromptEngine] = None,
        retry_handler: Optional[RetryHandler] = None,
    ):
        self.provider = provider
        self.prompt_engine = prompt_engine or PromptEngine(version="v1")
        self.retry_handler = retry_handler or RetryHandler(max_retries=3)
        self.defender = PromptInjectionDefender()

    def generate_plan_for_role(
        self,
        db_session: Session,
        role_id: str,
        employee_id: Optional[str] = None,
        employee_name: Optional[str] = None,
        experience_level: Optional[str] = None,
        location: Optional[str] = None,
        assigned_responsibilities: Optional[str] = None,
    ) -> OnboardingPlan:
        """
        Retrieves ground-truth Role Requirement Matrix and generates a complete, multi-stage OnboardingPlan.
        """
        # Step 1: Fetch ground-truth Role Requirement Matrix
        matrix_builder = RoleMatrixBuilder(db_session)
        matrix = matrix_builder.build_matrix_for_role(role_id)

        role_title = matrix["role_title"]
        department = matrix["department"]
        mandatory_reqs = matrix["mandatory_items"]
        optional_reqs = matrix["optional_items"]

        # Track input requirement IDs
        input_req_ids = [r["requirement_id"] for r in mandatory_reqs] + [r["requirement_id"] for r in optional_reqs]

        # Step 2: Prepare Jinja2 template context
        context = {
            "employee_name": employee_name or "New Team Member",
            "employee_id": employee_id or "EMP-UNASSIGNED",
            "role_id": role_id,
            "role_title": role_title,
            "department": department,
            "experience_level": experience_level or "Standard",
            "location": location or "HQ",
            "assigned_responsibilities": assigned_responsibilities or "General departmental scope",
            "mandatory_requirements": mandatory_reqs,
            "optional_requirements": optional_reqs,
        }

        # Step 3: Sanitize context through prompt injection defender
        sanitized_context = self.defender.sanitize_context_variables(context)

        # Step 4: Render prompt template
        prompt = self.prompt_engine.render_prompt("onboarding_plan.jinja2", sanitized_context)

        # Step 5: Execute generation with bounded retry & schema validation
        plan: OnboardingPlan = self.retry_handler.execute_with_retry(
            provider=self.provider,
            prompt=prompt,
            response_schema=OnboardingPlan,
            system_instruction="You are the SkillSprint AI generation engine. Generate schema-compliant JSON.",
            temperature=0.2,
        )

        # Step 6: Attach precise audit metadata and ensure source traceability
        source_versions = {}
        for r in mandatory_reqs + optional_reqs:
            source_versions[r["source_doc_id"]] = r["source_version"]

        plan.employee_id = employee_id or plan.employee_id or "EMP-UNASSIGNED"
        plan.role_id = role_id
        plan.role_title = role_title
        plan.department = department

        # Track covered requirement IDs explicitly
        plan.covered_requirement_ids = list(set(input_req_ids))

        plan.metadata = GeneratedContentMetadata(
            prompt_version=self.prompt_engine.version,
            provider=self.provider.provider_name,
            model=self.provider.model_name,
            generation_timestamp=datetime.now(timezone.utc).isoformat(),
            input_requirement_ids=input_req_ids,
            source_versions=source_versions,
            output_schema_version="1.0",
            generation_status="SUCCESS",
            error_info=None,
        )

        logger.info(f"Generated OnboardingPlan {plan.plan_id} for role {role_id} with {len(plan.modules)} modules.")
        return plan
