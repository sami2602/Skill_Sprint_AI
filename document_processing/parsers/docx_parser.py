"""
SkillSprint AI — DOCX Document Parser
Extracts plain text and section metadata from Word (.docx) documents, retaining paragraph indices and headings.
"""

import os
from typing import Dict, Any, List
import docx


class DOCXParser:
    """Parses DOCX documents retaining Section Heading and Paragraph Index (e.g. Para 4.2)."""

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parses DOCX file and returns structured extraction dictionary:
        {
            "doc_title": str,
            "paragraphs": [{"paragraph_ref": str, "text": str, "heading": str}],
            "sections": [{"section_id": str, "title": str, "paragraph_start": int}],
            "full_text": str
        }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DOCX file not found at: {file_path}")

        doc = docx.Document(file_path)
        paragraphs_data = []
        full_text_list = []
        sections = []
        current_heading = "General"

        sec_idx = 1
        para_idx = 1

        for idx, p in enumerate(doc.paragraphs):
            text = p.text.strip()
            if not text:
                continue

            style_name = p.style.name if p.style else ""
            is_heading = style_name.startswith("Heading") or text.startswith(("Section ", "SEC-", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."))

            if is_heading and len(text) < 120:
                current_heading = text
                sec_id = f"SEC-{sec_idx:02d}"
                sections.append({
                    "section_id": sec_id,
                    "title": text,
                    "paragraph_start": idx + 1
                })
                sec_idx += 1

            para_ref = f"Para {para_idx}"
            para_idx += 1

            paragraphs_data.append({
                "paragraph_ref": para_ref,
                "text": text,
                "heading": current_heading
            })
            full_text_list.append(text)

        full_text = "\n\n".join(full_text_list)
        doc_title = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")

        return {
            "doc_title": doc_title,
            "paragraphs": paragraphs_data,
            "sections": sections,
            "full_text": full_text
        }
