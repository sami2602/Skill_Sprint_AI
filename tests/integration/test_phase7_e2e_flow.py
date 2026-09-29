"""
SkillSprint AI — Phase 7 Integration Flow Tests
Verifies full end-to-end integration workflows through the production FastAPI backend endpoints:
Flow 1: Document -> Requirements -> Role -> Employee -> Generation -> Validation -> Comparison -> Review -> Approval -> Audit
Flow 2: Policy Update -> Impact Analysis -> Affected Content -> Selective Regeneration -> Revalidation -> Audit
"""

import pytest
from backend.app.database import SessionLocal
from backend.models.models import Document, Role, PolicyRequirement, Employee, GeneratedPlan


def get_token(client, username="admin", password="AdminPass123!"):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.json()}"
    return login_res.json()["access_token"]


def test_phase7_end_to_end_flow_1(client):
    """
    Flow 1: DOCUMENT -> REQUIREMENTS -> ROLE -> EMPLOYEE -> GENERATION -> VALIDATION -> COMPARISON -> REVIEW -> APPROVAL -> AUDIT
    """
    token = get_token(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch available Roles
    roles_res = client.get("/api/v1/roles", headers=headers)
    assert roles_res.status_code == 200
    roles = roles_res.json()["items"]
    assert len(roles) > 0
    test_role = roles[0]
    role_id = test_role["role_id"]

    # 2. Fetch or Create Employee
    emp_res = client.get(f"/api/v1/employees?role_id={test_role['id']}", headers=headers)
    assert emp_res.status_code == 200
    emps = emp_res.json()["items"]
    if emps:
        emp_id = emps[0]["employee_id"]
    else:
        create_emp_res = client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "employee_id": "EMP-FLOW-01",
                "name": "Integration Test Learner",
                "email": "flow_learner@skillsprint.ai",
                "role_id": test_role["id"],
                "department": test_role["department"],
                "experience_level": "Junior",
                "joining_date": "2026-01-15"
            }
        )
        assert create_emp_res.status_code in [201, 409]
        emp_id = "EMP-FLOW-01"

    # 3. Trigger Onboarding Plan Generation
    gen_res = client.post(
        "/api/v1/generation/plan",
        headers=headers,
        json={
            "role_id": role_id,
            "employee_id": emp_id,
            "experience_level": "Junior",
            "department": test_role["department"]
        }
    )
    assert gen_res.status_code == 201
    plan_data = gen_res.json()
    plan_id = plan_data["plan_id"]
    assert plan_id.startswith("PLAN-")

    # 4. Trigger Ground-Truth Python Validation
    val_res = client.post(
        f"/api/v1/validation/run?plan_id={plan_id}",
        headers=headers
    )
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert "coverage_score" in val_data
    assert "verification_status" in val_data

    # 5. Fetch Requirement Comparison Report
    comp_res = client.get(f"/api/v1/verification/comparison/{plan_id}", headers=headers)
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["plan_id"] == plan_id

    # 6. Fetch Verification Summary
    sum_res = client.get(f"/api/v1/verification/summary/{plan_id}", headers=headers)
    assert sum_res.status_code == 200
    assert "verification_status" in sum_res.json()

    # 7. Check Review Queue & Perform Reviewer Action
    rev_token = get_token(client, "reviewer", "ReviewerPass123!")
    rev_headers = {"Authorization": f"Bearer {rev_token}"}
    queue_res = client.get(f"/api/v1/review/queue?plan_id={plan_id}", headers=rev_headers)
    assert queue_res.status_code == 200
    queue_items = queue_res.json()

    if queue_items:
        review_item = queue_items[0]
        action_res = client.post(
            "/api/v1/review/action",
            headers=rev_headers,
            json={
                "review_id": review_item["review_id"],
                "action": "APPROVE",
                "reviewer_id": "USR-REV-01",
                "comment": "Approved item during integration test flow."
            }
        )
        assert action_res.status_code == 200

    # 8. Verify Immutable Audit Trail Entries Captured
    audit_res = client.get(f"/api/v1/audit/history?entity_id={plan_id}", headers=headers)
    assert audit_res.status_code == 200
    audit_items = audit_res.json()["items"]
    assert len(audit_items) > 0


def test_phase7_end_to_end_flow_2(client):
    """
    Flow 2: POLICY UPDATE -> IMPACT ANALYSIS -> AFFECTED CONTENT -> SELECTIVE REGENERATION -> REVALIDATION -> AUDIT
    """
    token = get_token(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    try:
        doc = db.query(Document).first()
        if not doc:
            pytest.skip("No document found in database for policy update test.")
        doc_id = doc.doc_id
        old_version = doc.version
        new_version = "2.0"
    finally:
        db.close()

    # 1. Analyze Policy Impact
    impact_res = client.post(
        "/api/v1/policy-impact/analyze",
        headers=headers,
        json={
            "doc_id": doc_id,
            "new_version": new_version,
            "old_version": old_version
        }
    )
    assert impact_res.status_code == 200
    impact_data = impact_res.json()
    assert impact_data["doc_id"] == doc_id
    assert "affected_roles" in impact_data

    # 2. Get a generated plan for selective regeneration
    plans_res = client.get("/api/v1/generation/plans", headers=headers)
    plans = plans_res.json()["items"]
    if not plans:
        pytest.skip("No generated plan found for selective regeneration test.")
    test_plan = plans[0]

    # 3. Execute Selective Regeneration
    regen_res = client.post(
        "/api/v1/policy-impact/selective-regenerate",
        headers=headers,
        json={
            "plan_id": test_plan["plan_id"],
            "doc_id": doc_id,
            "old_version": old_version,
            "new_version": new_version,
            "affected_module_ids": ["MOD-01"],
            "reason": "Policy update v2.0 selective regeneration test"
        }
    )
    assert regen_res.status_code == 200
    regen_data = regen_res.json()
    assert regen_data["plan_id"] == test_plan["plan_id"]

    # 4. Revalidate Selective Regenerated Plan
    val_res = client.post(
        f"/api/v1/validation/run?plan_id={test_plan['plan_id']}",
        headers=headers
    )
    assert val_res.status_code == 200

    # 5. Verify Audit Trail Recorded
    audit_res = client.get(f"/api/v1/audit/history?entity_id={test_plan['plan_id']}", headers=headers)
    assert audit_res.status_code == 200
    assert len(audit_res.json()["items"]) > 0
