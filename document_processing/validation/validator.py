"""
SkillSprint AI — Document File Validation Service
Validates file extension, size, duplicate status, non-emptiness, checksum, and adversarial payloads.
"""

import hashlib
import os
from typing import Optional, List
from backend.schemas.schemas import DocumentValidationResult
from security.scanners.adversarial_scanner import AdversarialScanner

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class DocumentValidator:
    """Validates uploaded company policy documents before parsing."""

    def __init__(self, existing_checksums: Optional[List[str]] = None):
        self.existing_checksums = set(existing_checksums or [])
        self.adversarial_scanner = AdversarialScanner()

    def compute_checksum(self, file_content: bytes) -> str:
        """Calculates SHA-256 checksum of file bytes."""
        return hashlib.sha256(file_content).hexdigest()

    def validate_file(self, file_path: str, raw_text: str = "") -> DocumentValidationResult:
        """Validates a file on disk."""
        errors = []
        warnings = []
        is_adversarial = False
        adversarial_details = None

        if not os.path.exists(file_path):
            return DocumentValidationResult(
                is_valid=False,
                file_name=os.path.basename(file_path),
                file_type="",
                file_size_bytes=0,
                checksum="",
                error_messages=["File does not exist on disk."]
            )

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()
        file_size = os.path.getsize(file_path)

        # Read file bytes for checksum & emptiness
        with open(file_path, "rb") as f:
            content = f.read()

        checksum = self.compute_checksum(content)

        # Extension Check
        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f"Invalid file extension '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}.")

        # File Size Check
        if file_size == 0:
            errors.append("File is empty (0 bytes).")
        elif file_size > MAX_FILE_SIZE_BYTES:
            errors.append(f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed size (20 MB).")

        # Duplicate Check
        if checksum in self.existing_checksums:
            errors.append("Duplicate document detected (identical SHA-256 checksum already stored).")

        # Scan text for adversarial prompt injection
        scan_text_target = raw_text or content.decode("utf-8", errors="ignore")
        if scan_text_target:
            is_adv, detected_sigs = self.adversarial_scanner.scan_text(scan_text_target)
            if is_adv:
                is_adversarial = True
                adversarial_details = f"Prompt injection signatures detected: {', '.join(detected_sigs)}"
                warnings.append(f"Adversarial signature flagged: {adversarial_details}")

        is_valid = len(errors) == 0 and not is_adversarial

        return DocumentValidationResult(
            is_valid=is_valid,
            file_name=file_name,
            file_type=ext,
            file_size_bytes=file_size,
            checksum=checksum,
            error_messages=errors,
            warnings=warnings,
            is_adversarial=is_adversarial,
            adversarial_details=adversarial_details
        )
