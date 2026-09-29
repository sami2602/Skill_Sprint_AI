# SkillSprint AI — Master Discovery & Requirements Specification Report (DISCOVERY_REPORT.md)

## Executive Summary
This **Master Discovery Report** synthesizes the complete, end-to-end analysis of the **SkillSprint AI Software Requirements Specification (SRS Version 1.0)**, establishing the authoritative foundation for Phase 0 before business feature implementation begins.

---

## A. SRS Overview
- **Project Name**: SkillSprint AI
- **Theme**: OnboardVerse
- **Category**: Generative AI PowerPlay
- **Specification Version**: 1.0 (Aptech Limited / TechWiz 7)
- **Core Purpose**: Automatically analyze enterprise company policies, SOPs, role descriptions, FAQs, and compliance manuals to construct personalized, multi-stage onboarding plans, while independently verifying completeness, grounding, source traceability, and policy compliance via a deterministic Python Ground-Truth Engine.

---

## B. Total Requirements Identified
- **Total Functional Requirements (FR)**: 62 Requirements
- **Total Non-Functional Requirements (NFR)**: 5 Requirements
- **Total Security Requirements (SEC)**: 5 Requirements
- **Total Competition Integrity Requirements (INT)**: 5 Requirements
- **Total Dataset Requirements (DAT)**: 8 Requirements
- **Total Hidden Evaluation Requirements (HEV)**: 7 Requirements
- **Total Documentation & Deliverables Requirements (DOC)**: 8 Requirements
- **Grand Total Extracted Requirements**: **100 System Requirements**

---

## C. Functional Requirements Summary
- Complete user authentication and Role-Based Access Control (RBAC) across 5 roles (Admin, Training Manager, Reviewer, Manager, Employee).
- Multi-format document ingestion, parsing, metadata extraction, chunking, and version control for PDF and DOCX documents.
- Dynamic construction of the **Role Requirement Matrix** mapping roles to mandatory/optional policy items.
- Pipeline 1 GenAI personalized onboarding plan generation spanning multi-stage timelines (Day 1, Week 1, Week 2, 30/60/90 Days) with learning modules, checklists, practical tasks, scenario tasks, quizzes, and assessment rubrics.
- Pipeline 2 independent Python ground-truth validation (0 GenAI API calls) enforcing mandatory requirement coverage, source traceability, contradiction detection, hallucination flagging, role relevance verification, sequence validation, and score calculation.
- Result comparison matrix (100+ items), verification status decider, manual review queue, and append-only audit trail logger.
- Role update detection, impact analysis, selective regeneration, progress tracking, weak-area analytics, adaptive recommendations, search/filter, and report export (CSV, PDF, XLSX).

---

## D. Non-Functional Requirements Summary
- **Performance (NFR-01)**: Onboarding plan generation and Python validation cycle completes within **30 seconds** under normal API conditions.
- **Scalability (NFR-02)**: System supports at least **1,000 employee profiles, 100 job roles, and 1,000 organizational documents** without requiring architectural redesign.
- **Usability (NFR-03)**: Responsive, user-friendly UI for employees, admins, reviewers, HR teams, and training managers.
- **Accuracy & Grounding (NFR-04)**: Mandatory onboarding plans must achieve **100% coverage** of the approved mandatory Role Requirement Matrix before final approval.
- **Availability (NFR-05)**: Application maintains at least **99% uptime** during competition evaluation.

---

## E. Security Requirements Summary
- **Prompt Injection Defense**: Uploaded documents treated strictly as untrusted data; text isolated inside `<untrusted_document_data>` tags; document text NEVER executed as commands.
- **Adversarial Scanner**: Automated security scanner flags malicious payloads and injection attempts.
- **Immutable Audit Trail**: Append-only database table (`audit_trail`) protected by DB triggers prevents modification or deletion of reviewer override history.
- **PII Scrubbing**: Sensitive personal data excluded from profile payloads and masked before outbound GenAI calls.
- **Secret Protection**: API keys loaded strictly from environment variables (`.env`); scanned via `gitleaks`.

---

## F. Dataset Requirements Summary
- **Required by SRS**: Fictional company scenario with minimum 20 company documents, 10 job roles, 150+ policy requirements, 50+ mandatory requirements, 30+ role-specific requirements, 10 conflicting cases, 10 policy version updates, and 10 prompt injection test documents.
- **Project Recommendation**: Apex Global Solutions Ltd. dataset featuring 22 documents, 10 roles, and 165 extracted requirement entities.

---

## G. Hidden Evaluation Requirements Summary
- Architecture processes unseen hidden evaluation document packs (new roles, replacement policies, conflicting FAQs, prompt injections, missing requirements, ambiguous clauses) **dynamically without source-code modification**.
- Includes dry-run hidden evaluation test harness (`tests/hidden_eval/test_hidden_eval.py`).

---

## H. Anti-Shortcut Requirements Summary
- **Dual-Pipeline Independence**: GenAI MAY NOT approve or validate its own output.
- **No Hardcoded Output**: Prohibits prewritten role plans, hardcoded quiz answers, fabricated validation scores, or fake comparison results.
- **Commit Activity**: 5-day GitHub commit history reflecting genuine development activity.
- **AI_USAGE.md**: Complete tracking of all AI tool assistance.

---

## I. Architecture Constraints
- Backend: FastAPI (Python 3.14.7)
- Frontend: React (Vite + TailwindCSS / Bootstrap)
- Database: SQLite (Dev) / PostgreSQL (Prod) via SQLAlchemy ORM
- GenAI API: Google Gemini API (`gemini-2.5-flash`) via `google-genai` SDK
- Document Processing: `pdfplumber`, `pypdf`, `python-docx`

---

## J. Testing Requirements
- Pytest suite covering unit, integration, API, validation, security, prompt injection, contradiction, policy version, e2e, and AST anti-hardcoding audit tests.

---

## K. Documentation Requirements
- Full PDF Project Report, Architecture Specs, ADRs, Threat Model, Master Test Plan, Deliverables Checklist, Technical Blog (min 2,000 words), Installation Guide, and Execution Guide.

---

## L. Submission Requirements
- All 18 mandatory project submission items listed in SRS §1.10.

---

## M. Ambiguous Requirements & Clarifications
- Framework choices (FastAPI, React, SQLite/PostgreSQL selected via ADRs 01-04).
- DOCX source citations mapped via Section Heading + Paragraph Index.

---

## N. Risks
- Detailed in [project-risks.md](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/architecture/project-risks.md).

---

## O. Human Decisions Required
- Detailed in [human-decisions-required.md](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/architecture/human-decisions-required.md).

---

## P. Recommended Implementation Order

1. **Phase 0**: SRS Discovery & Architecture Verification (COMPLETE)
2. **Phase 1**: Repository & Environment Foundation (COMPLETE)
3. **Phase 2**: Dataset Creation & Document Ingestion Engine (`document_processing/`)
4. **Phase 3**: Knowledge Base & Role Requirement Matrix Engine (`knowledge/`)
5. **Phase 4**: Pipeline 1 GenAI Plan & Module Generator (`genai/`)
6. **Phase 5**: Pipeline 2 Independent Python Ground-Truth Validation Engine (`validation/`)
7. **Phase 6**: Result Comparison Engine, Review Queue & Audit Logging (`comparison_engine/`, `security/`)
8. **Phase 7**: Backend REST API & Database Integration (`backend/`)
9. **Phase 8**: Frontend React Dashboard & UI Workflows (`frontend/`)
10. **Phase 9**: Security Red-Teaming, Automated Test Suite & Hidden Eval Dry-Run (`tests/`, `security/`)
11. **Phase 10**: Documentation, Technical Blog, Demo Video & Final Submission (`docs/`, `reports/`)
