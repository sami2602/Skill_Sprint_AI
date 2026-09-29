"""
SkillSprint AI — Security & Robustness Suite: Malformed Inputs & RBAC Authorization Matrix (Items 9 & 10)
Verifies safe failure behavior for malformed inputs and independent backend authorization enforcement for all roles.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from security.auth import create_access_token
from document_processing.validation.validator import DocumentValidator


client = TestClient(app)


def get_auth_header(role: str, user_id: str):
    token = create_access_token(data={"sub": user_id, "role": role, "email": f"{user_id}@skillsprint.ai"})
    return {"Authorization": f"Bearer {token}"}


# =====================================================================
# Item 9: Malformed Input Tests
# =====================================================================

def test_malformed_json_plan_generation():
    """Verifies backend returns 422 Unprocessable Entity on malformed JSON payload."""
    headers = get_auth_header("ADMIN", "admin")
    response = client.post(
        "/api/v1/generation/plan",
        content="{\"role_id\": \"ROL-01\", \"employee_id\": ", # Malformed JSON!
        headers={**headers, "Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_doc_validator_unsupported_and_corrupt_files():
    """Verifies DocumentValidator rejects invalid file extensions and empty 0-byte files safely."""
    validator = DocumentValidator()

    # 1. Unsupported extension
    res_ext = validator.validate_file("test.exe", b"executable content")
    assert res_ext.is_valid is False
    assert len(res_ext.error_messages) > 0

    # 2. Empty / corrupt file (0 bytes)
    res_empty = validator.validate_file("empty.pdf", b"")
    assert res_empty.is_valid is False
    assert len(res_empty.error_messages) > 0


# =====================================================================
# Item 10: Authorization Testing (ADMIN, REVIEWER, MANAGER, EMPLOYEE)
# =====================================================================

def test_employee_cannot_perform_reviewer_action():
    """Verifies EMPLOYEE role is forbidden (403) from applying reviewer decisions."""
    headers = get_auth_header("EMPLOYEE", "employee")
    action_payload = {
        "item_id": "ITEM-001",
        "plan_id": "PLAN-01",
        "action": "APPROVE",
        "reason": "Employee override attempt"
    }
    response = client.post("/api/v1/review/action", json=action_payload, headers=headers)
    assert response.status_code == 403


def test_employee_cannot_perform_audit_query():
    """Verifies EMPLOYEE role is forbidden (403) from querying audit history."""
    headers = get_auth_header("EMPLOYEE", "employee")
    response = client.get("/api/v1/audit/history", headers=headers)
    assert response.status_code == 403


def test_admin_can_access_admin_system_analytics():
    """Verifies ADMIN role can access system analytics."""
    headers = get_auth_header("ADMIN", "admin")
    response = client.get("/api/v1/analytics/system", headers=headers)
    assert response.status_code == 200


def test_reviewer_can_access_review_queue():
    """Verifies REVIEWER role can access review queue."""
    headers = get_auth_header("REVIEWER", "reviewer")
    response = client.get("/api/v1/review/queue", headers=headers)
    assert response.status_code == 200


def test_unauthenticated_request_rejected():
    """Verifies request without Authorization header returns 401 Unauthorized."""
    response = client.get("/api/v1/review/queue")
    assert response.status_code == 401
