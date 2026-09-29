"""
SkillSprint AI — Global Pytest Configuration & Test Fixtures
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app, seed_default_users
from backend.app.database import init_db, SessionLocal
from backend.models.models import Role
from scripts.seed_dataset import seed_database


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Initializes database tables, dataset, and default user accounts for API test runs."""
    init_db()
    seed_default_users()
    db = SessionLocal()
    try:
        if db.query(Role).count() == 0:
            seed_database()
    finally:
        db.close()


@pytest.fixture
def client():
    """Provides FastAPI TestClient with initialized startup context."""
    with TestClient(app) as c:
        yield c
