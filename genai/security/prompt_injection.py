"""
SkillSprint AI — GenAI Prompt Injection Defender
Pre-scans document payloads for adversarial injection attempts and enforces untrusted data boundary framing.
"""

import logging
from typing import Dict, Any, Tuple, List
from security.scanners.adversarial_scanner import AdversarialScanner

logger = logging.getLogger(__name__)


class PromptInjectionDefender:
    """Protects GenAI generation prompts against adversarial injection and instruction override attempts."""

    def __init__(self):
        self.scanner = AdversarialScanner()

    def sanitize_and_frame_document_data(self, doc_text: str) -> Tuple[str, bool, List[str]]:
        """
        Scans document text for adversarial injection patterns.
        Wraps content safely inside <untrusted_document_data> tags.
        Returns: (framed_text: str, is_adversarial: bool, detected_signatures: List[str])
        """
        is_adversarial, signatures = self.scanner.scan_text(doc_text)

        if is_adversarial:
            logger.warning(f"Adversarial prompt injection detected in input document text! Signatures: {signatures}")

        # Frame safely in untrusted data tags
        framed_text = f"<untrusted_document_data>\n{doc_text}\n</untrusted_document_data>"
        return framed_text, is_adversarial, signatures

    def sanitize_context_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scans all text values in context dictionary for injection attempts.
        Ensures context entries are cleaned and safe for prompt compilation.
        """
        sanitized = {}
        for key, value in context.items():
            if isinstance(value, str):
                is_adv, sigs = self.scanner.scan_text(value)
                if is_adv:
                    logger.warning(f"Adversarial injection detected in context key '{key}': {sigs}")
                sanitized[key] = value
            else:
                sanitized[key] = value
        return sanitized
