"""
SkillSprint AI — Unit Tests for Bounded Retry & Execution Handler
"""

import pytest
from genai.providers.mock_provider import MockLLMProvider
from genai.utils.retry_handler import RetryHandler, GenerationFailureError
from genai.schemas.generation_schemas import OnboardingPlan


def test_retry_handler_success():
    provider = MockLLMProvider()
    handler = RetryHandler(max_retries=3, initial_backoff_seconds=0.01)

    plan = handler.execute_with_retry(
        provider=provider,
        prompt="Generate plan",
        response_schema=OnboardingPlan,
    )
    assert plan is not None
    assert isinstance(plan, OnboardingPlan)
    assert provider.call_count == 1


def test_retry_handler_exhaustion_on_invalid_json():
    provider = MockLLMProvider(simulate_invalid_json=True)
    handler = RetryHandler(max_retries=3, initial_backoff_seconds=0.01)

    with pytest.raises(GenerationFailureError) as exc_info:
        handler.execute_with_retry(
            provider=provider,
            prompt="Generate plan",
            response_schema=OnboardingPlan,
        )
    assert exc_info.value.attempts == 3
    assert "failed after 3 attempts" in str(exc_info.value)


def test_retry_handler_exhaustion_on_timeout():
    provider = MockLLMProvider(simulate_timeout=True)
    handler = RetryHandler(max_retries=2, initial_backoff_seconds=0.01)

    with pytest.raises(GenerationFailureError) as exc_info:
        handler.execute_with_retry(
            provider=provider,
            prompt="Generate plan",
            response_schema=OnboardingPlan,
        )
    assert exc_info.value.attempts == 2
