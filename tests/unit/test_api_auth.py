"""
SkillSprint AI — Unit Tests for Authentication & Authorization API Endpoints
"""

import uuid
import pytest
from backend.app.database import SessionLocal
from backend.models.models import User
from security.auth import hash_password


@pytest.fixture(autouse=True)
def setup_test_users():
    """Seeds test database with sample accounts for auth testing."""
    db = SessionLocal()
    try:
        db.query(User).filter(
            (User.username.in_(["testadmin", "testreviewer", "testemployee", "sarah_connor", "john_doe"])) |
            (User.email.in_(["sarah.connor@skillsprint.ai", "john.doe@skillsprint.ai"]))
        ).delete(synchronize_session=False)
        db.commit()

        u_admin = User(
            user_id="USR-TEST-ADMIN",
            username="testadmin",
            email="testadmin@skillsprint.ai",
            hashed_password=hash_password("AdminPass123!"),
            role="ADMIN",
            is_active=True
        )
        u_reviewer = User(
            user_id="USR-TEST-REV",
            username="testreviewer",
            email="testreviewer@skillsprint.ai",
            hashed_password=hash_password("ReviewerPass123!"),
            role="REVIEWER",
            is_active=True
        )
        u_employee = User(
            user_id="USR-TEST-EMP",
            username="testemployee",
            email="testemployee@skillsprint.ai",
            hashed_password=hash_password("EmployeePass123!"),
            role="EMPLOYEE",
            is_active=True
        )
        db.add_all([u_admin, u_reviewer, u_employee])
        db.commit()
    finally:
        db.close()


def test_valid_login(client):
    """Verifies valid user login returns 200 and access_token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testadmin", "password": "AdminPass123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "ADMIN"


def test_invalid_login(client):
    """Verifies invalid password returns 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testadmin", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert "Incorrect username" in response.json()["error"]["message"]


def test_unauthenticated_protected_endpoint(client):
    """Verifies protected endpoint returns 401 when Bearer token is missing."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_rbac_admin_endpoint_as_employee(client):
    """Verifies Employee role is blocked with 403 Forbidden on Admin endpoint."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "testemployee", "password": "EmployeePass123!"}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["error"]["message"]


def test_rbac_admin_endpoint_as_admin(client):
    """Verifies Admin role successfully accesses Admin user listing endpoint."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "testadmin", "password": "AdminPass123!"}
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "items" in response.json()


def test_signup_active_employee_success(client):
    """Verifies that an active company employee can register an account."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "sarah_connor",
            "email": "sarah.connor@skillsprint.ai",
            "password": "SarahPassword123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "sarah_connor"
    assert data["email"] == "sarah.connor@skillsprint.ai"
    assert data["role"] == "EMPLOYEE"


def test_signup_nonexistent_employee_rejected(client):
    """Verifies public/external users without employee records are rejected (403)."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "external_hacker",
            "email": "hacker@external.com",
            "password": "HackerPassword123!"
        }
    )
    assert response.status_code == 403
    assert "not recognized in official employee records" in response.json()["error"]["message"]


def test_signup_inactive_employee_rejected(client):
    """Verifies terminated/inactive employees are rejected (403)."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "john_doe",
            "email": "john.doe@skillsprint.ai",
            "password": "JohnPassword123!"
        }
    )
    assert response.status_code == 403
    assert "inactive/terminated" in response.json()["error"]["message"]


def test_signup_duplicate_rejected(client):
    """Verifies duplicate registration for existing account returns 409 Conflict."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "duplicate_admin",
            "email": "admin@skillsprint.ai",
            "password": "Password123!"
        }
    )
    assert response.status_code == 409


def test_database_persistence():
    """
    Explicit DB Persistence Test:
    Create record -> commit -> close database session -> create new database session -> read record -> record still exists.
    """
    session1 = SessionLocal()
    test_user_id = f"USR-PERSIST-{uuid.uuid4().hex[:6]}"
    u = User(
        user_id=test_user_id,
        username=f"persist_{uuid.uuid4().hex[:6]}",
        email=f"persist_{uuid.uuid4().hex[:6]}@skillsprint.ai",
        hashed_password=hash_password("Pass123!"),
        role="EMPLOYEE",
        is_active=True
    )
    session1.add(u)
    session1.commit()
    session1.close()

    session2 = SessionLocal()
    retrieved = session2.query(User).filter(User.user_id == test_user_id).first()
    assert retrieved is not None
    assert retrieved.user_id == test_user_id
    session2.delete(retrieved)
    session2.commit()
    session2.close()

