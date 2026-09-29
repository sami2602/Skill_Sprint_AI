"""
SkillSprint AI — Semantic Text Chunker
Splits parsed document text into traceable chunks while retaining metadata and citation boundaries.
"""

import hashlib
from typing import List, Dict, Any
from backend.schemas.schemas import DocumentChunkSchema


class SemanticChunker:
    """Chunks text preserving headings, page numbers, paragraph references, and section boundaries."""

    def __init__(self, target_chunk_words: int = 200, overlap_words: int = 30):
        self.target_chunk_words = target_chunk_words
        self.overlap_words = overlap_words

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def chunk_pdf_doc(self, doc_id: str, parsed_pdf: Dict[str, Any]) -> List[DocumentChunkSchema]:
        """Chunks parsed PDF document keeping page numbers intact."""
        chunks = []
        chunk_idx = 0

        pages = parsed_pdf.get("pages", [])
        if not pages or all(not p.get("text") for p in pages):
            full_text = parsed_pdf.get("full_text", "")
            if full_text:
                pages = [{"page_number": 1, "text": full_text}]

        step_size = max(1, self.target_chunk_words - self.overlap_words)
        for page in pages:
            page_num = page["page_number"]
            text = page["text"]

            words = text.split()
            if not words:
                continue

            for start in range(0, len(words), step_size):
                chunk_words = words[start:start + self.target_chunk_words]
                chunk_text = " ".join(chunk_words)

                chunk_id = f"CHK-{doc_id}-P{page_num}-{chunk_idx:03d}"
                chunks.append(DocumentChunkSchema(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    section_id=f"SEC-P{page_num}",
                    heading=f"Page {page_num} Content",
                    text_content=chunk_text,
                    page_number=page_num,
                    paragraph_ref=None,
                    chunk_index=chunk_idx,
                    token_count=len(chunk_words),
                    checksum=self._hash_text(chunk_text)
                ))
                chunk_idx += 1

        return chunks

    def chunk_docx_doc(self, doc_id: str, parsed_docx: Dict[str, Any]) -> List[DocumentChunkSchema]:
        """Chunks parsed DOCX document keeping paragraph references intact."""
        chunks = []
        chunk_idx = 0

        current_words = []
        current_heading = "General"
        start_para_ref = "Para 1"

        for p_data in parsed_docx.get("paragraphs", []):
            p_ref = p_data["paragraph_ref"]
            heading = p_data["heading"]
            p_text = p_data["text"]

            if not current_words:
                start_para_ref = p_ref
                current_heading = heading

            words = p_text.split()
            current_words.extend(words)

            if len(current_words) >= self.target_chunk_words:
                chunk_text = " ".join(current_words)
                chunk_id = f"CHK-{doc_id}-{chunk_idx:03d}"
                chunks.append(DocumentChunkSchema(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    section_id="SEC-01",
                    heading=current_heading,
                    text_content=chunk_text,
                    page_number=None,
                    paragraph_ref=start_para_ref,
                    chunk_index=chunk_idx,
                    token_count=len(current_words),
                    checksum=self._hash_text(chunk_text)
                ))
                chunk_idx += 1
                current_words = current_words[-self.overlap_words:]

        if current_words:
            chunk_text = " ".join(current_words)
            chunk_id = f"CHK-{doc_id}-{chunk_idx:03d}"
            chunks.append(DocumentChunkSchema(
                chunk_id=chunk_id,
                doc_id=doc_id,
                section_id="SEC-01",
                heading=current_heading,
                text_content=chunk_text,
                page_number=None,
                paragraph_ref=start_para_ref,
                chunk_index=chunk_idx,
                token_count=len(current_words),
                checksum=self._hash_text(chunk_text)
            ))

        return chunks

    def chunk_text(self, text: str, doc_id: str, section_id: str = "SEC-01") -> List[DocumentChunkSchema]:
        """Chunks generic text string into DocumentChunkSchema instances."""
        words = text.split()
        if not words:
            return []

        chunks = []
        step_size = max(1, self.target_chunk_words - self.overlap_words)
        chunk_idx = 0

        for start in range(0, len(words), step_size):
            chunk_words = words[start:start + self.target_chunk_words]
            chunk_str = " ".join(chunk_words)
            chunk_id = f"CHK-{doc_id}-{chunk_idx:03d}"
            chunks.append(DocumentChunkSchema(
                chunk_id=chunk_id,
                doc_id=doc_id,
                section_id=section_id,
                heading=f"Section {section_id} Content",
                text_content=chunk_str,
                page_number=1,
                paragraph_ref=None,
                chunk_index=chunk_idx,
                token_count=len(chunk_words),
                checksum=self._hash_text(chunk_str)
            ))
            chunk_idx += 1

        return chunks

