"""
SkillSprint AI — Humanized Requirement Explanation Generator
Generates practical, humanized requirement explanations and scenario guides for employees.
"""

import logging
from typing import Dict, Any, Optional
from genai.providers.base_provider import BaseLLMProvider
from genai.prompts.prompt_engine import PromptEngine
from genai.schemas.generation_schemas import RequirementExplanation, SourceCitation
from genai.utils.retry_handler import RetryHandler
from genai.security.prompt_injection import PromptInjectionDefender

logger = logging.getLogger(__name__)


class RequirementExplanationGenerator:
    """Generates humanized explanations and practical scenarios for policy requirements."""

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

    def generate_explanation(self, requirement: Dict[str, Any]) -> RequirementExplanation:
        """
        Generates a RequirementExplanation object for a given requirement dictionary.
        """
        req_id = requirement.get("requirement_id", "REQ-000")
        doc_id = requirement.get("source_doc_id", "DOC-00")
        doc_ver = requirement.get("source_version", "1.0")
        sec_ref = requirement.get("source_section_ref", "SEC-01")

        context = {
            "requirement_id": req_id,
            "source_doc_id": doc_id,
            "source_version": doc_ver,
            "source_section_ref": sec_ref,
            "title": requirement.get("title", "Policy Requirement"),
            "category": requirement.get("category", "MUST_KNOW"),
            "is_mandatory": requirement.get("is_mandatory", True),
            "requirement_text": requirement.get("requirement_text", ""),
        }

        sanitized_context = self.defender.sanitize_context_variables(context)
        prompt = self.prompt_engine.render_prompt("requirement_explanation.jinja2", sanitized_context)

        explanation: RequirementExplanation = self.retry_handler.execute_with_retry(
            provider=self.provider,
            prompt=prompt,
            response_schema=RequirementExplanation,
            system_instruction="Generate clear humanized requirement explanation JSON.",
            temperature=0.2,
        )

        explanation.requirement_id = req_id
        explanation.source_citation = SourceCitation(
            doc_id=doc_id,
            doc_version=doc_ver,
            section_id=sec_ref,
            requirement_id=req_id,
        )

        return explanation
