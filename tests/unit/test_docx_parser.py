"""
SkillSprint AI — Unit Tests for DOCX Parser
"""

import os
import pytest
from document_processing.parsers.docx_parser import DOCXParser
from scripts.seed_dataset import create_dummy_docx


def test_docx_parser_extraction(tmp_path):
    docx_path = str(tmp_path / "test_policy.docx")
    title = "Data Protection Policy"
    content = "Section 1: Data Handling\nEmployees must handle PII with care.\nSection 2: Retention\nRetain records for 7 years."

    create_dummy_docx(docx_path, title, content)

    parser = DOCXParser()
    result = parser.parse(docx_path)

    assert result["doc_title"] is not None
    assert len(result["paragraphs"]) >= 1
    assert "Para 1" in result["paragraphs"][0]["paragraph_ref"]
