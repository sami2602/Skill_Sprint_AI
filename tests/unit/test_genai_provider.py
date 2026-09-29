"""
SkillSprint AI — Unit Tests for GenAI Provider Abstraction
"""

import pytest
import os
from genai.providers.factory import get_llm_provider
from genai.providers.mock_provider import MockLLMProvider
from genai.providers.gemini_provider import GeminiProvider
from genai.providers.base_provider import (
    LLMProviderError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMInvalidResponseError,
)
from genai.schemas.generation_schemas import OnboardingPlan


def test_provider_factory_default_mock():
    provider = get_llm_provider("mock")
    assert isinstance(provider, MockLLMProvider)
    assert provider.provider_name == "Mock"
    assert "mock" in provider.model_name.lower()


def test_mock_provider_generation():
    provider = MockLLMProvider()
    response = provider.generate(
        prompt="Generate plan for ROL-01",
        response_schema=OnboardingPlan,
    )
    assert response is not None
    assert "PLAN-ROL-01" in response or "plan_id" in response


def test_mock_provider_simulated_timeout():
    provider = MockLLMProvider(simulate_timeout=True)
    with pytest.raises(LLMTimeoutError):
        provider.generate("test prompt")


def test_mock_provider_simulated_rate_limit():
    provider = MockLLMProvider(simulate_rate_limit=True)
    with pytest.raises(LLMRateLimitError):
        provider.generate("test prompt")


def test_mock_provider_simulated_invalid_json():
    provider = MockLLMProvider(simulate_invalid_json=True)
    res = provider.generate("test prompt")
    assert res == "{ invalid json payload: [ "


def test_gemini_provider_unconfigured_error():
    # Force no API key
    provider = GeminiProvider(api_key="")
    with pytest.raises(LLMProviderError) as exc_info:
        provider.generate("test prompt")
    assert "API key is not configured" in str(exc_info.value)
