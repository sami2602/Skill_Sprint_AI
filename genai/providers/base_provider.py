"""
SkillSprint AI — Provider Abstraction Interface for GenAI Models
Defines standard provider interface and error hierarchy to ensure decoupling from specific LLM vendors.
"""

from abc import ABC, abstractmethod
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel


class LLMProviderError(Exception):
    """Base exception for LLM provider failures."""
    pass


class LLMTimeoutError(LLMProviderError):
    """Raised when an LLM API call times out."""
    pass


class LLMRateLimitError(LLMProviderError):
    """Raised when an LLM API rate limit or quota is exceeded (HTTP 429)."""
    pass


class LLMInvalidResponseError(LLMProviderError):
    """Raised when LLM returns invalid output or malformed JSON that violates schema."""
    pass


class BaseLLMProvider(ABC):
    """Abstract interface for GenAI Provider interaction."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Executes a prompt completion request.
        
        Args:
            prompt: User/context prompt string.
            system_instruction: Optional system instruction prompt.
            response_schema: Optional Pydantic BaseModel to enforce structured JSON output.
            temperature: Model temperature (0.0 to 1.0).
            max_tokens: Max output token limit.

        Returns:
            Generated response string (valid JSON string if response_schema is provided).
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the provider name (e.g., 'Gemini', 'Mock')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the specific model name (e.g., 'gemini-2.5-flash')."""
        pass
