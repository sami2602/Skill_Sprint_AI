"""
SkillSprint AI — Unit Tests for Document Validator
"""

import os
import pytest
from document_processing.validation.validator import DocumentValidator


def test_validator_valid_file(tmp_path):
    f_path = str(tmp_path / "valid.pdf")
    with open(f_path, "w") as f:
        f.write("Sample content for validation test.")

    validator = DocumentValidator()
    result = validator.validate_file(f_path)

    assert result.is_valid is True
    assert result.file_size_bytes > 0
    assert len(result.error_messages) == 0


def test_validator_invalid_extension(tmp_path):
    f_path = str(tmp_path / "invalid.exe")
    with open(f_path, "w") as f:
        f.write("Binary content")

    validator = DocumentValidator()
    result = validator.validate_file(f_path)

    assert result.is_valid is False
    assert any("Invalid file extension" in err for err in result.error_messages)


def test_validator_duplicate_detection(tmp_path):
    f_path = str(tmp_path / "dup.pdf")
    content = b"Exact duplicate content"
    with open(f_path, "wb") as f:
        f.write(content)

    validator = DocumentValidator()
    checksum = validator.compute_checksum(content)
    validator_dup = DocumentValidator(existing_checksums=[checksum])

    result = validator_dup.validate_file(f_path)
    assert result.is_valid is False
    assert any("Duplicate document" in err for err in result.error_messages)
