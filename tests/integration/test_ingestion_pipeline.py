"""
SkillSprint AI — Integration Tests for Ingestion Pipeline
"""

import os
import pytest
from document_processing.validation.validator import DocumentValidator
from document_processing.parsers.pdf_parser import PDFParser
from document_processing.chunking.semantic_chunker import SemanticChunker
from document_processing.provenance.metadata_manager import MetadataManager
from backend.schemas.schemas import DocumentBase
from scripts.seed_dataset import create_dummy_pdf


def test_full_ingestion_pipeline_flow(tmp_path):
    pdf_path = str(tmp_path / "DOC-POL01.pdf")
    doc_id = "DOC-POL01"
    title = "Information Security Policy v2.0"
    content = "Section 1: Security Overview\nEmployees must use 2FA.\nSection 2: Incident Response\nReport breaches immediately."

    create_dummy_pdf(pdf_path, title, content)

    # 1. Validate
    validator = DocumentValidator()
    val_result = validator.validate_file(pdf_path, content)
    assert val_result.is_valid is True

    # 2. Parse
    parser = PDFParser()
    parsed_pdf = parser.parse(pdf_path)
    assert parsed_pdf["total_pages"] >= 1

    # 3. Chunk
    chunker = SemanticChunker(target_chunk_words=15)
    chunks = chunker.chunk_pdf_doc(doc_id, parsed_pdf)
    assert len(chunks) >= 1

    # 4. Provenance Metadata Tagging
    meta_mgr = MetadataManager()
    doc_base = DocumentBase(
        doc_id=doc_id,
        title=title,
        category="Security",
        file_type=".pdf",
        version="2.0",
        effective_date="2026-01-01"
    )

    enriched = meta_mgr.attach_provenance(chunks[0], doc_base)
    assert meta_mgr.verify_provenance_completeness(enriched) is True
    assert enriched["doc_id"] == doc_id
    assert "DOC-POL01" in enriched["location_citation"]
