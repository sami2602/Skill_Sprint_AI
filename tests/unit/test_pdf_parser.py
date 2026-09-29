"""
SkillSprint AI — Unit Tests for PDF Parser
"""

import os
import pytest
from document_processing.parsers.pdf_parser import PDFParser
from scripts.seed_dataset import create_dummy_pdf


def test_pdf_parser_extraction(tmp_path):
    pdf_path = str(tmp_path / "test_policy.pdf")
    title = "Information Security Policy v2.0"
    content = "Section 1: Information Security Overview\nAll employees must encrypt laptop hard drives.\nSection 2: Escalations\nReport incidents within 2 hours."
    
    create_dummy_pdf(pdf_path, title, content)

    parser = PDFParser()
    result = parser.parse(pdf_path)

    assert result["doc_title"] is not None
    assert result["total_pages"] >= 1
    assert "Section 1" in result["full_text"] or "encrypt" in result["full_text"]
