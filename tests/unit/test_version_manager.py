"""
SkillSprint AI — Unit Tests for Policy Version Control Manager
"""

import pytest
from backend.app.database import Base, engine, SessionLocal
from backend.models.models import Document, ValidationStatusEnum
from document_processing.versioning.version_manager import VersionManager


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_version_manager_update():
    db = SessionLocal()
    # Ensure test doc does not conflict
    db.query(Document).filter(Document.doc_id == "TEST-VERSION-DOC01").delete()
    db.commit()

    # Insert v1 document
    doc_v1 = Document(
        doc_id="TEST-VERSION-DOC01",
        title="Leave Policy v1.0",
        category="HR",
        file_path="data/documents/TEST-VERSION-DOC01.pdf",
        file_type=".pdf",
        file_size_bytes=1024,
        version="1.0",
        is_active=True,
        checksum="checksum_v1",
        validation_status=ValidationStatusEnum.VALIDATED
    )
    db.add(doc_v1)
    db.commit()

    vm = VersionManager(db)
    result = vm.process_policy_update(
        doc_id="TEST-VERSION-DOC01",
        new_version="2.0",
        new_file_path="data/documents/TEST-VERSION-DOC01_v2.pdf",
        change_summary="Updated leave days from 5 to 10."
    )

    assert result["old_version"] == "1.0"
    assert result["new_version"] == "2.0"

    # Verify v1 is now inactive
    doc_v1_updated = db.query(Document).filter(Document.id == doc_v1.id).first()
    assert doc_v1_updated.is_active is False
    db.close()
