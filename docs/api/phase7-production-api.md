# SkillSprint AI — Phase 7 Production Backend API Documentation

## Overview
This document specifies the complete REST API interface provided by the **SkillSprint AI** production FastAPI backend server.

Base Path: `/api/v1`

---

## API Module Summary

| Module | Base Path | Description | Access Control |
| :--- | :--- | :--- | :--- |
| **Health** | `/healthz`, `/health`, `/readiness` | System health and database readiness checks | Public |
| **Auth** | `/api/v1/auth` | User login, JWT token issuance, profile lookup | Public / Bearer |
| **Users** | `/api/v1/users` | User account management & role assignment | Admin |
| **Documents** | `/api/v1/documents` | Document upload, parsing, chunking, versioning | Admin / Reviewer |
| **Requirements** | `/api/v1/requirements` | Extracted policy requirement catalog & traceability | Authenticated |
| **Roles** | `/api/v1/roles` | Job roles & Role Requirement Matrix grid | Authenticated |
| **Employees** | `/api/v1/employees` | Employee onboarding profiles & milestone status | Manager / Admin / Self |
| **Generation** | `/api/v1/generation` | GenAI onboarding plan generation & payload detail | Authenticated |
| **Validation** | `/api/v1/validation` | Ground-truth Python validation runs & evidence | Authenticated |
| **Verification** | `/api/v1/verification` | Verification summary & matrix comparison report | Authenticated |
| **Review** | `/api/v1/review` | Manual review queue inspection & reviewer overrides | Reviewer / Admin |
| **Audit** | `/api/v1/audit` | Append-only immutable audit trail history | Reviewer / Admin |
| **Policy Impact** | `/api/v1/policy-impact` | Impact analysis & selective module regeneration | Admin / Reviewer |
| **Analytics** | `/api/v1/analytics` | Organization-wide metrics & weak-area diagnostics | Authenticated |
| **Reports** | `/api/v1/reports` | Exportable validation, comparison, and security reports | Authenticated |

---

## Authentication & Authorization

All protected routes require standard HTTP Authorization header:
```
Authorization: Bearer <access_token>
```
Tokens are issued via `POST /api/v1/auth/login` and signed using HMAC-SHA256 with 24-hour expiration.

---

## Global Error Schema

All API error responses follow the standardized error payload structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error summary",
    "details": []
  },
  "timestamp": "2026-09-27T21:45:00Z"
}
```
