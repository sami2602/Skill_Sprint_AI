"""
SkillSprint AI — Provider Factory
Dynamically resolves and instantiates the appropriate LLM provider based on configuration or environment variables.
"""

import os
from typing import Optional
from genai.providers.base_provider import BaseLLMProvider
from genai.providers.gemini_provider import GeminiProvider
from genai.providers.mock_provider import MockLLMProvider


def get_llm_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    use_mock_fallback: bool = True,
) -> BaseLLMProvider:
    """
    Factory function to retrieve an active LLM provider instance.
    
    Order of preference:
    1. Explicit provider_name if passed ("gemini", "mock").
    2. Environment variable GENAI_PROVIDER ("gemini", "mock").
    3. GeminiProvider if GEMINI_API_KEY / GENAI_API_KEY is available.
    4. MockLLMProvider fallback if use_mock_fallback is True.
    """
    target_provider = (provider_name or os.getenv("GENAI_PROVIDER") or "").lower()
    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GENAI_API_KEY")

    if target_provider == "mock":
        return MockLLMProvider(model=model or "gemini-2.5-flash-mock")

    if target_provider == "gemini" or key:
        try:
            return GeminiProvider(api_key=key, model=model or "gemini-2.5-flash")
        except Exception:
            if use_mock_fallback:
                return MockLLMProvider(model=model or "gemini-2.5-flash-mock")
            raise

    if use_mock_fallback:
        return MockLLMProvider(model=model or "gemini-2.5-flash-mock")

    raise RuntimeError("No LLM provider configured and mock fallback is disabled.")
