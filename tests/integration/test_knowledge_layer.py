"""
SkillSprint AI — Integration Tests for Knowledge Model & Ground-Truth Evidence Layer
"""

import pytest
from backend.app.database import SessionLocal
from knowledge.retrieval.ground_truth import GroundTruthRetrievalService
from knowledge.roles.matrix_builder import RoleMatrixBuilder
from knowledge.conflicts.resolver import ConflictResolver
from scripts.seed_dataset import seed_database


@pytest.fixture(autouse=True)
def setup_db():
    seed_database()
    yield


def test_full_knowledge_layer_integration():
    db = SessionLocal()
    gt_service = GroundTruthRetrievalService(db)

    # 1. Test validation evidence calculation for ROL-01
    evidence = gt_service.calculate_validation_evidence("ROL-01")

    assert "mandatory_total" in evidence
    assert evidence["mandatory_total"] > 0
    assert "coverage_score" in evidence
    assert "traceability_score" in evidence
    assert "verification_status" in evidence

    # 2. Test conflict scanner integration
    resolver = ConflictResolver(db)
    scan = resolver.scan_for_conflicts()
    assert scan["total_conflicts"] >= 0

    # 3. Test matrix builder summary
    mb = RoleMatrixBuilder(db)
    summaries = mb.get_ground_truth_matrix_summary()
    assert len(summaries) >= 10

    db.close()
