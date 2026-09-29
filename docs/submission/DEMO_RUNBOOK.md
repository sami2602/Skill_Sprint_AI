# SkillSprint AI — Competition Demo Runbook & Execution Guide

## Overview
This runbook provides step-by-step instructions for running, testing, building, and demonstrating **SkillSprint AI** in a clean local environment.

---

## 1. Prerequisites & Environment Setup

Ensure the following tools are installed on your host system:
- **Python**: Python 3.10 or higher
- **Node.js**: Node.js 18.x or higher & npm
- **Git**: Latest version

---

## 2. One-Command Full Verification Sequence

To verify the complete system health from scratch, execute:

```powershell
# 1. Run Python Backend Test Suite (101 tests)
python -m pytest

# 2. Run Dataset Verification Script
python scripts/validate_dataset.py

# 3. Run Backend Performance Benchmark
python scripts/benchmark_backend.py

# 4. Run Frontend Unit Test Suite (7 tests)
cmd /c "cd frontend && npm test -- --run"

# 5. Build Production Frontend Bundle
cmd /c "cd frontend && npm run build"
```

---

## 3. Step-by-Step Local Launch Guide

### Step A: Seed Database with NOVAQUANT Benchmark Data
```powershell
python scripts/seed_dataset.py
```
*Expected Output*:
`Successfully seeded database! Total Policy Requirements created: 154`

### Step B: Start FastAPI Backend Server
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
*Verification*: Open browser to `http://127.0.0.1:8000/docs` to inspect interactive OpenAPI Swagger UI.

### Step C: Start React Frontend Application
Open a new terminal window:
```powershell
cd frontend
cmd /c "npm run dev"
```
*Verification*: Open browser to `http://localhost:5173`.

---

## 4. Demo Step-by-Step Walkthrough Guide for Evaluators

### Step 1: User Login & Role Selection
- Open `http://localhost:5173`.
- Authenticate as **Administrator / Reviewer** or **Employee**.
- Experience seamless JWT authentication and role header context.

### Step 2: Executive Dashboard Overview
- Navigate to **Executive Dashboard**.
- Inspect real-time corporate metrics: Total Documents (22), Job Roles (10), Active Requirements (154), Average Mandatory Coverage (100%), Active Onboarding Plans.

### Step 3: Document Catalog & Source Provenance
- Navigate to **Document Repository**.
- View parsed SOPs, compliance policies, and HR guidelines.
- Click any document to view chunk metadata, version history, effective dates, and location references (PDF page / DOCX paragraph).

### Step 4: Role Requirement Matrix Grid
- Navigate to **Role Matrix**.
- Select role `ROL-01` (Software Engineer) or `ROL-03` (Customer Support Executive).
- Inspect mandatory and optional requirements mapped to ground-truth policy documents.

### Step 5: Dual-Pipeline AI Onboarding Generation & Ground-Truth Verification
- Navigate to **Verification Center**.
- Click **"Generate AI Onboarding Plan"** for Customer Support Executive.
- Watch **Pipeline 1 (GenAI)** construct structured JSON onboarding plan.
- Watch **Pipeline 2 (Python Ground-Truth Validator)** automatically inspect the JSON against the Role Requirement Matrix.
- View real-time **Coverage Score (100%)** and **Traceability Score (100%)**.

### Step 6: Contradiction & Prompt Injection Defense Demonstration
- Inspect the **Ground-Truth Guard Status Panel**.
- Observe how policy contradictions (e.g. FAQ v1 vs SOP v2) are automatically resolved via Policy Precedence rules.
- Observe how adversarial injection payloads inside uploaded documents are wrapped inside `<untrusted_document_data>` tags and stripped of executable commands.

### Step 7: Manual Reviewer Workflow & Audit Log
- Navigate to **Review Queue**.
- Inspect flagged items (e.g., optional ungrounded tasks).
- Click **Approve Override** or **Reject Item** with reviewer notes.
- Observe the append-only **Audit Trail** entry capturing the override history.

### Step 8: Policy Impact Analysis & Selective Regeneration
- Navigate to **Policy Impact**.
- Simulate updating a policy (e.g., updating `HR-POL-03` to Version 3.1).
- View the **Impact Analysis Tree** highlighting affected modules and outdated plans.
- Click **Selective Regenerate** to update ONLY affected modules while keeping existing unchanged modules untouched.

### Step 9: Employee Portal Experience
- Switch role view to **Employee Portal**.
- View personalized onboarding timeline (Day 1, Week 1, 30 Days).
- Interact with **Learning Modules**, **Checklists**, **Scenario Tasks**, and **Interactive Quizzes**.
- Track real-time completion progress and weak area remediation recommendations.

---

## 5. Troubleshooting & FAQ

- **Database Lock / Tables Missing**: Run `python scripts/seed_dataset.py` to reset and seed the database.
- **Port 8000 Conflict**: Kill running uvicorn process or specify alternative port `--port 8080`.
- **Frontend Dependencies Issue**: Run `cmd /c "cd frontend && npm install"` to sync node modules.
