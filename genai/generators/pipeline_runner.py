"""
SkillSprint AI — GenAI Master Generation Pipeline Orchestrator
Coordinates end-to-end generation across providers, prompt templates, retry handlers, and security defenders.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from genai.providers.factory import get_llm_provider
from genai.providers.base_provider import BaseLLMProvider
from genai.prompts.prompt_engine import PromptEngine
from genai.generators.plan_generator import OnboardingPlanGenerator
from genai.generators.quiz_generator import QuizGenerator
from genai.generators.explanation_generator import RequirementExplanationGenerator
from genai.schemas.generation_schemas import OnboardingPlan, Quiz, RequirementExplanation

logger = logging.getLogger(__name__)


class GenAIPipelineRunner:
    """Master orchestrator for the Phase 4 GenAI Generation Pipeline."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None, prompt_version: str = "v1"):
        self.provider = provider or get_llm_provider()
        self.prompt_engine = PromptEngine(version=prompt_version)
        self.plan_generator = OnboardingPlanGenerator(provider=self.provider, prompt_engine=self.prompt_engine)
        self.quiz_generator = QuizGenerator(provider=self.provider, prompt_engine=self.prompt_engine)
        self.explanation_generator = RequirementExplanationGenerator(provider=self.provider, prompt_engine=self.prompt_engine)

    def generate_onboarding_plan(
        self,
        db_session: Session,
        role_id: str,
        employee_id: Optional[str] = None,
        employee_name: Optional[str] = None,
        experience_level: Optional[str] = None,
        location: Optional[str] = None,
        assigned_responsibilities: Optional[str] = None,
    ) -> OnboardingPlan:
        """Generates a complete multi-stage personalized OnboardingPlan."""
        logger.info(f"Starting GenAI Pipeline execution for role {role_id}")
        return self.plan_generator.generate_plan_for_role(
            db_session=db_session,
            role_id=role_id,
            employee_id=employee_id,
            employee_name=employee_name,
            experience_level=experience_level,
            location=location,
            assigned_responsibilities=assigned_responsibilities,
        )

    def generate_quiz(
        self,
        requirements: List[Dict[str, Any]],
        quiz_title: str = "Compliance Assessment",
        passing_score: float = 80.0,
    ) -> Quiz:
        """Generates a Quiz assessment for policy requirements."""
        return self.quiz_generator.generate_quiz_for_requirements(
            requirements=requirements,
            quiz_title=quiz_title,
            passing_score=passing_score,
        )

    def generate_explanation(self, requirement: Dict[str, Any]) -> RequirementExplanation:
        """Generates a humanized requirement explanation."""
        return self.explanation_generator.generate_explanation(requirement)
