# SkillSprint AI — Architecture Decision Records (ADRs)

## Overview
This document logs the core architectural decisions for **SkillSprint AI**, detailing context, decision outcomes, rationale, and compliance with the official **SRS Version 1.0**.

---

## ADR-01: Strict Dual-Pipeline Isolation Architecture

* **Status**: Approved
* **Context**: SRS Section 1.2 & Core Architecture Principle mandate that Generative AI generation and Python validation MUST remain independent. GenAI must NEVER validate or approve its own generated output.
* **Decision**: Implement two physically separate Python execution pipelines:
  1. `Pipeline 1 (GenAI Generation Pipeline)`: Calls GenAI API (Gemini) to interpret roles and generate structured onboarding plans, modules, checklists, tasks, quizzes, and assessments in JSON format.
  2. `Pipeline 2 (Python Ground-Truth Validation Pipeline)`: Executes 100% deterministic Python rule checks against the database-backed Role Requirement Matrix, metadata, and precedence rules. Makes zero outbound calls to GenAI APIs.
* **Consequences**: Complete protection against AI self-approval bias; guarantees objective coverage scoring; complies with competition anti-shortcut rules.

---

## ADR-02: Backend Framework Selection — FastAPI (Python 3.14.7)

* **Status**: Approved
* **Context**: SRS Section 1.9.2 allows Flask, Django, FastAPI, or Streamlit for the Python backend.
* **Decision**: Select **FastAPI** as the core backend framework.
* **Rationale**:
  - Asynchronous non-blocking architecture allows handling concurrent document processing and GenAI API calls.
  - Native integration with **Pydantic v2** provides high-speed request/response schema validation.
  - Automatic OpenAPI / Swagger interactive documentation generation.
  - Clean separation between REST API backend and single-page React frontend.
* **Consequences**: High performance API latency (< 30s pipeline execution); clear API module boundaries.

---

## ADR-03: Frontend Architecture — React with Vite & Modern Design System

* **Status**: Approved
* **Context**: SRS Section 1.9.2 allows HTML5/CSS3/JS, Bootstrap, Streamlit, or React. SRS Section 1.6 requires responsive web interface, interactive dashboards, comparison matrices, and review workflows.
* **Decision**: Select **React (Vite build system)** paired with **Bootstrap / TailwindCSS** and **Lucide Icons**.
* **Rationale**:
  - Streamlit lacks native capability for complex side-by-side diff matrices, interactive drag-and-drop document upload, and fine-grained stateful review workflows required by §1.2 Steps 46-49.
  - React single-page app provides instantaneous UI updates, responsive dashboards, and interactive visual charts (using Recharts / Chart.js).
* **Consequences**: Superior reviewer and learner experience; responsive layout across desktop and tablet viewports.

---

## ADR-04: Database Architecture — SQLite (Development) & PostgreSQL (Production) via SQLAlchemy ORM

* **Status**: Approved
* **Context**: SRS Section 1.9.2 supports MongoDB, PostgreSQL, MySQL, Firebase, or SQLite.
* **Decision**: Implement **SQLAlchemy 2.0 ORM** with **SQLite** for zero-dependency local development/testing and **PostgreSQL** for cloud production deployment.
* **Rationale**:
  - Relational mapping handles foreign key constraints between documents, sections, chunks, policy requirements, roles, mappings, conflicts, and audit trails cleanly.
  - Portable SQLite database enables zero-config evaluator testing during final competition evaluation.
* **Consequences**: Standardized data access layer across environments.

---

## ADR-005: Independent Python Ground-Truth Validation Engine Architecture

* **Status**: Approved
* **Context**: SRS FR-30 through FR-45 mandate that output completeness and accuracy must be verified by an independent, deterministic Python validation engine without relying on LLMs or self-validation.
* **Decision**: Architect `validation/` module with 8 specialized deterministic validators:
  1. `CoverageValidator`: Evaluates mandatory requirement coverage percentage against DB matrix.
  2. `TraceabilityValidator`: Evaluates document version, section, page, and requirement correspondence.
  3. `UnsupportedContentValidator`: Detects ungrounded/hallucinated claims.
  4. `DuplicateValidator`: Detects repetitive requirements, modules, tasks, and questions.
  5. `ContradictionValidator`: Enforces policy precedence ranks and checks direct policy conflicts.
  6. `SequenceValidator`: Validates stage order, task prerequisites, and compliance placement.
  7. `QuizValidator`: Independently verifies question options, distractor uniqueness, and correct answer flags.
  8. `RoleRelevanceValidator`: Flags cross-role requirement misallocations.
* **Rationale**: Eliminates LLM self-validation bias completely; guarantees 100% deterministic ground-truth verification; executes in average latency < 50 ms.
* **Consequences**: Rigorous verification decisions (VERIFIED, NEEDS_REVIEW, REJECTED), itemized requirement-level comparison matrices, and immutable reviewer override audit trails.

  - Relational schema ensures strict referential integrity between `documents`, `sections`, `roles`, `role_requirement_matrix`, `plans`, and `audit_trail`.
  - SQLAlchemy abstraction enables zero-code schema migration between local SQLite file database and hosted PostgreSQL instance.
* **Consequences**: Fast unit test execution using in-memory SQLite; robust relational data integrity in production.

---

## ADR-05: Multi-Format Document Parsing Engine

* **Status**: Approved
* **Context**: SRS Section 1.2 Steps 4-7 & Section 1.8 require parsing PDF and DOCX documents while preserving Document ID, section headings, version, effective date, page numbers (PDF), and paragraph references (DOCX).
* **Decision**: Implement a unified parsing engine using `pdfplumber` / `pypdf` for PDF text/page extraction and `python-docx` for DOCX structural paragraph/table parsing.
* **Rationale**:
  - `pdfplumber` provides exact character positioning and page number tracking for PDFs.
  - `python-docx` extracts structured headings (`Heading 1`, `Heading 2`) and paragraph index metadata from Word documents.
* **Consequences**: Precise source citations (`Doc ID`, `Section ID`, `Page/Paragraph Ref`) attached to every extracted text chunk.

---

## ADR-06: Generative AI API Gateway & Model Choice

* **Status**: Approved
* **Context**: SRS Section 1.9.2 allows OpenAI API, Google Gemini API, or Anthropic API.
* **Decision**: Use **Google Gemini API** (`gemini-2.5-flash` / `gemini-1.5-pro` via `google-genai` Python SDK) as the primary GenAI provider, with an abstraction interface for OpenAI fallback.
* **Rationale**:
  - Gemini API supports native Structured JSON Output enforcement (`response_schema`).
  - High context window accommodates large policy document payloads.
  - Cost-effective and low-latency response generation.
* **Consequences**: Reliable JSON responses matching Pydantic schema schemas.

---

## ADR-07: Prompt Management & Prompt Injection Defense Strategy

* **Status**: Approved
* **Context**: SRS Section 1.2 Step 40, Step 42 & Section 1.8 5 mandate stored prompt templates, prompt versioning, and strict prompt injection defense. Document text must NEVER become executable system instructions.
* **Decision**:
  1. Store all prompts in versioned template files (`prompt_templates/v1/onboarding_plan.jinja2`).
  2. Use strict XML data boundary framing (`<untrusted_company_document>` tags) in prompts.
  3. Pre-scan uploaded document text using regex/keyword security filter (`security/adversarial_detector.py`).
* **Rationale**: Explicit separation of instructions (system prompt) and data (document text) prevents prompt injection attacks from altering model behavior.
* **Consequences**: Document instructions cannot override application rules; full security compliance.

---

## ADR-08: Document Precedence & Contradiction Resolution Strategy

* **Status**: Approved
* **Context**: SRS Section 1.2 Step 34 & Section 1.8 6 mandate configurable document precedence rules to resolve conflicts between active policies, old SOPs, and FAQs.
* **Decision**: Implement a deterministic Python Precedence Engine (`contradiction_checks/precedence_engine.py`) using configurable priority hierarchy:
  - Priority 1: Latest Approved Policy (Active Version)
  - Priority 2: Department SOP (Active Version)
  - Priority 3: Official FAQ
  - Priority 4: Informal Guidance
* **Rationale**: When Python validator detects contradictory statements across sources, it automatically selects the higher-priority rule as ground truth and flags lower-priority claims as `CONTRADICTION_DETECTED`.
* **Consequences**: Consistent, deterministic conflict resolution without AI guessing.

---

## ADR-09: Immutable Audit Trail & Reviewer Override Design

* **Status**: Approved
* **Context**: SRS Section 1.2 Step 49 requires that authorized reviewers can override system decisions, while maintaining both original result and reviewer action in audit logs.
* **Decision**: Implement an append-only database table (`audit_trail`) managed by `security/audit_logger.py`.
* **Rationale**:
  - Prevents overwriting or deleting historical system validation outputs.
  - Records reviewer user ID, timestamp, target item ID, original verification status, override status, and reviewer commentary.
* **Consequences**: Full transparency and compliance auditability.

---

## ADR-10: Dynamic Database-Driven Architecture (No Hardcoding)

* **Status**: Approved
* **Context**: SRS Section 1.8 12 strictly prohibits hardcoded onboarding plans, quiz answers, prewritten role plans, fabricated validation scores, or fake comparison results.
* **Decision**: All system operations operate dynamically against database tables (`documents`, `roles`, `role_requirement_matrix`, `plans`, `validation_results`). Zero pre-baked response constants are allowed in backend code.
* **Rationale**: Enforces compliance with competition rules and enables processing of unseen hidden evaluation document packs.
* **Consequences**: Architecture handles arbitrary new roles and documents seamlessly without code changes.
