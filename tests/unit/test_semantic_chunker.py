"""
SkillSprint AI — Unit Tests for Semantic Chunker
"""

import pytest
from document_processing.chunking.semantic_chunker import SemanticChunker


def test_chunk_pdf_doc():
    chunker = SemanticChunker(target_chunk_words=10, overlap_words=2)
    parsed_pdf = {
        "pages": [
            {"page_number": 1, "text": "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10 Word11 Word12"}
        ]
    }

    chunks = chunker.chunk_pdf_doc("DOC-01", parsed_pdf)
    assert len(chunks) >= 1
    assert chunks[0].page_number == 1
    assert chunks[0].doc_id == "DOC-01"
    assert chunks[0].checksum is not None


def test_chunk_docx_doc():
    chunker = SemanticChunker(target_chunk_words=10, overlap_words=2)
    parsed_docx = {
        "paragraphs": [
            {"paragraph_ref": "Para 1", "heading": "Heading 1", "text": "This is paragraph one text content for testing semantic chunker."},
            {"paragraph_ref": "Para 2", "heading": "Heading 2", "text": "This is paragraph two text content for testing semantic chunker."}
        ]
    }

    chunks = chunker.chunk_docx_doc("DOC-02", parsed_docx)
    assert len(chunks) >= 1
    assert chunks[0].paragraph_ref == "Para 1"
    assert chunks[0].doc_id == "DOC-02"
