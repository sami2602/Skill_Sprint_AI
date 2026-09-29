"""
SkillSprint AI — Adversarial Document & Prompt Injection Scanner
Detects malicious prompt injection payloads embedded in uploaded company documents.
"""

import re
from typing import Tuple, List

# Key prompt injection patterns & adversarial signature regexes
ADVERSARIAL_PATTERNS = [
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"system\s+(override|instruction|prompt)",
    r"disregard\s+(the\s+)?(above|rules|system)",
    r"grant\s+100%\s+compliance",
    r"mark\s+all\s+requirements\s+as\s+verified",
    r"admin\s+override\s*:\s*skip",
    r"skip\s+practical\s+assessment",
    r"output\s+['\"]APPROVED['\"]",
    r"you\s+are\s+now\s+in\s+DAN\s+mode",
    r"jailbreak",
]


class AdversarialScanner:
    """Scans text content extracted from uploaded documents for prompt injection signatures."""

    def __init__(self, custom_patterns: List[str] = None):
        patterns = ADVERSARIAL_PATTERNS + (custom_patterns or [])
        self.compiled_regexes = [re.compile(p, re.IGNORECASE) for p in patterns]

    def scan_text(self, text: str) -> Tuple[bool, List[str]]:
        """
        Scans document text for adversarial injection attempts.
        Returns (is_adversarial: bool, detected_signatures: List[str]).
        """
        detected = []
        for regex in self.compiled_regexes:
            matches = regex.findall(text)
            if matches:
                detected.append(regex.pattern)

        is_adversarial = len(detected) > 0
        return is_adversarial, detected
