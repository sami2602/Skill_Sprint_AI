"""
SkillSprint AI — Unit Tests for Conflict & Ambiguity Detection Engine
"""

import pytest
from backend.app.database import SessionLocal
from knowledge.conflicts.resolver import ConflictResolver
from scripts.seed_dataset import seed_database


@pytest.fixture(autouse=True)
def setup_db():
    seed_database()
    yield


def test_conflict_scan_execution():
    db = SessionLocal()
    resolver = ConflictResolver(db)
    scan_results = resolver.scan_for_conflicts()

    assert "total_conflicts" in scan_results
    assert "ambiguous_clauses_count" in scan_results
    assert scan_results["ambiguous_clauses_count"] >= 0
    assert "outdated_sources_count" in scan_results
    db.close()
