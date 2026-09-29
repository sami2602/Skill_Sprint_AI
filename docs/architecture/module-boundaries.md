# SkillSprint AI — Module Boundaries & Directory Structure

## Overview
This document specifies the official directory structure, package boundaries, input/output contracts, and decoupling rules for **SkillSprint AI**, matching Section 1.10 of SRS Version 1.0.

---

## 1. Physical Directory Structure

```text
SkillSprint-AI/
├── config/                         # System configuration & environment loaders
│   ├── __init__.py
│   ├── settings.py                 # Pydantic BaseSettings for env vars & flags
│   └── logging_config.py           # Structured JSON logger configuration
├── docs/                           # Documentation repository
│   ├── srs/                        # Requirements inventory, matrix, acceptance criteria
│   ├── architecture/               # System architecture, ADRs, data flow, boundaries
│   ├── security/                   # Threat model & security specifications
│   └── testing/                    # Master test plan & test suites
├── document_processing/            # Document parsing & chunking subsystem
│   ├── __init__.py
│   ├── uploader.py                 # File upload, size, type validation
│   ├── parser.py                   # PDF (pdfplumber) & DOCX (python-docx) parsing
│   ├── chunker.py                  # Text chunking retaining metadata
│   ├── metadata.py                 # Source reference metadata manager
│   ├── versioning.py               # Active vs obsolete policy version control
│   └── impact.py                   # Policy change impact analysis engine
├── document_validation/            # Preliminary upload & schema validation
│   ├── __init__.py
│   └── validator.py                # Pre-ingestion validation rules
├── role_matrix/                    # Role Requirement Matrix subsystem
│   ├── __init__.py
│   ├── role_mgr.py                 # Job role management (10+ roles)
│   ├── extractor.py                # Policy requirement classifier (Must Know/Do)
│   └── matrix_builder.py           # Structured Role Requirement Matrix generator
├── genai_pipeline/                 # Pipeline 1: GenAI Generation Pipeline
│   ├── __init__.py
│   ├── client.py                   # Google Gemini API connector & client wrapper
│   ├── prompt_mgr.py               # Jinja2 prompt template renderer
│   ├── plan_builder.py             # Personalized onboarding plan generator
│   ├── module_gen.py               # Structured learning module generator
│   ├── checklist_gen.py            # Onboarding checklist generator
│   ├── task_gen.py                # Practical & scenario task generator
│   ├── quiz_gen.py                # MCQ / Scenario quiz generator
│   ├── assessment_gen.py          # Assessment & rubric generator
│   ├── recommendation.py          # Adaptive recommendation generator
│   ├── consistency.py             # GenAI generation consistency checker
│   ├── retry.py                   # Exponential backoff & retry interceptor
│   └── logger.py                  # Model & prompt execution logger
├── python_validation/              # Pipeline 2: Python Independent Ground-Truth Validator
│   ├── __init__.py
│   ├── engine.py                  # Core validation orchestrator (NO GenAI API calls)
│   ├── schema_val.py              # Pydantic JSON structure validator
│   ├── coverage.py                # Mandatory requirement coverage calculator
│   ├── traceability.py            # Source citation validator
│   ├── quiz_val.py                # Quiz answer & distractor validator
│   ├── duplicate.py               # Content duplicate detector
│   ├── role_relevance.py          # Role relevance validator
│   ├── sequence.py                # Prerequisite DAG & sequence validator
│   ├── progress_eval.py           # Employee progress evaluation engine
│   ├── scoring.py                 # Formula-based metric calculator
│   └── analytics.py               # Weak-area identification engine
├── prompt_templates/               # Managed versioned prompt template files
│   ├── v1/
│   │   ├── onboarding_plan.jinja2
│   │   ├── learning_module.jinja2
│   │   ├── quiz.jinja2
│   │   └── task.jinja2
│   └── prompt_registry.json       # Prompt version tracking metadata
├── schemas/                        # JSON Schemas & Pydantic Data Models
│   ├── onboarding_plan_schema.json
│   ├── learning_module_schema.json
│   ├── quiz_schema.json
│   └── requirement_matrix_schema.json
├── comparison_engine/              # GenAI vs Python Comparison & Decision Subsystem
│   ├── __init__.py
│   ├── comparator.py              # Itemized 100+ match/mismatch matrix generator
│   ├── decision.py                # Verification status state machine
│   └── review_queue.py            # Manual review queue workflow manager
├── hallucination_checks/           # Ungrounded claim detection module
│   ├── __init__.py
│   └── detector.py                # Source-embedding claim verification engine
├── contradiction_checks/           # Contradiction & precedence resolution module
│   ├── __init__.py
│   ├── engine.py                  # Contradiction detection engine
│   └── precedence.py              # Policy precedence rules manager
├── security/                       # Security & Prompt Injection Defense
│   ├── __init__.py
│   ├── auth.py                    # JWT authentication & session manager
│   ├── rbac.py                    # Role-Based Access Control middleware
│   ├── prompt_sanitizer.py        # Delimiter framing & input sanitizer
│   ├── adversarial_detector.py    # Adversarial document scanner
│   ├── pii_scrubber.py            # Outbound PII masking filter
│   └── audit.py                   # Immutable append-only audit trail logger
├── database/                       # Database models, ORM session, migrations
│   ├── __init__.py
│   ├── connection.py              # SQLAlchemy database engine connection
│   ├── models.py                  # SQLAlchemy ORM table definitions
│   └── seed_data.py               # Initial dataset seeder (20 docs, 10 roles)
├── reports_engine/                 # Reports & Export subsystem
│   ├── __init__.py
│   ├── generator.py               # Aggregate analytics report generator
│   └── exporter.py                # CSV, PDF, and XLSX export handler
├── static/                         # Frontend compiled assets & CSS
├── templates/                      # Server-side HTML templates (if any)
├── tests/                          # Automated Pytest test suite
│   ├── test_auth.py
│   ├── test_parser.py
│   ├── test_role_matrix.py
│   ├── test_plan_generator.py
│   ├── test_python_validation.py
│   ├── test_comparison_engine.py
│   ├── test_prompt_injection.py
│   ├── test_hidden_eval.py
│   └── test_no_hardcoding.py
├── sample_documents/               # Company dataset & test document repository
├── hidden_test_ready/              # Test folder for hidden evaluator pack dry-runs
├── reports/                        # Exported comparison & validation reports
├── src/                            # Application main entry point & API routes
│   ├── __init__.py
│   ├── main.py                    # FastAPI application initialization
│   └── api/                       # API route handlers
│       ├── v1/
│       │   ├── auth_routes.py
│       │   ├── doc_routes.py
│       │   ├── role_routes.py
│       │   ├── plan_routes.py
│       │   ├── validation_routes.py
│       │   ├── review_routes.py
│       │   └── report_routes.py
├── AI_USAGE.md                     # Mandatory AI usage log
├── LICENSE                         # Repository open-source license
├── README.md                       # Comprehensive installation & user guide
└── requirements.txt                # Python dependencies manifest
```

---

## 2. Module Interface & Contract Specifications

### Contract 1: Document Processing -> Database
- **Interface**: `document_processing.parser.parse_document(file_path: str, doc_metadata: dict) -> ParsedDocument`
- **Input**: Absolute path to uploaded PDF/DOCX file and user-provided metadata.
- **Output**: `ParsedDocument` object containing list of `DocumentChunk` items with fields `chunk_id`, `document_id`, `section_id`, `heading`, `page_number`, `paragraph_ref`, `text_content`, `version`, `effective_date`.

### Contract 2: Pipeline 1 (GenAI) Output -> Pipeline 2 (Python) Input
- **Interface**: `genai_pipeline.plan_builder.generate_onboarding_plan(employee_id: str, role_id: str) -> dict`
- **Input**: Employee ID and target Role ID.
- **Output**: Structured JSON dict matching `schemas/onboarding_plan_schema.json`.

### Contract 3: Pipeline 2 (Python Engine) Verification Contract
- **Interface**: `python_validation.engine.validate_plan(plan_json: dict, role_id: str) -> ValidationResult`
- **Input**: Structured JSON plan output from Pipeline 1 and Target Role ID.
- **Output**: `ValidationResult` dataclass containing:
  - `coverage_score`: float (0.0 to 100.0)
  - `traceability_score`: float (0.0 to 100.0)
  - `missing_requirements`: List[str]
  - `unsupported_claims`: List[dict]
  - `contradictions`: List[dict]
  - `sequence_errors`: List[dict]
  - `overall_status`: Enum (`VERIFIED`, `WARNING`, `INCOMPLETE`, `CONTRADICTORY`, `UNSUPPORTED`, `REVIEW_REQUIRED`)

---

## 3. Subsystem Decoupling Rules

1. **Pipeline Isolation**: `python_validation` MUST NOT import `genai_pipeline` modules. It operates strictly on stored data structures and rules.
2. **Database Access Abstraction**: Modules interact with database tables via SQLAlchemy ORM models in `database/models.py`. Direct SQL query execution outside ORM is prohibited.
3. **Prompt Independence**: Prompt templates in `prompt_templates/` are external text/Jinja2 files. No prompt string manipulation is permitted in Python source code files.
4. **Security Layer Isolation**: All inbound user files pass through `security.prompt_sanitizer` and `security.adversarial_detector` before reaching `document_processing`.
