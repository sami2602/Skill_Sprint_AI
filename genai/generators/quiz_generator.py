"""
SkillSprint AI — Quiz & Assessment Generator
Generates structured quizzes, questions, options, distractors, explanations, and requirement source mappings.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from genai.providers.base_provider import BaseLLMProvider
from genai.prompts.prompt_engine import PromptEngine
from genai.schemas.generation_schemas import Quiz, QuizQuestion, QuizOption, SourceCitation
from genai.utils.retry_handler import RetryHandler
from genai.security.prompt_injection import PromptInjectionDefender

logger = logging.getLogger(__name__)


class QuizGenerator:
    """Generates structured quizzes with dynamic distractors and source citations."""

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

    def generate_quiz_for_requirements(
        self,
        requirements: List[Dict[str, Any]],
        quiz_title: str = "Policy Compliance Assessment",
        passing_score: float = 80.0,
    ) -> Quiz:
        """
        Generates a Quiz testing the supplied list of ground-truth policy requirements.
        """
        context = {
            "requirements": requirements,
            "quiz_title": quiz_title,
            "passing_score": passing_score,
        }

        sanitized_context = self.defender.sanitize_context_variables(context)
        prompt = self.prompt_engine.render_prompt("quiz_generation.jinja2", sanitized_context)

        quiz: Quiz = self.retry_handler.execute_with_retry(
            provider=self.provider,
            prompt=prompt,
            response_schema=Quiz,
            system_instruction="Generate schema-compliant quiz JSON. Do not hardcode fixed answers.",
            temperature=0.2,
        )

        quiz.passing_score_percentage = passing_score
        quiz.requirement_ids = [r.get("requirement_id", "REQ-000") for r in requirements if isinstance(r, dict)]

        logger.info(f"Generated Quiz {quiz.quiz_id} with {len(quiz.questions)} questions.")
        return quiz
