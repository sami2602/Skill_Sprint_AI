"""
SkillSprint AI — Unit Tests for Policy Precedence Engine
"""

import pytest
from backend.app.database import SessionLocal
from backend.models.models import Document, ValidationStatusEnum
from knowledge.policies.precedence import PolicyPrecedenceEngine
from scripts.seed_dataset import seed_database


@pytest.fixture(autouse=True)
def setup_db():
    seed_database()
    yield


def test_policy_over_faq_precedence():
    db = SessionLocal()
    pe = PolicyPrecedenceEngine(db)

    policy_doc = Document(
        doc_id="TEST-POL-01",
        title="Expense Policy v2.0",
        category="Policy",
        file_path="dummy.pdf",
        file_type=".pdf",
        file_size_bytes=100,
        version="2.0",
        is_active=True,
        checksum="c1",
        validation_status=ValidationStatusEnum.VALIDATED
    )

    faq_doc = Document(
        doc_id="TEST-FAQ-01",
        title="Expense FAQ",
        category="FAQ",
        file_path="dummy.pdf",
        file_type=".pdf",
        file_size_bytes=100,
        version="1.0",
        is_active=True,
        checksum="c2",
        validation_status=ValidationStatusEnum.VALIDATED
    )

    resolution = pe.resolve_conflict(policy_doc, faq_doc)
    assert resolution["winner_doc_id"] == "TEST-POL-01"
    assert resolution["resolution_type"] == "CATEGORY_PRECEDENCE"
    db.close()
