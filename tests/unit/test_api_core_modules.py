"""
SkillSprint AI — Unit Tests for Requirements, Roles, Employees, Audit, Analytics & Reports APIs
"""

import pytest


def get_token(client, username="admin", password="AdminPass123!"):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.json()}"
    return login_res.json()["access_token"]


def test_requirements_and_roles_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Roles List
    res_roles = client.get("/api/v1/roles", headers=headers)
    assert res_roles.status_code == 200
    assert "items" in res_roles.json()

    # Requirements List
    res_reqs = client.get("/api/v1/requirements", headers=headers)
    assert res_reqs.status_code == 200
    assert "items" in res_reqs.json()


def test_employees_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/employees", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()


def test_audit_history_endpoint(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/audit/history", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()


def test_analytics_and_reports_endpoints(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Analytics
    res_analytics = client.get("/api/v1/analytics/system", headers=headers)
    assert res_analytics.status_code == 200
    data_a = res_analytics.json()
    assert "document_count" in data_a
    assert "avg_coverage_score" in data_a

    # Reports Validation
    res_report = client.get("/api/v1/reports/validation", headers=headers)
    assert res_report.status_code == 200
    assert res_report.json()["report_type"] == "VALIDATION_SUMMARY_REPORT"

    # Export CSV
    res_export = client.get("/api/v1/reports/export?report_type=validation&format=csv", headers=headers)
    assert res_export.status_code == 200
    assert "text/csv" in res_export.headers["content-type"]
