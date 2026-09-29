# SkillSprint AI — Project Deliverables Checklist

## Overview
This document tracks all **18 Mandatory Project Deliverables** required for final submission under **SkillSprint AI SRS Version 1.0 (§1.10 Project Deliverables)**.

---

## Deliverables Master Checklist

| # | Deliverable Name | Required Format / Artifact | Repository / Target Location | Key Contents Required by SRS §1.10 | Target Status |
| :- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Project Report** | PDF Document | `docs/reports/SkillSprint_AI_Project_Report.pdf` | Problem definition, background, solution, scope, constraints, FRs/NFRs, architecture, module descriptions, DB design, DFDs, UML diagrams (Use Case, Activity, Sequence), chunking, Role Matrix, prompts, validation logic, coverage calculation, traceability, hallucination detection, contradiction handling, prompt injection defense, security, testing, limitations, future scope. | Planned |
| **2** | **Source Code** | Python Codebase & Configuration | `src/`, `config/`, `requirements.txt`, `LICENSE` | Clean, modular Python backend codebase, API handlers, data processing engines, prompt management, schemas, and tests. | Planned |
| **3** | **Company Document Dataset** | PDF / DOCX Files + Metadata | `sample_documents/`, `docs/srs/dataset-requirements.md` | Company profile, scenario overview, 22 company policies, SOPs, role specs, FAQs, requirement matrix, metadata, version history, conflict cases, adversarial cases. | Planned |
| **4** | **GenAI Pipeline Evidence** | JSON Logs & Prompt Files | `genai_pipeline/`, `prompt_templates/`, `reports/genai_evidence/` | GenAI API used, model used, prompt templates, prompt versions, generation config, sample requests, sample responses, structured JSON output, failure & retry logs. | Planned |
| **5** | **Python Validation Pipeline Evidence** | Python Engine & Test Logs | `python_validation/`, `reports/validation_evidence/` | Requirement extraction logic, Role Requirement Matrix parser, source validation, coverage calculation, traceability check, duplicate detection, role relevance check, contradiction handling, schema validation, hallucination flagging. | Planned |
| **6** | **GenAI and Python Comparison Report** | PDF / CSV / Markdown | `reports/GenAI_Python_Comparison_Report.md` | Itemized comparison of at least 100 generated requirement-level results (Item ID, Role, Source, Python expected vs GenAI result, Match/Mismatch, Coverage status, Traceability status, Validation status, Disagreement explanation). | Planned |
| **7** | **Onboarding Plan Evidence** | Complete Plan Artifacts | `sample_documents/onboarding_plans_evidence/` | Complete generated and validated onboarding plans for at least 10 distinct job roles (Plan stages, modules, objectives, checklists, tasks, quizzes, assessments, source refs, verification results). | Planned |
| **8** | **Validation Report** | PDF / Markdown Report | `reports/Validation_Report.md` | Report documenting mandatory requirements, covered requirements, missing requirements, unsupported generated items, contradictions, duplicate content, traceability score, coverage score, manual review items. | Planned |
| **9** | **Security Testing Report** | PDF / Markdown Report | `docs/security/threat-model.md`, `reports/Security_Testing_Report.md` | Test execution results for prompt injection, malicious document parsing, unsupported topic queries, invalid file types, unauthorized API access, invalid API response formats. | Planned |
| **10** | **Test Cases & Test Suite** | Pytest Test Suite | `tests/` (`test_*.py`) | Comprehensive unit and integration test suite covering parsing, chunking, requirement extraction, GenAI API, JSON schema, Python validation, traceability, coverage, hallucination, contradiction, prompt injection, role relevance, versioning, regeneration, hidden doc readiness, boundary conditions. | Planned |
| **11** | **Installation Instructions** | Markdown Guide | `README.md`, `docs/installation-guide.md` | Clear setup instructions covering Python installation, virtual environment creation, dependency installation (`pip install`), API key setup (`.env`), DB setup, document seeding, app startup (`uvicorn` / `streamlit`). | Planned |
| **12** | **Execution Instructions** | Markdown Guide | `README.md` | Step-by-step user guide explaining login, uploading docs, creating roles/employees, generating requirement matrix, generating onboarding plans, running validation, reviewing comparison results, reviewing warnings/contradictions, approving content, tracking progress, updating policies, regenerating content, exporting reports. | Planned |
| **13** | **GitHub Repository** | Public GitHub Link | `https://github.com/USER/SkillSprint-AI` | Public repository containing meaningful commits across all 5 competition days, complete Python source, prompt templates, validation code, tests, sample docs, instructions, assumptions, limitations, deployment info, blog link, video link. NO secret keys committed. | Planned |
| **14** | **Deployed Application** | Hosted Live Web URL | Public Hosting Service (e.g. Render / Streamlit Cloud / Railway) | Live accessible web application URL, evaluator login credentials, administrator login credentials, sample loaded roles, sample company docs, step-by-step evaluation guide. | Planned |
| **15** | **Demonstration Video** | MP4 Video File | `documentation/demo_video.mp4` / YouTube Link | Mandatory .mp4 demonstration video showing login, doc upload, parsing, role creation, requirement matrix, plan generation, module generation, checklists, tasks, quizzes, GenAI JSON, Python validation, comparison view, scores, hallucination/contradiction detection, prompt injection defense, manual review, dashboard, policy update, selective regeneration, reporting. | Planned |
| **16** | **Technical Blog** | Published Blog Post URL | Published Medium / Dev.to / Hashnode Post | Technical blog post of at least 2,000 words discussing business problem, GenAI approach, Python architecture, doc processing, source grounding, prompt engineering, structured outputs, APIs, validation pipeline, Role Matrix, hallucination handling, prompt injection, contradictions, traceability, testing, challenges, security, lessons learned, limitations, future scope. | Planned |
| **17** | **AI Tool Usage Declaration**| Markdown File | `AI_USAGE.md` | Mandatory declaration detailing AI tools used, purpose, prompt or assistance type, files/modules affected, modifications performed, tests performed, and verifying team member. | Planned |
| **18** | **Final Submission Checklist & Team Contribution Record** | Markdown File | `docs/srs/deliverables-checklist.md` | Itemized checklist confirming completion of all 18 submission deliverables and detailed team contribution log. | Planned |

---

## Deliverables Sign-off & Audit Criteria

1. **Completeness Audit**: All 18 deliverables must be present in the public GitHub repository prior to final presentation.
2. **Zero Hardcoding Audit**: Codebase must pass `tests/test_no_hardcoding.py` confirming dynamic database-driven execution.
3. **5-Day Git History Audit**: Git log must demonstrate active commit history spanning all 5 competition days.
4. **Secrets Audit**: Repository must pass `gitleaks` / `.env` scan confirming zero API keys or secrets are exposed.
