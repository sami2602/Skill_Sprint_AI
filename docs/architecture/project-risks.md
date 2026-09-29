# SkillSprint AI — Project Risk Analysis & Mitigation Matrix

## Overview
This document evaluates technical, SRS compliance, GenAI, validation, security, dataset, hidden evaluation, and competition-integrity risks for **SkillSprint AI** as required by Step 15 of the SRS Discovery Phase.

---

## Risk Analysis & Mitigation Matrix

| Risk ID | Risk Description | Category | Impact | Likelihood | Mitigation Architecture Safeguard | Required Test / Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | GenAI model returns invalid JSON syntax or missing required fields, causing backend parsing crash. | GenAI Risk | High | Medium | Enforce strict Pydantic JSON schema via API `response_schema` parameter; implement exponential backoff retry manager (`genai/retry.py`). | `tests/integration/test_retry_manager.py` |
| **RSK-02** | GenAI generates ungrounded factual claims not supported by company policy documents (Hallucination). | Hallucination Risk | High | Medium | Python Pipeline 2 hallucination detector verifies all factual statements against extracted document chunks; flags ungrounded items as `Unsupported`. | `tests/unit/test_hallucination.py` |
| **RSK-03** | Uploaded document contains prompt injection attack payload attempting to override system instructions. | Security Risk | High | Medium | Pre-scan documents with adversarial scanner (`security/adversarial_detector.py`); wrap document text inside `<untrusted_document_data>` tags in prompt templates. | `tests/security/test_prompt_injection.py` |
| **RSK-04** | Python Ground-Truth Validator calls GenAI API for verification, violating Dual-Pipeline Isolation. | SRS Compliance Risk | Critical | Low | Strict package separation (`validation/` has zero imports from `genai/`); Pytest network interceptor enforces 0 outbound HTTP calls during validation runs. | `tests/unit/test_python_validation.py` |
| **RSK-05** | Onboarding plan assignment assigns all mandatory training modules to Day 1, overloading learner. | SRS Compliance Risk | Medium | Low | Stage builder enforces multi-stage timeline distribution rules (Day 1, Week 1, Week 2, 30/60/90 Days) in prompt template and sequence validator. | `tests/unit/test_stages.py` |
| **RSK-06** | System fails to ingest unseen hidden evaluation documents during competition assessment. | Hidden Eval Risk | Critical | Low | Architecture is 100% data-driven with no hardcoded role or policy assumptions; verified using hidden evaluation test runner (`tests/test_hidden_eval.py`). | `tests/hidden_eval/test_hidden_eval.py` |
| **RSK-07** | Team commits secrets or Gemini API keys to the public GitHub repository. | Competition Integrity Risk| Critical | Low | API keys loaded strictly from `.env` via `config/settings.py`; `.env` listed in `.gitignore`; pre-commit hook runs `gitleaks` key scan. | Secret scanning audit script |
| **RSK-08** | Policy version replacement leaves obsolete policy active or fails to mark affected plans as outdated. | Technical Risk | High | Low | Version manager explicitly sets `is_active=False` on superseded documents; impact analysis marks active employee plans as `is_outdated=True`. | `tests/integration/test_policy_update.py` |
| **RSK-09** | Plan generation and validation latency exceeds 30 seconds performance threshold. | Performance Risk | Medium | Medium | Asynchronous FastAPI endpoints, database query indexing, connection pooling, and optimized chunk lookup algorithms. | `tests/unit/test_performance.py` |
| **RSK-10** | Reviewer overrides system verification decision without maintaining historical audit record. | Audit Risk | High | Low | Append-only database table (`audit_trail`) protected against `UPDATE` or `DELETE` operations via database triggers. | `tests/security/test_audit_trail.py` |
