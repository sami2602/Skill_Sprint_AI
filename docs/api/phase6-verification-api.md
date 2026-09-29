# SkillSprint AI — Phase 6 Verification, Review & Audit API Specification

## Overview
This document specifies the REST API endpoints and data schemas implemented in **Phase 6** of **SkillSprint AI** for requirement comparison, verification summary, human review workflow, reviewer overrides, audit history, policy impact analysis, and selective regeneration.

Base Path: `/api/v1`

---

## 1. Requirement Comparison Report
- **URL**: `GET /api/v1/comparison/{plan_id}`
- **Description**: Generates an itemized requirement-level comparison report between ground-truth matrix expectations, GenAI output, and Python validator findings.
- **SRS Alignment**: FR-42

### Response Schema (`RequirementComparisonReport`):
```json
{
  "plan_id": "PLAN-P6-001",
  "role_id": "ROL-01",
  "generated_at": "2026-09-27T21:20:00Z",
  "summary": {
    "total_evaluated": 15,
    "covered": 14,
    "missing_mandatory": 1,
    "partially_covered": 0,
    "unsupported": 0,
    "contradictory": 0,
    "outdated_sources": 0,
    "irrelevant": 0,
    "needs_review": 0,
    "coverage_percentage": 93.33
  },
  "items": [
    {
      "requirement_id": "REQ-001",
      "title": "Password Complexity Policy",
      "requirement_text": "Passwords must contain 12+ characters.",
      "is_mandatory": true,
      "role_id": "ROL-01",
      "expected_behavior": "Ground truth requires 'REQ-001' to be covered for role 'ROL-01'.",
      "generated_behavior": "Covered by 1 item(s): TASK 'Configure Strong Password' (Day 1)",
      "generated_content": "Covered by 1 item(s): TASK 'Configure Strong Password' (Day 1)",
      "generated_coverage": "FULL",
      "source_doc_id": "DOC-POL01",
      "source_version": "1.0",
      "source_location": "SEC-01",
      "validation_rule": "MandatoryCoverageRule",
      "validation_result": "PASSED",
      "result_status": "COVERED",
      "evidence": "Expected: Satisfy REQ-001 -> Generated: Covered -> Validated: PASSED -> Decision: COVERED",
      "reviewer_status": null,
      "reviewer_id": null,
      "reviewer_comment": null,
      "override_reason": null
    }
  ]
}
```

---

## 2. Dynamic Verification Summary
- **URL**: `GET /api/v1/verification/summary/{plan_id}`
- **Description**: Calculates exact numeric metrics for coverage, traceability, hallucinations, contradictions, outdated sources, and verification status.
- **SRS Alignment**: FR-43

### Response Schema (`VerificationSummarySchema`):
```json
{
  "plan_id": "PLAN-P6-001",
  "role_id": "ROL-01",
  "total_requirements": 15,
  "mandatory_requirements": 12,
  "mandatory_covered": 12,
  "mandatory_missing": 0,
  "coverage_percentage": 100.0,
  "traceable_items": 10,
  "untraceable_items": 0,
  "traceability_percentage": 100.0,
  "unsupported_items": 0,
  "duplicate_items": 0,
  "contradictions": 0,
  "outdated_sources": 0,
  "role_irrelevance": 0,
  "sequence_errors": 0,
  "verification_status": "VERIFIED",
  "explanation": "100% Mandatory Coverage satisfied. All content items grounded in active policy sources with zero sequence, contradiction, or quiz errors."
}
```

---

## 3. Manual Review Queue & Reviewer Actions
- **URL**: `GET /api/v1/review-queue`
- **Description**: Returns list of pending items flagged for review.
- **SRS Alignment**: FR-44

- **URL**: `GET /api/v1/review-queue/inspect/{plan_id}/{item_id}`
- **Description**: Returns itemized evidence chain for reviewer inspection: `Expected -> Generated -> Validated -> Decision`.

- **URL**: `POST /api/v1/review-queue/action`
- **Description**: Applies reviewer action (`APPROVE`, `REJECT`, `REQUEST_REVISION`, `OVERRIDE`) and writes append-only audit trail.
- **SRS Alignment**: FR-44, FR-45

---

## 4. Immutable Audit Trail History
- **URL**: `GET /api/v1/audit/history`
- **Description**: Retrieves audit trail logs for event types (`DOCUMENT_CHANGE`, `POLICY_VERSION_CHANGE`, `GENERATION_EVENT`, `VALIDATION_EVENT`, `COMPARISON_EVENT`, `VERIFICATION_DECISION`, `REVIEWER_ACTION`, `OVERRIDE`, `REGENERATION_EVENT`).
- **SRS Alignment**: FR-45

---

## 5. Policy Impact Analysis
- **URL**: `POST /api/v1/policy-impact/analyze`
- **Description**: Calculates affected requirements, roles, onboarding plans, modules, tasks, and quizzes following document updates.
- **SRS Alignment**: FR-53, FR-54

---

## 6. Selective Regeneration Request
- **URL**: `POST /api/v1/plans/selective-regenerate`
- **Description**: Regenerates targeted affected modules while leaving untouched modules preserved.
- **SRS Alignment**: FR-55
