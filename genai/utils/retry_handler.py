"""
SkillSprint AI — Bounded Retry & Execution Handler
Manages resilient execution with exponential backoff and schema validation retries.
"""

import time
import logging
import json
from typing import Callable, TypeVar, Optional, Type, Dict, Any
from pydantic import BaseModel, ValidationError
from genai.providers.base_provider import (
    BaseLLMProvider,
    LLMProviderError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMInvalidResponseError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class GenerationFailureError(Exception):
    """Raised when GenAI generation fails permanently after retries are exhausted."""
    def __init__(self, message: str, attempts: int, last_error: Optional[Exception] = None):
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


class RetryHandler:
    """Executes LLM generation calls with bounded retries and exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff_seconds: float = 0.5,
        backoff_multiplier: float = 2.0,
    ):
        self.max_retries = max_retries
        self.initial_backoff_seconds = initial_backoff_seconds
        self.backoff_multiplier = backoff_multiplier

    def execute_with_retry(
        self,
        provider: BaseLLMProvider,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        """
        Executes generation and validates response against Pydantic schema T.
        Retries up to max_retries on transient errors or schema validation failures.
        Never silently returns fabricated fallback data on exhaustion.
        """
        last_exception: Optional[Exception] = None
        backoff = self.initial_backoff_seconds

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"GenAI execution attempt {attempt}/{self.max_retries} via {provider.provider_name} ({provider.model_name})")

                raw_output = provider.generate(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    response_schema=response_schema,
                    temperature=temperature,
                )

                # Parse JSON
                cleaned_output = self._clean_json(raw_output)
                parsed_json = json.loads(cleaned_output)

                # Validate Pydantic schema
                validated_obj = response_schema.model_validate(parsed_json)
                logger.info(f"GenAI generation successful on attempt {attempt}")
                return validated_obj

            except (json.JSONDecodeError, ValidationError, LLMInvalidResponseError) as schema_err:
                last_exception = schema_err
                logger.warning(f"Attempt {attempt}/{self.max_retries} failed schema validation: {str(schema_err)}")

            except (LLMTimeoutError, LLMRateLimitError) as transient_err:
                last_exception = transient_err
                logger.warning(f"Attempt {attempt}/{self.max_retries} transient provider error: {str(transient_err)}")

            except LLMProviderError as provider_err:
                last_exception = provider_err
                logger.error(f"Attempt {attempt}/{self.max_retries} non-retryable provider error: {str(provider_err)}")
                # If provider error is unrecoverable (e.g. missing API key), break early
                if "API key is not configured" in str(provider_err):
                    raise GenerationFailureError(
                        f"GenAI pipeline failure: {str(provider_err)}",
                        attempts=attempt,
                        last_error=provider_err
                    )

            except Exception as unhandled_err:
                last_exception = unhandled_err
                logger.error(f"Attempt {attempt}/{self.max_retries} unhandled error: {str(unhandled_err)}")

            # Exponential backoff delay before retry if not last attempt
            if attempt < self.max_retries:
                time.sleep(backoff)
                backoff *= self.backoff_multiplier

        # Retries exhausted without valid schema response
        raise GenerationFailureError(
            f"GenAI pipeline failed after {self.max_retries} attempts. Last error: {str(last_exception)}",
            attempts=self.max_retries,
            last_error=last_exception
        )

    def _clean_json(self, text: str) -> str:
        """Strips markdown code fence wrappers from raw JSON string."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text
