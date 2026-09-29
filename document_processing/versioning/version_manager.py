"""
SkillSprint AI — Policy Version Control Manager
Distinguishes active policy versions from obsolete versions when company policies update.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.models import Document, PolicyVersionHistory


class VersionManager:
    """Manages document versioning lifecycle (FR-10)."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def process_policy_update(
        self,
        doc_id: str,
        new_version: str,
        new_file_path: str,
        change_summary: str = ""
    ) -> Dict[str, Any]:
        """
        Handles document version update:
        1. Marks older active document version as obsolete (`is_active = False`).
        2. Logs entry to `policy_version_history`.
        """
        old_doc = self.db.query(Document).filter(
            Document.doc_id == doc_id,
            Document.is_active == True
        ).first()

        old_version = "None"
        if old_doc:
            old_version = old_doc.version
            old_doc.is_active = False

        # Log version history
        history_entry = PolicyVersionHistory(
            doc_id=doc_id,
            old_version=old_version,
            new_version=new_version,
            change_summary=change_summary
        )
        self.db.add(history_entry)
        self.db.commit()

        return {
            "doc_id": doc_id,
            "old_version": old_version,
            "new_version": new_version,
            "status": "SUPERSEDED_AND_LOGGED"
        }

    def get_active_documents(self) -> List[Document]:
        """Returns all currently active policy documents."""
        return self.db.query(Document).filter(Document.is_active == True).all()
