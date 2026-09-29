"""
SkillSprint AI — Document Metadata & Provenance Manager
Manages document provenance tracking and citation metadata verification.
"""

from typing import Dict, Any, List
from backend.schemas.schemas import DocumentChunkSchema, DocumentBase


class MetadataManager:
    """Attaches and verifies source provenance tags on all extracted content chunks."""

    def attach_provenance(self, chunk: DocumentChunkSchema, doc_metadata: DocumentBase) -> Dict[str, Any]:
        """Enriches a text chunk with complete document provenance tags."""
        return {
            "chunk_id": chunk.chunk_id,
            "doc_id": doc_metadata.doc_id,
            "doc_title": doc_metadata.title,
            "category": doc_metadata.category,
            "version": doc_metadata.version,
            "effective_date": doc_metadata.effective_date,
            "section_id": chunk.section_id,
            "heading": chunk.heading,
            "page_number": chunk.page_number,
            "paragraph_ref": chunk.paragraph_ref,
            "location_citation": f"{doc_metadata.doc_id} (§{chunk.section_id}, {chunk.paragraph_ref or f'Page {chunk.page_number}'})",
            "text_content": chunk.text_content,
            "checksum": chunk.checksum
        }

    def verify_provenance_completeness(self, enriched_chunk: Dict[str, Any]) -> bool:
        """Verifies that all mandatory provenance attributes are present."""
        required_fields = ["doc_id", "version", "location_citation", "checksum"]
        return all(enriched_chunk.get(field) for field in required_fields)
