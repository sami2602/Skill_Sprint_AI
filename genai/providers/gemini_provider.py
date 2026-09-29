"""
SkillSprint AI — Gemini 2.5 Flash GenAI Provider Implementation
Encapsulates Google Gemini API integration with structured JSON enforcement and error wrapping.
"""

import os
import json
import logging
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel
from genai.providers.base_provider import (
    BaseLLMProvider,
    LLMProviderError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMInvalidResponseError,
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API Provider implementation supporting Gemini 2.5 Flash."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GENAI_API_KEY")
        self._model_name = model

        # Check if google-genai or google-generativeai SDK is available
        self._client = None
        self._sdk_type = None

        if self._api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
                self._sdk_type = "google-genai"
            except ImportError:
                try:
                    import google.generativeai as genai_legacy
                    genai_legacy.configure(api_key=self._api_key)
                    self._client = genai_legacy
                    self._sdk_type = "google-generativeai"
                except ImportError:
                    logger.warning("Neither 'google-genai' nor 'google-generativeai' SDK is installed.")

    @property
    def provider_name(self) -> str:
        return "Gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Executes generation using Google Gemini API with fallback handling.
        """
        if not self._api_key or not self._client:
            raise LLMProviderError(
                "Gemini API key is not configured or Gemini SDK is missing. "
                "Set GEMINI_API_KEY environment variable."
            )

        try:
            if self._sdk_type == "google-genai":
                config_kwargs: Dict[str, Any] = {
                    "temperature": temperature,
                }
                if system_instruction:
                    config_kwargs["system_instruction"] = system_instruction
                if response_schema:
                    config_kwargs["response_mime_type"] = "application/json"
                    config_kwargs["response_schema"] = response_schema

                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config_kwargs
                )
                raw_text = response.text

            elif self._sdk_type == "google-generativeai":
                generation_config = {"temperature": temperature}
                if response_schema:
                    generation_config["response_mime_type"] = "application/json"

                model_obj = self._client.GenerativeModel(
                    model_name=self._model_name,
                    system_instruction=system_instruction
                )
                response = model_obj.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                raw_text = response.text
            else:
                raise LLMProviderError("Gemini SDK client not initialized.")

            if not raw_text or not raw_text.strip():
                raise LLMInvalidResponseError("Gemini returned empty response.")

            # Validate against schema if requested
            if response_schema:
                try:
                    # Validate JSON parseable
                    cleaned_json = self._clean_json_markdown(raw_text)
                    parsed = json.loads(cleaned_json)
                    response_schema.model_validate(parsed)
                    return cleaned_json
                except (json.JSONDecodeError, Exception) as val_err:
                    raise LLMInvalidResponseError(f"Gemini output failed schema validation: {str(val_err)}")

            return raw_text

        except LLMInvalidResponseError:
            raise
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "resource_exhausted" in err_str or "rate limit" in err_str:
                raise LLMRateLimitError(f"Gemini rate limit exceeded: {str(e)}")
            elif "timeout" in err_str or "deadline" in err_str:
                raise LLMTimeoutError(f"Gemini API timed out: {str(e)}")
            else:
                raise LLMProviderError(f"Gemini generation error: {str(e)}")

    def _clean_json_markdown(self, text: str) -> str:
        """Strips markdown code fence wrappers from raw JSON output."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text
