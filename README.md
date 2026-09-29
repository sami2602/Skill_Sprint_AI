# 🚀 SkillSprint AI — Enterprise Training & Onboarding Intelligence Platform
### **🏆 Designed & Developed by TEAM NASR 🏆**

[![Python Version](https://img.shields.io/badge/python-3.14.7-blue.svg)](https://www.python.org/)
[![Backend Framework](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Frontend Framework](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![Team](https://img.shields.io/badge/Team-NASR-gold.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Team**: Team NASR  
> **Theme**: OnboardVerse  
> **Category**: Generative AI PowerPlay  
> **Project**: SkillSprint AI  
> **SRS Version**: 1.0 (Aptech Limited / TechWiz 7)

---

## 📌 Executive Overview

**SkillSprint AI** is an advanced Generative AI corporate training and onboarding intelligence application. It automatically analyzes company policy documents, Standard Operating Procedures (SOPs), role descriptions, FAQs, and compliance manuals to construct personalized, multi-stage onboarding plans for diverse job roles.

To guarantee compliance, accuracy, and eliminate AI hallucination, SkillSprint AI implements a **Dual-Pipeline Architecture**:
1. **Pipeline 1 (GenAI Generator)**: Leverages Google Gemini API to interpret roles and generate structured onboarding plans, learning modules, checklists, tasks, quizzes, and assessments.
2. **Pipeline 2 (Python Ground-Truth Validator)**: An independent, deterministic Python validation engine (NO GenAI API calls) that evaluates generated content against an approved database-backed **Role Requirement Matrix**, calculating mandatory requirement coverage, source traceability, role relevance, policy precedence, and sequence validity.

---

## 🏗 System Architecture Diagram

```text
+-----------------------------------------------------------------------------+
|                                KNOWLEDGE SOURCES                            |
|       Company Policies | SOPs | Role Descriptions | FAQs | Compliance        |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                       DOCUMENT PARSING & CHUNKING                           |
|       PDF & DOCX Extraction | Metadata Tagging | Version Control            |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                      ROLE REQUIREMENT MATRIX BUILDER                        |
|       Ground-Truth Reference Matrix (Must Know / Must Complete Reqs)       |
+-----------------------------------------------------------------------------+
                               /               \
                              /                 \
                             v                   v
+------------------------------------+   +------------------------------------+
|  PIPELINE 1: GenAI GENERATOR       |   | PIPELINE 2: PYTHON VALIDATOR       |
|  (Python + Google Gemini API)      |   | (Independent Deterministic Engine) |
|  - Multi-Stage Plans               |   | - Schema & Type Validation         |
|  - Learning Modules & Objectives   |   | - Mandatory Coverage Score (%)     |
|  - Checklists & Practical Tasks    |   | - Source Traceability Score (%)    |
|  - Quizzes & Rubrics               |   | - Policy Precedence Resolution     |
|  - Structured JSON Output          |   | - Contradiction & Hallucination    |
+------------------------------------+   +------------------------------------+
                             \                   /
                              \                 /
                               v               v
+-----------------------------------------------------------------------------+
|                    RESULT COMPARISON & DECISION ENGINE                      |
|       Match/Mismatch Matrix | Verification Status (Verified / Review)      |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                     PRESENTATION & AUDIT LOGGING                            |
|       Learner Dashboard | Admin Dashboard | Review Queue | Audit Trail      |
+-----------------------------------------------------------------------------+
```

---

## 📁 Repository Structure

```text
SkillSprint-AI/
├── .agents/                        # Agent configurations & operational rules
├── backend/                        # FastAPI application, models, routes, services
├── document_processing/            # File upload, PDF/DOCX parsing, chunking, versioning
├── knowledge/                      # Role requirement matrix, policy taxonomy, conflicts
├── genai/                          # Gemini API client, Jinja2 prompt templates, generators
├── validation/                     # Independent Python ground-truth validation engine
├── security/                       # Adversarial scanner, prompt injection defense, RBAC
├── frontend/                       # React dashboard frontend application
├── data/                           # Fictional enterprise dataset (docs, roles, policies)
├── tests/                          # Automated Pytest suite (unit, integration, security)
├── scripts/                        # Dataset seeding & dry-run evaluation scripts
├── reports/                        # Exported validation, security, & comparison reports
└── docs/                           # Official SRS analysis, architecture, ADRs, test plan
    ├── srs/                        # Requirements inventory, matrix, acceptance criteria
    ├── architecture/               # System architecture, ADRs, data flow, boundaries
    ├── security/                   # STRIDE threat model & injection defense
    └── testing/                    # Master test plan & test case specifications
```

---

## 🚀 Quick Setup & Installation Guide

### Prerequisites
- **Python**: 3.14.7
- **Node.js**: 18+ (for frontend execution)
- **Git**: 2.30+

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/USER/SkillSprint-AI.git
cd SkillSprint-AI

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Linux/macOS)
# source venv/bin/activate
```

### Step 2: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
```bash
# Copy example environment configuration
cp .env.example .env

# Edit .env and supply your Google Gemini API Key
# GEMINI_API_KEY="your_actual_gemini_api_key_here"
```

### Step 4: Seed Database & Initialize Sample Dataset
```bash
python scripts/seed_dataset.py
```

### Step 5: Start FastAPI Backend Server
```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive API documentation is accessible at: `http://127.0.0.1:8000/docs` or `http://127.0.0.1:8000/redoc`.

---

## 🧪 Running Automated Tests & Performance Benchmarks

Run the complete Pytest suite including unit, API, auth, RBAC, document security, validation, comparison, review queue, audit, policy impact, selective regeneration, and Phase 7 end-to-end integration tests:

```bash
# Run all 81 automated unit, security, API, and integration tests
python -m pytest

# Run Phase 7 Production API unit & security tests
python -m pytest tests/unit/test_api_auth.py tests/unit/test_api_documents_security.py tests/unit/test_api_core_modules.py

# Run Phase 7 End-to-End Integration workflows
python -m pytest tests/integration/test_phase7_e2e_flow.py

# Run Backend Performance Measurement Benchmark Script
python scripts/benchmark_backend.py
```

---

## 🐳 Docker Deployment

Build and run via Docker Compose:
```bash
docker-compose up -d --build
```
Or view the complete [Deployment Guide](docs/deployment.md).

---

## 📄 Key Project Documentation

- [Master SRS Traceability Matrix (100/100)](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/submission/SRS_TRACEABILITY_MATRIX.md)
- [Competition Demo Runbook](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/submission/DEMO_RUNBOOK.md)
- [Technical Blog (2,000+ Words)](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/submission/TECHNICAL_BLOG.md)
- [Final Competition Readiness Report](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/reports/final/FINAL_COMPETITION_READINESS_REPORT.md)
- [Dataset Readiness & Verification Report](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/reports/final/dataset_readiness_report.md)
- [Dual-Pipeline Isolation & Ground-Truth Evidence](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/reports/final/dual_pipeline_evidence.md)
- [Final System Performance Report](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/reports/final/performance_report.md)
- [Requirements Inventory](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/srs/requirements-inventory.md)
- [Acceptance Criteria Specification](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/srs/acceptance-criteria.md)
- [Phase 7 Production API Specification](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/api/phase7-production-api.md)
- [Auth & RBAC Security Specification](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/security/auth-rbac-spec.md)
- [Validation Engine Architecture](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/architecture/validation-architecture.md)
- [Architecture Decision Records (ADRs)](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/architecture/architecture-decision-record.md)
- [System Architecture Specification](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/architecture/system-architecture.md)
- [Security Threat Model](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/security/threat-model.md)
- [Master Test Plan](file:///c:/Users/HOMe/Desktop/SkillSprint-AI/docs/testing/master-test-plan.md)

---

## 📜 License & AI Declaration

- **License**: Released under the [MIT License](LICENSE).
- **AI Tool Usage**: Full details of AI-assisted development are recorded in [AI_USAGE.md](AI_USAGE.md).

