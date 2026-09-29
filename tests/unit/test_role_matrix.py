"""
SkillSprint AI — Unit Tests for Role Requirement Matrix Builder & Unseen Role Handling
"""

import pytest
from backend.app.database import Base, engine, SessionLocal
from backend.models.models import Role, PolicyRequirement, Document, RequirementCategoryEnum, PriorityEnum, ValidationStatusEnum
from knowledge.roles.matrix_builder import RoleMatrixBuilder
from scripts.seed_dataset import seed_database


@pytest.fixture(autouse=True)
def setup_db():
    seed_database()
    yield


def test_matrix_builder_existing_role():
    db = SessionLocal()
    mb = RoleMatrixBuilder(db)
    matrix = mb.build_matrix_for_role("ROL-01")

    assert matrix["role_id"] == "ROL-01"
    assert matrix["mandatory_requirement_count"] > 0
    assert matrix["total_requirement_count"] >= matrix["mandatory_requirement_count"]
    db.close()


def test_matrix_builder_unseen_role_handling():
    db = SessionLocal()
    mb = RoleMatrixBuilder(db)
    # Unseen role during hidden evaluation (HE-01)
    unseen_matrix = mb.build_matrix_for_role("ROL-CYBER-SPECIALIST")

    assert unseen_matrix["role_id"] == "ROL-CYBER-SPECIALIST"
    assert unseen_matrix["mandatory_requirement_count"] >= 0
    assert "mandatory_items" in unseen_matrix
    db.close()
