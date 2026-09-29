# SkillSprint AI — Data Flow Specification & Sequence Diagrams

## Overview
This document specifies the Data Flow Architecture for **SkillSprint AI**, including DFD Level 0 (Context Diagram), DFD Level 1, DFD Level 2, and Sequence Diagrams for all critical system workflows.

---

## 1. Data Flow Diagram Level 0 — Context Diagram

```mermaid
flowchart LR
    Admin["Administrator / Reviewer"]
    Learner["Employee / Learner"]
    GenAI_API["External GenAI API\n(Google Gemini API)"]
    
    subgraph SkillSprintAI ["SkillSprint AI Core Platform"]
        SystemProcess["SkillSprint AI Engine\n(FastAPI Backend + React UI)"]
    end
    
    Admin -->|Upload Documents, Define Roles, Override Flags| SystemProcess
    SystemProcess -->|Dashboards, Reports, Audit Logs, Verification Results| Admin
    
    Learner -->|Complete Modules, Tasks, Take Quizzes| SystemProcess
    SystemProcess -->|Personalized Plans, Modules, Progress Status| Learner
    
    SystemProcess -->|Prompt Payloads + Doc Context| GenAI_API
    GenAI_API -->|Structured JSON Onboarding Content| SystemProcess
```

---

## 2. Data Flow Diagram Level 1 — Subsystem Data Flow

```mermaid
flowchart TD
    subgraph External
        DocFiles["PDF / DOCX Files"]
        UserReq["User Profile & Role Selection"]
        GeminiAPI["Google Gemini API"]
    end

    subgraph DataStores [Database Stores]
        DS_Docs[("documents & chunks")]
        DS_Matrix[("role_requirement_matrix")]
        DS_Plans[("onboarding_plans")]
        DS_Audit[("audit_trail")]
    end

    subgraph Processes
        P1["1.0 Document Validation & Parsing"]
        P2["2.0 Requirement Matrix Extraction"]
        P3["3.0 GenAI Plan Generation (Pipeline 1)"]
        P4["4.0 Python Ground-Truth Validation (Pipeline 2)"]
        P5["5.0 Result Comparison & Decision Engine"]
        P6["6.0 Reviewer Override & Audit Logging"]
    end

    DocFiles --> P1
    P1 -->|Store Extracted Chunks & Metadata| DS_Docs
    DS_Docs --> P2
    P2 -->|Store Role Requirements| DS_Matrix

    UserReq --> P3
    DS_Docs --> P3
    P3 <-->|API Prompt & Structured JSON Response| GeminiAPI
    P3 -->|Store Draft Plan| DS_Plans

    DS_Plans --> P4
    DS_Matrix --> P4
    DS_Docs --> P4
    P4 -->|Generated Validation Results| P5

    P5 -->|Update Verification Status| DS_Plans
    P5 -->|Route Flagged Plan| P6
    P6 -->|Write Override Event| DS_Audit
    P6 -->|Final Approved Plan| DS_Plans
```

---

## 3. Core Sequence Diagrams

### Sequence Diagram 1: Document Ingestion, Parsing & Chunking

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrator
    participant UI as React UI
    participant API as FastAPI Backend
    participant Security as Adversarial Scanner
    participant Parser as Doc Parser (pdfplumber/docx)
    participant Chunker as Text Chunker
    participant DB as SQLite / PostgreSQL

    Admin->>UI: Select and Upload File (PDF/DOCX)
    UI->>API: POST /api/v1/documents/upload (Multipart file)
    API->>Security: Scan File for Malicious Commands & Injection
    Security-->>API: Scan Passed (Clean Untrusted Data)
    API->>Parser: Parse File Content & Metadata
    Parser-->>API: Extracted Text + Section Headings + Page/Para Refs
    API->>Chunker: Split Text into Semantic Chunks (~500 tokens)
    Chunker-->>API: Chunks with Doc ID, Chunk ID, Section, Page Ref
    API->>DB: Save Document Record & Document Chunks
    DB-->>API: Confirm Database Save
    API-->>UI: Return HTTP 200 (Upload & Parse Successful)
    UI-->>Admin: Display Parsed Document Summary & Section Tree
```

---

### Sequence Diagram 2: Dual-Pipeline Plan Generation & Verification

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrator / HR
    participant UI as React UI
    participant API as FastAPI Backend
    participant Matrix as Role Matrix Engine
    participant GenAI as Pipeline 1 (GenAI Generator)
    participant Gemini as Google Gemini API
    participant Validator as Pipeline 2 (Python Ground-Truth Validator)
    participant Comparator as Comparison & Decision Engine
    participant DB as System Database

    Admin->>UI: Select Employee Profile & Job Role (e.g. Customer Support)
    UI->>API: POST /api/v1/plans/generate (role_id, employee_id)
    API->>DB: Fetch Active Role Requirement Matrix & Source Chunks
    DB-->>API: Return Matrix Rules & Ground-Truth References

    rect rgb(230, 240, 255)
        Note over API, Gemini: Pipeline 1: GenAI Content Generation
        API->>GenAI: Execute Plan Generation Prompt Template
        GenAI->>Gemini: Call Gemini API (Structured Response Schema)
        Gemini-->>GenAI: Return Structured JSON (Modules, Checklists, Tasks, Quizzes)
        GenAI-->>API: Return Pipeline 1 JSON Payload
    end

    rect rgb(255, 240, 230)
        Note over API, Validator: Pipeline 2: Python Independent Ground-Truth Validation (NO GenAI Calls)
        API->>Validator: Run Independent Python Validation Engine
        Validator->>Validator: 1. Schema Validation (Pydantic)
        Validator->>Validator: 2. Mandatory Coverage Check (Formula)
        Validator->>Validator: 3. Source Traceability Check (Citation Match)
        Validator->>Validator: 4. Contradiction & Precedence Check (Policy v2 > SOP)
        Validator->>Validator: 5. Hallucination & Ungrounded Claim Check
        Validator->>Validator: 6. Prerequisite & Learning Sequence Check
        Validator-->>API: Return Python Validation Metrics & Rule Results
    end

    API->>Comparator: Compare Pipeline 1 JSON vs Pipeline 2 Validation Metrics
    Comparator->>Comparator: Calculate Matches, Mismatches & Assigned Verification Status
    Comparator->>DB: Save Generated Plan, Verification Status & Comparison Matrix
    DB-->>API: Save Complete
    API-->>UI: Return Verification Decision & Comparison Matrix
    UI-->>Admin: Display Verification Header (Verified / Warning / Review Required) & Matrix
```

---

### Sequence Diagram 3: Policy Update & Selective Regeneration

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrator
    participant UI as React UI
    participant API as FastAPI Backend
    participant Versioning as Version Control Subsystem
    participant Impact as Impact Analysis Engine
    participant GenAI as Pipeline 1 Generator
    participant DB as System Database

    Admin->>UI: Upload Replacement Policy File (e.g. HR-Policy_v2.docx)
    UI->>API: POST /api/v1/documents/policy-update (old_doc_id, new_file)
    API->>Versioning: Mark HR-Policy_v1 as Obsolete (is_active = False)
    API->>Impact: Identify Affected Modules, Quizzes, and Employee Plans
    Impact->>DB: Query Plans Referencing HR-Policy_v1
    DB-->>Impact: Return 15 Affected Employee Onboarding Plans
    Impact->>DB: Update Status of Affected Plans (is_outdated = True)
    Impact-->>API: Return Impact Analysis Summary (Affected Modules & Plans)
    API-->>UI: Display Impact Analysis Tree (15 Plans, 3 Modules Affected)
    
    Admin->>UI: Click "Regenerate Affected Modules Only"
    UI->>API: POST /api/v1/plans/regenerate-selective (plan_ids, module_ids)
    API->>GenAI: Regenerate ONLY Affected Modules using HR-Policy_v2
    GenAI-->>API: Return Updated Module Content
    API->>DB: Update Affected Modules; Retain Unchanged Modules
    API-->>UI: Return Selective Regeneration Complete Notification
```

---

### Sequence Diagram 4: Manual Reviewer Override & Audit Logging

```mermaid
sequenceDiagram
    autonumber
    actor Reviewer as Authorized Reviewer
    participant UI as React UI
    participant API as FastAPI Backend
    participant ReviewQueue as Review Queue Subsystem
    participant Audit as Audit Logger
    participant DB as System Database

    Reviewer->>UI: View Manual Review Queue (/review-queue)
    UI->>API: GET /api/v1/review-queue
    API->>DB: Fetch Plans with Status 'Manual Review Required'
    DB-->>API: Return Flagged Items List
    API-->>UI: Display Flagged Plan Items & Mismatch Warnings

    Reviewer->>UI: Select Item, Select Action 'Approve with Override', Add Comment
    UI->>API: POST /api/v1/review-queue/override (item_id, decision, comment)
    API->>ReviewQueue: Process Override Decision
    API->>Audit: Log Audit Event (User ID, Timestamp, Original Status, Decision, Comment)
    Audit->>DB: Insert Immutable Row into audit_trail Table
    DB-->>Audit: Row Inserted
    API->>DB: Update Plan Item Status to Approved
    API-->>UI: Return HTTP 200 (Override Saved & Audit Logged)
    UI-->>Reviewer: Display Updated Verification Status & Audit Badge
```
