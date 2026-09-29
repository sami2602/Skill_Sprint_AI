# SkillSprint AI — API Architecture Specification

## Overview
This document specifies the RESTful API endpoints, request/response schemas, status codes, and authorization requirements for **SkillSprint AI** as required by Step 12 of the SRS Discovery Phase.

All endpoints adhere to OpenAPI 3.0 standards via FastAPI.

---

## 1. Authentication & Security Endpoints (`/api/v1/auth`)

### `POST /api/v1/auth/login`
- **Summary**: User login & JWT token issuance.
- **Request Body**: `{ "username": "user@skillsprint.ai", "password": "SecretPassword123!" }`
- **Response 200**: `{ "access_token": "eyJhbG...", "token_type": "bearer", "user": { "user_id": "U-01", "role": "Admin" } }`
- **Response 401**: `{ "detail": "Invalid credentials" }`

---

## 2. Document Ingestion Endpoints (`/api/v1/documents`)

### `POST /api/v1/documents/upload`
- **Summary**: Upload PDF or DOCX file.
- **RBAC Role**: `Admin`, `TrainingManager`
- **Form Data**: `file`: Multipart binary, `category`: string, `department`: string, `effective_date`: date
- **Response 200**: `{ "document_id": "DOC-01", "title": "Employee Handbook", "file_type": "pdf", "chunks_count": 42, "status": "PARSED" }`

### `POST /api/v1/documents/policy-update`
- **Summary**: Upload replacement policy version file and trigger impact analysis.
- **RBAC Role**: `Admin`
- **Form Data**: `old_doc_id`: string, `file`: Multipart binary
- **Response 200**: `{ "obsolete_doc_id": "DOC-02", "new_doc_id": "DOC-03", "affected_plans_count": 12, "affected_modules_count": 3 }`

---

## 3. Role & Requirement Matrix Endpoints (`/api/v1/roles`)

### `GET /api/v1/roles`
- **Summary**: List all configured job roles (>= 10 roles).
- **Response 200**: `[ { "role_id": "ROLE-SUP-01", "role_name": "Customer Support Executive", "department": "Customer Success" } ]`

### `GET /api/v1/role-matrix/{role_id}`
- **Summary**: Retrieve ground-truth Role Requirement Matrix for a specific job role.
- **Response 200**: `{ "role_id": "ROLE-SUP-01", "mandatory_requirements_count": 8, "matrix": [ { "requirement_id": "REQ-SEC-01", "is_mandatory": true, "due_stage": "Day 1", "source_document_id": "DOC-04" } ] }`

---

## 4. Onboarding Plan Generation Endpoints (`/api/v1/plans`)

### `POST /api/v1/plans/generate`
- **Summary**: Trigger Pipeline 1 (GenAI Plan Generator) for a given employee and role.
- **RBAC Role**: `Admin`, `TrainingManager`
- **Request Body**: `{ "employee_id": "EMP-101", "role_id": "ROLE-SUP-01" }`
- **Response 200**: `{ "plan_id": "PLAN-99", "verification_status": "Verified", "coverage_score": 100.0, "traceability_score": 100.0, "stages_count": 6 }`

### `POST /api/v1/plans/regenerate-selective`
- **Summary**: Trigger selective regeneration of specified affected modules only.
- **Request Body**: `{ "plan_ids": ["PLAN-99"], "module_ids": ["MOD-04"] }`
- **Response 200**: `{ "regenerated_modules": ["MOD-04"], "plan_status": "Verified" }`

---

## 5. Python Validation & Comparison Endpoints (`/api/v1/validation`)

### `POST /api/v1/validation/run`
- **Summary**: Run Pipeline 2 (Independent Python Ground-Truth Validator - 0 GenAI API calls).
- **Request Body**: `{ "plan_id": "PLAN-99" }`
- **Response 200**: `{ "coverage_score": 100.0, "traceability_score": 100.0, "missing_requirements": [], "unsupported_claims": [], "contradictions": [], "verification_status": "Verified" }`

### `GET /api/v1/comparison/{plan_id}`
- **Summary**: Retrieve 100+ item match/mismatch comparison report matrix between GenAI JSON and Python expected rules.
- **Response 200**: `{ "plan_id": "PLAN-99", "total_items_compared": 105, "matches_count": 105, "mismatches_count": 0, "matrix": [ ... ] }`

---

## 6. Manual Review Queue & Audit Endpoints (`/api/v1/review-queue`)

### `GET /api/v1/review-queue`
- **Summary**: Fetch flagged onboarding plans requiring manual human reviewer action.
- **RBAC Role**: `Admin`, `Reviewer`
- **Response 200**: `[ { "plan_id": "PLAN-12", "reason": "UNSUPPORTED_FACTUAL_CLAIM", "flagged_item": "Task #3" } ]`

### `POST /api/v1/review-queue/override`
- **Summary**: Submit reviewer decision (Approve, Reject, Edit, Regenerate) with commentary; logs to immutable audit trail.
- **RBAC Role**: `Admin`, `Reviewer`
- **Request Body**: `{ "item_id": "TSK-03", "decision": "APPROVED_WITH_OVERRIDE", "comment": "Ungrounded optional task approved by HR manager." }`
- **Response 200**: `{ "status": "APPROVED", "audit_event_id": "AUD-88" }`

---

## 7. Reports & Export Endpoints (`/api/v1/reports`)

### `GET /api/v1/reports/export`
- **Summary**: Export onboarding, coverage, assessment, or validation reports in CSV, PDF, or XLSX format.
- **Query Params**: `type=coverage&format=pdf`
- **Response 200**: Binary File Download (`Content-Type: application/pdf`)
