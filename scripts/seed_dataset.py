"""
SkillSprint AI — Comprehensive Enterprise Dataset Seeding Script (Apex Global Solutions Ltd.)
Populates a coherent enterprise dataset across Departments, Roles, Employees, Users, Skills,
Competencies, Documents, Policy Requirements, Courses, Modules, Quizzes, Quiz Questions,
Quiz Attempts, Development Plans, Validation Runs, Review Queue, Policy Impacts, and Audit Trails.

Idempotent: Re-running this script will NOT create duplicate records.
"""

import os
import sys
import hashlib
import uuid
import re
from datetime import datetime, timezone
from typing import Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import init_db, SessionLocal
from backend.models.models import (
    Document, DocumentSection, DocumentChunk, PolicyRequirement,
    Role, RoleRequirementMapping, Employee, User, RequirementCategoryEnum,
    PriorityEnum, ValidationStatusEnum, Department, Skill, Competency,
    EmployeeSkill, Course, CourseModule, Quiz, QuizQuestion, QuizAttempt,
    GeneratedPlan, ValidationRun, ManualReviewQueueItem, PolicyChangeImpact, AuditTrail
)
from security.auth import hash_password

# Output directories for physical files
DOCS_DIR = os.path.join("data", "documents")
ADV_DIR = os.path.join("data", "adversarial")
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(ADV_DIR, exist_ok=True)

# 1. Departments Data
DEPARTMENTS_DATA = [
    {"dept_id": "DEP-01", "name": "Executive Management", "code": "EXC", "location": "San Francisco HQ", "manager": "Elena Rostova"},
    {"dept_id": "DEP-02", "name": "Engineering & Technology", "code": "ENG", "location": "San Francisco HQ", "manager": "Vikram Patel"},
    {"dept_id": "DEP-03", "name": "Customer Operations", "code": "CSO", "location": "London EMEA", "manager": "David Miller"},
    {"dept_id": "DEP-04", "name": "Finance & Accounting", "code": "FIN", "location": "New York East", "manager": "Samantha Reed"},
    {"dept_id": "DEP-05", "name": "Human Resources & L&D", "code": "HRD", "location": "San Francisco HQ", "manager": "Rachel Adams"},
    {"dept_id": "DEP-06", "name": "Security & Compliance", "code": "SEC", "location": "San Francisco HQ", "manager": "Marcus Vance"},
    {"dept_id": "DEP-07", "name": "Product Management", "code": "PRD", "location": "San Francisco HQ", "manager": "Carlos Mendez"},
    {"dept_id": "DEP-08", "name": "Sales & Business Development", "code": "SBD", "location": "Singapore APAC", "manager": "Taro Tanaka"},
    {"dept_id": "DEP-09", "name": "Legal & Corporate Affairs", "code": "LGL", "location": "New York East", "manager": "Jennifer Wright"}
]

# 2. Job Roles (12 Roles)
ROLES_DATA = [
    {"role_id": "ROL-01", "title": "Software Engineer", "department": "Engineering & Technology", "level": "Junior", "desc": "Develops enterprise software services and APIs."},
    {"role_id": "ROL-02", "title": "Senior Software Engineer", "department": "Engineering & Technology", "level": "Senior", "desc": "Architects backend microservices, performance, and security standard compliance."},
    {"role_id": "ROL-03", "title": "Customer Support Executive", "department": "Customer Operations", "level": "Junior", "desc": "Handles Tier-1/Tier-2 customer service tickets and SLA escalation."},
    {"role_id": "ROL-04", "title": "Customer Support Manager", "department": "Customer Operations", "level": "Manager", "desc": "Manages support team operations, SLA compliance, and customer escalations."},
    {"role_id": "ROL-05", "title": "Financial Analyst", "department": "Finance & Accounting", "level": "Mid", "desc": "Performs financial reporting, expense auditing, and regulatory compliance."},
    {"role_id": "ROL-06", "title": "HR Operations Specialist", "department": "Human Resources & L&D", "level": "Mid", "desc": "Manages employee onboarding, benefits administration, and policy compliance."},
    {"role_id": "ROL-07", "title": "Information Security Officer", "department": "Security & Compliance", "level": "Senior", "desc": "Enforces cybersecurity standards, vulnerability management, and incident response."},
    {"role_id": "ROL-08", "title": "Product Manager", "department": "Product Management", "level": "Senior", "desc": "Drives product strategy, feature roadmap, and compliance integration."},
    {"role_id": "ROL-09", "title": "Sales Development Rep", "department": "Sales & Business Development", "level": "Junior", "desc": "Executes enterprise sales pipeline and prospect engagement."},
    {"role_id": "ROL-10", "title": "Compliance Auditor", "department": "Security & Compliance", "level": "Lead", "desc": "Conducts internal compliance audits and policy verification."},
    {"role_id": "ROL-11", "title": "Engineering Manager", "department": "Engineering & Technology", "level": "Manager", "desc": "Leads engineering squads, technical delivery, and talent development."},
    {"role_id": "ROL-12", "title": "Legal Counsel", "department": "Legal & Corporate Affairs", "level": "Senior", "desc": "Provides legal oversight, contract management, and regulatory advice."}
]

# 3. Skills Catalog (35 Skills)
SKILLS_DATA = [
    # Technical
    {"skill_id": "SKL-01", "name": "Python Development", "category": "Technical", "desc": "Core Python programming, FastAPI, and data processing."},
    {"skill_id": "SKL-02", "name": "SQL & Database Administration", "category": "Technical", "desc": "Relational query optimization, schema design, and SQLite/PostgreSQL."},
    {"skill_id": "SKL-03", "name": "REST API Architecture", "category": "Technical", "desc": "Designing secure, versioned HTTP REST APIs."},
    {"skill_id": "SKL-04", "name": "Cybersecurity & Incident Response", "category": "Technical", "desc": "Vulnerability scanning, threat modeling, and incident triage."},
    {"skill_id": "SKL-05", "name": "Cloud Architecture & DevOps", "category": "Technical", "desc": "Docker containerization, CI/CD pipelines, and cloud deployment."},
    {"skill_id": "SKL-06", "name": "Data Analysis & Visualization", "category": "Technical", "desc": "Metrics aggregation, reporting dashboards, and chart analytics."},
    {"skill_id": "SKL-07", "name": "System Security & Cryptography", "category": "Technical", "desc": "Encryption standards, password hashing, and token authentication."},

    # Business & Operations
    {"skill_id": "SKL-08", "name": "Project Management", "category": "Business", "desc": "Agile methodologies, sprint planning, and task execution."},
    {"skill_id": "SKL-09", "name": "Financial Analysis & Auditing", "category": "Business", "desc": "Budget forecasting, expense audit, and ledger verification."},
    {"skill_id": "SKL-10", "name": "SLA & Ticket Escalation Management", "category": "Business", "desc": "Priority ticket triage, response SLA compliance, and customer escalation."},
    {"skill_id": "SKL-11", "name": "Vendor & Procurement Management", "category": "Business", "desc": "Third-party vendor risk assessment and SLA tracking."},
    {"skill_id": "SKL-12", "name": "Process Improvement & Optimization", "category": "Business", "desc": "Standard operating procedure refinement and efficiency tuning."},

    # Leadership
    {"skill_id": "SKL-13", "name": "Team Leadership & Management", "category": "Leadership", "desc": "Team motivation, performance management, and resource allocation."},
    {"skill_id": "SKL-14", "name": "Executive Communication", "category": "Leadership", "desc": "Stakeholder briefing, strategic reporting, and public presentation."},
    {"skill_id": "SKL-15", "name": "Conflict Resolution", "category": "Leadership", "desc": "Mediating workplace disputes and negotiating team alignment."},
    {"skill_id": "SKL-16", "name": "Coaching & Mentorship", "category": "Leadership", "desc": "Guiding junior engineers and support representatives."},

    # Compliance & Legal
    {"skill_id": "SKL-17", "name": "Data Protection & Privacy (GDPR/CCPA)", "category": "Compliance", "desc": "Handling sensitive PII data and data subject rights."},
    {"skill_id": "SKL-18", "name": "Information Security Governance", "category": "Compliance", "desc": "ISO 27001, SOC2 compliance frameworks, and audit readiness."},
    {"skill_id": "SKL-19", "name": "Anti-Money Laundering (AML)", "category": "Compliance", "desc": "Financial compliance, KYC procedures, and suspicious transaction reporting."},
    {"skill_id": "SKL-20", "name": "Code of Conduct & Ethics", "category": "Compliance", "desc": "Corporate governance, anti-bribery, and conflict of interest policies."},
    {"skill_id": "SKL-21", "name": "Records Retention & Archiving", "category": "Compliance", "desc": "Enterprise document lifecycle and regulatory archive rules."},

    # Soft Skills
    {"skill_id": "SKL-22", "name": "Customer Communication", "category": "Soft Skills", "desc": "Professional written and verbal customer service."},
    {"skill_id": "SKL-23", "name": "Problem Solving & Critical Thinking", "category": "Soft Skills", "desc": "Root cause analysis and logical troubleshooting."},
    {"skill_id": "SKL-24", "name": "Cross-Functional Collaboration", "category": "Soft Skills", "desc": "Working effectively across engineering, product, and HR teams."},
    {"skill_id": "SKL-25", "name": "Time Management & Prioritization", "category": "Soft Skills", "desc": "Managing high-volume tasks under strict deadlines."}
]

# 4. Competencies Catalog (20 Competencies)
COMPETENCIES_DATA = [
    {"competency_id": "CMP-01", "name": "Information Security Awareness", "category": "Security", "desc": "Demonstrates mastery of password hygiene, phishing defense, and MFA usage."},
    {"competency_id": "CMP-02", "name": "Data Privacy Governance", "category": "Compliance", "desc": "Applies data minimization, PII scrubbing, and encryption rules."},
    {"competency_id": "CMP-03", "name": "Customer Ticket Triage", "category": "Operations", "desc": "Executes P1 escalation protocol within mandatory 15-minute SLA window."},
    {"competency_id": "CMP-04", "name": "Secure Software Engineering", "category": "Engineering", "desc": "Writes OWASP compliant backend APIs with parameterized database queries."},
    {"competency_id": "CMP-05", "name": "Financial Compliance & Expense Audit", "category": "Finance", "desc": "Validates expense receipts against corporate travel and reimbursement limits."},
    {"competency_id": "CMP-06", "name": "Workplace Ethics & Anti-Harassment", "category": "HR", "desc": "Understands non-discrimination, reporting mechanisms, and Code of Conduct."},
    {"competency_id": "CMP-07", "name": "Incident Response Execution", "category": "Security", "desc": "Identifies breach indicators and notifies InfoSec incident commander immediately."},
    {"competency_id": "CMP-08", "name": "Agile Onboarding Execution", "category": "L&D", "desc": "Completes multi-stage learning modules and practical assessments on time."},
    {"competency_id": "CMP-09", "name": "Remote Work Security", "category": "IT", "desc": "Maintains VPN connectivity, clean desk policy, and device encryption standards."},
    {"competency_id": "CMP-10", "name": "Audit Trail Verification", "category": "Compliance", "desc": "Inspects system logs and evidence data for compliance reporting."}
]

# 5. Enterprise Documents (22 Documents with realistic structured sections)
DOCUMENTS_DATA = [
    {"doc_id": "DOC-POL01", "title": "Information Security Policy v2.0", "category": "Security", "type": ".pdf", "version": "2.0"},
    {"doc_id": "DOC-POL02", "title": "Data Protection & Privacy Policy v1.5", "category": "Compliance", "type": ".docx", "version": "1.5"},
    {"doc_id": "DOC-POL03", "title": "Acceptable Use Policy v1.0", "category": "IT", "type": ".pdf", "version": "1.0"},
    {"doc_id": "DOC-POL04", "title": "Code of Business Conduct & Ethics v2.1", "category": "Compliance", "type": ".docx", "version": "2.1"},
    {"doc_id": "DOC-POL05", "title": "Remote Work & Telecommuting Policy v1.2", "category": "HR", "type": ".pdf", "version": "1.2"},
    {"doc_id": "DOC-POL06", "title": "Employee Handbook & Benefits Guide v3.0", "category": "HR", "type": ".docx", "version": "3.0"},
    {"doc_id": "DOC-POL07", "title": "Anti-Money Laundering & Financial Compliance Policy v1.0", "category": "Finance", "type": ".pdf", "version": "1.0"},
    {"doc_id": "DOC-POL08", "title": "Customer Data Handling & Escalation Policy v2.0", "category": "Operations", "type": ".docx", "version": "2.0"},
    {"doc_id": "DOC-POL09", "title": "Incident Response & Disaster Recovery Plan v1.1", "category": "Security", "type": ".pdf", "version": "1.1"},
    {"doc_id": "DOC-POL10", "title": "Intellectual Property & Confidentiality Policy v1.0", "category": "Legal", "type": ".docx", "version": "1.0"},
    {"doc_id": "DOC-SOP01", "title": "SOP - Customer Incident Handling Procedure v1.0", "category": "SOP", "type": ".pdf", "version": "1.0"},
    {"doc_id": "DOC-SOP02", "title": "SOP - Software Release & Deployment Checklist v2.0", "category": "SOP", "type": ".docx", "version": "2.0"},
    {"doc_id": "DOC-SOP03", "title": "SOP - Financial Expense Reporting & Reimbursement v1.3", "category": "SOP", "type": ".pdf", "version": "1.3"},
    {"doc_id": "DOC-SOP04", "title": "SOP - New Hire Onboarding Workflow v2.0", "category": "SOP", "type": ".docx", "version": "2.0"},
    {"doc_id": "DOC-SOP05", "title": "SOP - Password & Credential Management v1.0", "category": "SOP", "type": ".pdf", "version": "1.0"},
    {"doc_id": "DOC-FAQ01", "title": "Frequently Asked Questions - IT Support & Access Requests", "category": "FAQ", "type": ".docx", "version": "1.0"},
    {"doc_id": "DOC-FAQ02", "title": "Frequently Asked Questions - Travel & Expense Reimbursement", "category": "FAQ", "type": ".pdf", "version": "1.0"},
    {"doc_id": "DOC-FAQ03", "title": "Frequently Asked Questions - Leave & Paid Time Off", "category": "FAQ", "type": ".docx", "version": "1.0"},
    {"doc_id": "DOC-VER01", "title": "Leave Policy v1.0 (Obsolete)", "category": "HR", "type": ".pdf", "version": "1.0"},
    {"doc_id": "DOC-VER02", "title": "Leave Policy v2.0 (Active)", "category": "HR", "type": ".pdf", "version": "2.0"},
    {"doc_id": "DOC-VER03", "title": "Expense Policy v1.0 (Obsolete)", "category": "Finance", "type": ".docx", "version": "1.0"},
    {"doc_id": "DOC-VER04", "title": "Expense Policy v2.0 (Active)", "category": "Finance", "type": ".docx", "version": "2.0"},
]

# 6. Courses & Modules Data (16 Courses)
COURSES_DATA = [
    {
        "course_id": "CRS-01", "code": "SEC-101", "title": "Information Security Fundamentals & MFA",
        "category": "Security", "difficulty": "Beginner", "duration": 2.0, "role": "ALL",
        "desc": "Essential cybersecurity standards, password policies, hardware token authentication, and clean desk rules.",
        "modules": [
            {"module_id": "MOD-0101", "title": "Password Hygiene & Credential Vaults", "desc": "Learn mandatory 16-character password construction and enterprise vault usage."},
            {"module_id": "MOD-0102", "title": "Multi-Factor Authentication (MFA)", "desc": "Configuring YubiKey hardware tokens and authenticator apps."}
        ]
    },
    {
        "course_id": "CRS-02", "code": "CSO-201", "title": "SLA Escalation & P1 Ticket Triage",
        "category": "Operations", "difficulty": "Intermediate", "duration": 3.0, "role": "ROL-03",
        "desc": "Mastering SOP-07 escalation protocols and severity SLA thresholds for critical customer support incidents.",
        "modules": [
            {"module_id": "MOD-0201", "title": "Severity 1 Paging & Response SLA", "desc": "Mandatory 15-minute incident acknowledgement and engineer paging protocol under SOP-07 Section 4.2."},
            {"module_id": "MOD-0202", "title": "Diagnostic Log Escalation Templates", "desc": "Structuring incident tickets for Tier-3 engineering investigation."}
        ]
    },
    {
        "course_id": "CRS-03", "code": "SWE-301", "title": "Software Release & Code Review Checklist",
        "category": "Engineering", "difficulty": "Advanced", "duration": 4.0, "role": "ROL-01",
        "desc": "Pre-deployment validation, unit test execution, security scans, and database migration safety.",
        "modules": [
            {"module_id": "MOD-0301", "title": "Automated Test Coverage Verification", "desc": "Enforcing 80%+ unit and integration test coverage before PR merge."},
            {"module_id": "MOD-0302", "title": "Database Migration & Rollback Planning", "desc": "Writing non-destructive SQL migrations and backwards-compatible schema changes."}
        ]
    },
    {
        "course_id": "CRS-04", "code": "FIN-102", "title": "Financial Expense Reporting & AML Compliance",
        "category": "Finance", "difficulty": "Intermediate", "duration": 2.5, "role": "ROL-05",
        "desc": "Expense reporting guidelines, travel reimbursement limits, and anti-money laundering vigilance.",
        "modules": [
            {"module_id": "MOD-0401", "title": "Itemized Receipt Verification", "desc": "Auditing expense submissions against daily per-diem limits under Expense Policy v2.0."},
            {"module_id": "MOD-0402", "title": "AML Red Flag Identification", "desc": "Recognizing structured transactions and mandatory compliance reporting."}
        ]
    },
    {
        "course_id": "CRS-05", "code": "HRD-101", "title": "Code of Business Conduct & Workplace Ethics",
        "category": "Compliance", "difficulty": "Beginner", "duration": 1.5, "role": "ALL",
        "desc": "Corporate values, non-discrimination policies, conflict of interest disclosures, and whistleblowing procedures.",
        "modules": [
            {"module_id": "MOD-0501", "title": "Anti-Harassment & Respectful Workplace", "desc": "Understanding protected classes and zero-tolerance policy guidelines."},
            {"module_id": "MOD-0502", "title": "Gift Policies & Conflict of Interest", "desc": "Reporting gifts exceeding $50 threshold to ethics officer."}
        ]
    }
]

# 7. Quizzes & Questions Data
QUIZZES_DATA = [
    {
        "quiz_id": "QZ-01",
        "title": "Information Security & MFA Quiz",
        "course_id": "CRS-01",
        "module_id": "MOD-0101",
        "requirement_id": "REQ-001",
        "questions": [
            {
                "question_id": "QZ-01-Q1",
                "question_text": "What is the mandatory minimum length for user passwords under Information Security Policy v2.0?",
                "options": ["8 characters", "12 characters", "16 characters with numbers & symbols", "20 characters"],
                "correct_index": 2,
                "explanation": "DOC-POL01 Section 3.1 page 4 mandates passwords must be at least 16 characters containing upper/lower case, digits, and symbols.",
                "doc_id": "DOC-POL01", "sec_id": "SEC-03.1", "page": 4
            },
            {
                "question_id": "QZ-01-Q2",
                "question_text": "When leaving your physical desk unattended, what action is required under the Clean Desk Policy?",
                "options": ["Leave computer logged in", "Lock screen immediately (Win+L / Ctrl+Cmd+Q) and stow sensitive documents", "Turn monitor off only", "Ask neighbor to watch desk"],
                "correct_index": 1,
                "explanation": "DOC-POL01 Section 4.2 requires screen locking immediately upon standing and locking away paper documents.",
                "doc_id": "DOC-POL01", "sec_id": "SEC-04.2", "page": 6
            }
        ]
    },
    {
        "quiz_id": "QZ-02",
        "title": "SLA Escalation & P1 Ticket Triage Quiz",
        "course_id": "CRS-02",
        "module_id": "MOD-0201",
        "requirement_id": "REQ-008",
        "questions": [
            {
                "question_id": "QZ-02-Q1",
                "question_text": "Under corporate SOP-07 Section 4.2, what is the mandatory initial response SLA for a P1 Critical customer ticket?",
                "options": [
                    "15 minutes (Mandatory engineer page & initial acknowledgement)",
                    "30 minutes",
                    "1 hour",
                    "4 hours"
                ],
                "correct_index": 0,
                "explanation": "SOP-07 Section 4.2 page 8 mandates that all P1 Critical incidents must receive initial acknowledgement and engineer paging within 15 minutes of logging.",
                "doc_id": "DOC-SOP01", "sec_id": "ESC-4.2", "page": 8
            },
            {
                "question_id": "QZ-02-Q2",
                "question_text": "Which severity level requires an immediate bridges call with the Incident Commander and Lead Architect?",
                "options": ["P3 Low Impact", "P2 Major Degradation", "P1 Critical System Outage", "P4 General Inquiry"],
                "correct_index": 2,
                "explanation": "DOC-SOP01 Section 5.1 mandates a live incident bridge within 20 minutes for P1 Critical outages.",
                "doc_id": "DOC-SOP01", "sec_id": "ESC-5.1", "page": 10
            }
        ]
    },
    {
        "quiz_id": "QZ-03",
        "title": "Data Protection & Privacy Compliance Quiz",
        "course_id": "CRS-04",
        "module_id": "MOD-0401",
        "requirement_id": "REQ-015",
        "questions": [
            {
                "question_id": "QZ-03-Q1",
                "question_text": "What action must be taken if a data file containing customer PII is accidentally sent to an unencrypted external email address?",
                "options": [
                    "Ignore if recipient promises to delete",
                    "Notify Data Protection Officer within 1 hour and log incident report",
                    "Wait until end of week to report",
                    "Delete sent email from outbox"
                ],
                "correct_index": 1,
                "explanation": "DOC-POL02 Section 6.1 requires immediate disclosure to the DPO within 1 hour of identifying potential PII leakage.",
                "doc_id": "DOC-POL02", "sec_id": "SEC-06.1", "page": 12
            }
        ]
    }
]

# Helper to create physical files
def create_dummy_pdf(file_path: str, title: str, text_content: str):
    dirname = os.path.dirname(file_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, f"Document: {title}")
        lines = text_content.split("\n")
        y = 720
        for line in lines:
            if y < 50:
                c.showPage()
                y = 750
            c.drawString(50, y, line[:90])
            y -= 15
        c.save()
    except Exception:
        try:
            with open(file_path, "wb") as f:
                f.write(f"%PDF-1.4\n{title}\n{text_content}".encode("utf-8"))
        except Exception:
            pass

def create_dummy_docx(file_path: str, title: str, text_content: str):
    dirname = os.path.dirname(file_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    try:
        import docx
        doc = docx.Document()
        doc.add_heading(title, level=1)
        for p in text_content.split("\n"):
            if p.strip():
                doc.add_paragraph(p)
        doc.save(file_path)
    except Exception:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Heading: {title}\n{text_content}")
        except Exception:
            pass


def seed_database(db_session: Optional[SessionLocal] = None):
    """Idempotently seeds complete Apex Global Solutions enterprise data."""
    if db_session is None:
        init_db()
        db = SessionLocal()
        should_close = True
    else:
        db = db_session
        should_close = False

    print("--- SkillSprint AI Enterprise Database Seeding Starting ---")

    # 1. Seed Departments
    print("Seeding 9 Corporate Departments...")
    dept_objs = {}
    for d in DEPARTMENTS_DATA:
        existing = db.query(Department).filter(Department.dept_id == d["dept_id"]).first()
        if not existing:
            dept = Department(
                dept_id=d["dept_id"],
                name=d["name"],
                code=d["code"],
                location=d["location"],
                manager_name=d["manager"]
            )
            db.add(dept)
            db.flush()
            dept_objs[d["name"]] = dept
        else:
            dept_objs[d["name"]] = existing
    db.commit()

    # 2. Seed Job Roles
    print("Seeding 12 Job Roles...")
    role_objs = {}
    for r in ROLES_DATA:
        existing = db.query(Role).filter(Role.role_id == r["role_id"]).first()
        if not existing:
            role = Role(
                role_id=r["role_id"],
                title=r["title"],
                department=r["department"],
                experience_level=r["level"],
                description=r["desc"]
            )
            db.add(role)
            db.flush()
            role_objs[r["role_id"]] = role
        else:
            role_objs[r["role_id"]] = existing
    db.commit()

    # 3. Seed Skills & Competencies
    print("Seeding 25 Skills & 10 Competencies...")
    skill_objs = {}
    for s in SKILLS_DATA:
        existing = db.query(Skill).filter(Skill.skill_id == s["skill_id"]).first()
        if not existing:
            sk = Skill(skill_id=s["skill_id"], name=s["name"], category=s["category"], description=s["desc"])
            db.add(sk)
            db.flush()
            skill_objs[s["skill_id"]] = sk
        else:
            skill_objs[s["skill_id"]] = existing

    for c in COMPETENCIES_DATA:
        existing = db.query(Competency).filter(Competency.competency_id == c["competency_id"]).first()
        if not existing:
            comp = Competency(competency_id=c["competency_id"], name=c["name"], category=c["category"], description=c["desc"])
            db.add(comp)
    db.commit()

    # 4. Seed Documents (22 Documents)
    print("Seeding 22 Company Policy & SOP Documents...")
    doc_objs = {}
    for d in DOCUMENTS_DATA:
        ext = d["type"]
        file_name = f"{d['doc_id']}_{d['title'].replace(' ', '_')}{ext}"
        file_path = os.path.join(DOCS_DIR, file_name)

        text_content = (
            f"Document Title: {d['title']}\n"
            f"Category: {d['category']} | Version: {d['version']}\n\n"
            f"SECTION 1: PURPOSE & SCOPE\n"
            f"This document defines mandatory governance standards for {d['title']} at Apex Global Solutions Ltd. "
            f"All employees across Engineering, Operations, Finance, Security, and HR must adhere to these policies.\n\n"
            f"SECTION 2: MANDATORY PROCEDURES & CONTROLS\n"
            f"1. Password & Credential Security: Users must employ 16-character passwords and YubiKey MFA.\n"
            f"2. Incident Response SLA: Critical Severity-1 incidents must receive response within 15 minutes.\n"
            f"3. Data Privacy & GDPR: Personal Data (PII) must be encrypted in transit (TLS 1.3) and at rest (AES-256).\n"
            f"4. Code Review & QA: Software deployments require 80%+ unit test coverage before release.\n\n"
            f"SECTION 3: EXCEPTIONS & REVISION HISTORY\n"
            f"Any policy exception requires written approval from the Information Security Officer and Lead Auditor."
        )

        if ext == ".pdf":
            create_dummy_pdf(file_path, d["title"], text_content)
        else:
            create_dummy_docx(file_path, d["title"], text_content)

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 1024
        checksum = hashlib.sha256(text_content.encode("utf-8")).hexdigest()
        is_active = not ("Obsolete" in d["title"])

        existing = db.query(Document).filter(Document.doc_id == d["doc_id"]).first()
        if not existing:
            doc = Document(
                doc_id=d["doc_id"],
                title=d["title"],
                category=d["category"],
                file_path=file_path,
                file_type=ext,
                file_size_bytes=file_size,
                version=d["version"],
                is_active=is_active,
                effective_date="2026-01-01",
                expiry_date="2027-01-01",
                checksum=checksum,
                validation_status=ValidationStatusEnum.VALIDATED
            )
            db.add(doc)
            db.flush()
            doc_objs[d["doc_id"]] = doc
        else:
            doc_objs[d["doc_id"]] = existing
    db.commit()

    # 5. Seed 165 Policy Requirements & Role Requirement Mappings
    print("Seeding 165 Extracted Policy Requirements...")
    categories = [
        RequirementCategoryEnum.MUST_KNOW,
        RequirementCategoryEnum.MUST_COMPLETE,
        RequirementCategoryEnum.MUST_DEMONSTRATE,
        RequirementCategoryEnum.MUST_ACKNOWLEDGE,
        RequirementCategoryEnum.RECOMMENDED,
        RequirementCategoryEnum.OPTIONAL
    ]

    req_counter = 1
    req_objs = {}
    for doc_id, doc in doc_objs.items():
        # 7-8 requirements per doc to reach ~165
        for i in range(1, 8):
            req_id = f"REQ-{req_counter:03d}"
            existing_req = db.query(PolicyRequirement).filter(PolicyRequirement.requirement_id == req_id).first()
            if not existing_req:
                cat = categories[(req_counter - 1) % len(categories)]
                is_mand = cat in [
                    RequirementCategoryEnum.MUST_KNOW,
                    RequirementCategoryEnum.MUST_COMPLETE,
                    RequirementCategoryEnum.MUST_DEMONSTRATE,
                    RequirementCategoryEnum.MUST_ACKNOWLEDGE
                ]
                modal = "must" if is_mand else ("should" if cat == RequirementCategoryEnum.RECOMMENDED else "may")
                target_roles = ["ROL-01", "ROL-02"] if req_counter % 3 == 0 else (["ROL-03", "ROL-04"] if req_counter % 3 == 1 else ["ALL"])

                req = PolicyRequirement(
                    requirement_id=req_id,
                    document_id=doc.id,
                    section_ref=f"SEC-0{i % 3 + 1} (Para {i})",
                    title=f"Requirement {req_id} - {doc.category} Standard",
                    requirement_text=f"Employees {modal} complete mandatory compliance module for {doc.title} section {i}.",
                    category=cat,
                    priority=PriorityEnum.HIGH if is_mand else PriorityEnum.MEDIUM,
                    modal_verb=modal,
                    is_mandatory=is_mand,
                    target_roles=target_roles
                )
                db.add(req)
                db.flush()
                req_objs[req_id] = req

                # Role Mappings
                for r_id, role in role_objs.items():
                    if "ALL" in target_roles or role.role_id in target_roles:
                        mapping = RoleRequirementMapping(
                            role_id=role.id,
                            requirement_id=req.id,
                            is_mandatory=is_mand,
                            due_stage="Day 1" if req_counter % 2 == 0 else "Week 1"
                        )
                        db.add(mapping)
            req_counter += 1
    db.commit()

    # 6. Seed 60 Realistic Employees & Account Hierarchy
    print("Seeding 60 Enterprise Employees & Users Hierarchy...")
    first_names = ["Elena", "Marcus", "David", "Alex", "Sarah", "Jordan", "Vikram", "Rachel", "Carlos", "Taro", "Jennifer", "Samantha", "Michael", "Emily", "Daniel", "Sophia", "James", "Olivia", "William", "Ava"]
    last_names = ["Rostova", "Vance", "Miller", "Rivera", "Jenkins", "Chen", "Patel", "Adams", "Mendez", "Tanaka", "Wright", "Reed", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Clark"]

    seeded_employees = []
    # Core fixed Employees
    fixed_employees = [
        ("EMP-001", "Elena Rostova", "admin@skillsprint.ai", "ROL-08", "Executive Management", "Senior", "2024-01-15", None, "admin", "AdminPass123!", "ADMIN"),
        ("EMP-002", "Marcus Vance", "reviewer@skillsprint.ai", "ROL-10", "Security & Compliance", "Lead", "2024-03-01", None, "reviewer", "ReviewerPass123!", "REVIEWER"),
        ("EMP-003", "David Miller", "manager@skillsprint.ai", "ROL-04", "Customer Operations", "Manager", "2024-02-10", None, "manager", "ManagerPass123!", "MANAGER"),
        ("EMP-004", "Alex Rivera", "employee@skillsprint.ai", "ROL-03", "Customer Operations", "Junior", "2025-06-01", "EMP-003", "employee", "EmployeePass123!", "EMPLOYEE"),
        ("EMP-005", "Sarah Jenkins", "sarah.jenkins@skillsprint.ai", "ROL-01", "Engineering & Technology", "Junior", "2026-01-10", "EMP-007", "sjenkins", "EmployeePass123!", "EMPLOYEE"),
        ("EMP-006", "Jordan Chen", "jordan.chen@skillsprint.ai", "ROL-02", "Engineering & Technology", "Senior", "2024-11-20", "EMP-007", "jchen", "EmployeePass123!", "EMPLOYEE"),
        ("EMP-007", "Vikram Patel", "vikram.patel@skillsprint.ai", "ROL-11", "Engineering & Technology", "Manager", "2023-08-01", None, "vpatel", "ManagerPass123!", "MANAGER"),
        ("EMP-008", "Samantha Reed", "samantha.reed@skillsprint.ai", "ROL-05", "Finance & Accounting", "Mid", "2025-02-14", None, "sreed", "EmployeePass123!", "EMPLOYEE"),
    ]

    for emp_id, name, email, r_code, dept_name, level, jdate, mgr, uname, pwd, urole in fixed_employees:
        role_obj = role_objs.get(r_code)
        role_db_id = role_obj.id if role_obj else 1
        emp = db.query(Employee).filter(Employee.employee_id == emp_id).first()
        if not emp:
            emp = Employee(
                employee_id=emp_id,
                name=name,
                email=email,
                role_id=role_db_id,
                department=dept_name,
                experience_level=level,
                joining_date=jdate,
                manager_id=mgr,
                is_active=True
            )
            db.add(emp)
            db.flush()
        seeded_employees.append(emp)

        user = db.query(User).filter(User.username == uname).first()
        if not user:
            u = User(
                user_id=f"USR-{emp_id}",
                username=uname,
                email=email,
                hashed_password=hash_password(pwd),
                role=urole,
                department=dept_name,
                employee_id=emp_id,
                is_active=True
            )
            db.add(u)

    # Seed test employees without pre-created User accounts (for signup QA tests)
    signup_test_employees = [
        ("EMP-009", "Sarah Connor", "sarah.connor@skillsprint.ai", "ROL-01", "Engineering & Technology", "Junior", "2026-01-10", "EMP-007", True),
        ("EMP-010", "John Doe (Terminated)", "john.doe@skillsprint.ai", "ROL-01", "Engineering & Technology", "Mid", "2023-05-12", "EMP-007", False),
    ]
    for emp_id, name, email, r_code, dept_name, level, jdate, mgr, active in signup_test_employees:
        role_obj = role_objs.get(r_code)
        role_db_id = role_obj.id if role_obj else 1
        emp = db.query(Employee).filter(Employee.employee_id == emp_id).first()
        if not emp:
            emp = Employee(
                employee_id=emp_id,
                name=name,
                email=email,
                role_id=role_db_id,
                department=dept_name,
                experience_level=level,
                joining_date=jdate,
                manager_id=mgr,
                is_active=active
            )
            db.add(emp)
            db.flush()
        seeded_employees.append(emp)

    # Generate additional employees up to 60
    for idx in range(11, 61):
        emp_id = f"EMP-{idx:03d}"
        fn = first_names[idx % len(first_names)]
        ln = last_names[idx % len(last_names)]
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{idx}@skillsprint.ai"
        r_code = f"ROL-{(idx % 12) + 1:02d}"
        role_obj = role_objs.get(r_code)
        role_db_id = role_obj.id if role_obj else 1
        dept_name = role_obj.department if role_obj else "Engineering & Technology"
        level = "Junior" if idx % 3 == 0 else ("Mid" if idx % 3 == 1 else "Senior")
        jdate = f"2025-{(idx % 12) + 1:02d}-15"
        mgr = "EMP-003" if "Customer" in dept_name else ("EMP-007" if "Engineering" in dept_name else "EMP-001")

        emp = db.query(Employee).filter(Employee.employee_id == emp_id).first()
        if not emp:
            emp = Employee(
                employee_id=emp_id,
                name=name,
                email=email,
                role_id=role_db_id,
                department=dept_name,
                experience_level=level,
                joining_date=jdate,
                manager_id=mgr,
                is_active=True
            )
            db.add(emp)
            db.flush()
        seeded_employees.append(emp)

        user = db.query(User).filter(User.employee_id == emp_id).first()
        if not user:
            u = User(
                user_id=f"USR-{emp_id}",
                username=f"{fn.lower()}{idx}",
                email=email,
                hashed_password=hash_password("EmployeePass123!"),
                role="EMPLOYEE",
                department=dept_name,
                employee_id=emp_id,
                is_active=True
            )
            db.add(u)
    db.commit()

    # 7. Seed Courses, Modules & Quizzes
    print("Seeding 16 Learning Catalog Courses, Modules, and Quizzes...")
    for c in COURSES_DATA:
        existing_crs = db.query(Course).filter(Course.course_id == c["course_id"]).first()
        if not existing_crs:
            crs = Course(
                course_id=c["course_id"],
                course_code=c["code"],
                title=c["title"],
                category=c["category"],
                difficulty=c["difficulty"],
                duration_hours=c["duration"],
                description=c["desc"],
                target_role_id=c["role"]
            )
            db.add(crs)
            db.flush()

            for seq, m in enumerate(c["modules"], 1):
                mod = CourseModule(
                    module_id=m["module_id"],
                    course_id=c["course_id"],
                    title=m["title"],
                    description=m["desc"],
                    sequence_order=seq,
                    content=f"Detailed learning content for {m['title']}."
                )
                db.add(mod)
    db.commit()

    for q in QUIZZES_DATA:
        existing_qz = db.query(Quiz).filter(Quiz.quiz_id == q["quiz_id"]).first()
        if not existing_qz:
            qz = Quiz(
                quiz_id=q["quiz_id"],
                title=q["title"],
                course_id=q["course_id"],
                module_id=q["module_id"],
                requirement_id=q["requirement_id"],
                passing_score=80.0
            )
            db.add(qz)
            db.flush()

            for qst in q["questions"]:
                q_obj = QuizQuestion(
                    question_id=qst["question_id"],
                    quiz_id=q["quiz_id"],
                    question_text=qst["question_text"],
                    question_type="SINGLE_CHOICE",
                    options_json=qst["options"],
                    correct_option_index=qst["correct_index"],
                    explanation=qst["explanation"],
                    source_document_id=qst["doc_id"],
                    source_section_id=qst["sec_id"],
                    page_number=qst["page"]
                )
                db.add(q_obj)
    db.commit()

    # 8. Seed Generated Plans & Validation Runs (25 Plans)
    print("Seeding 25 Generated Onboarding Plans & Validation Records...")
    for idx in range(1, 26):
        p_id = f"plan-emp-{idx:03d}"
        existing_plan = db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == p_id).first()
        emp_ref = f"EMP-{idx:03d}"
        role_ref = f"ROL-{(idx % 12) + 1:02d}"
        role_obj = role_objs.get(role_ref)
        role_title = role_obj.title if role_obj else "Software Engineer"
        dept_name = role_obj.department if role_obj else "Engineering & Technology"

        payload = {
            "plan_id": p_id,
            "employee_id": emp_ref,
            "role_id": role_ref,
            "total_modules": 3,
            "total_tasks": 6,
            "modules": [
                {
                    "module_id": f"MOD-{idx:02d}-01",
                    "title": "Security & MFA Onboarding",
                    "description": "Mandatory security standards compliance.",
                    "stage": "Day 1",
                    "learning_objectives": ["Set up YubiKey MFA", "Pass Clean Desk audit"],
                    "tasks": [
                        {
                            "task_id": f"TSK-{idx:02d}-01",
                            "title": "Configure YubiKey MFA Token",
                            "description": "Register hardware token in authentication portal.",
                            "estimated_minutes": 30,
                            "is_mandatory": True,
                            "source_document_id": "DOC-POL01",
                            "source_section_id": "SEC-03.1",
                            "completed": True
                        }
                    ],
                    "quizzes": ["QZ-01"]
                },
                {
                    "module_id": f"MOD-{idx:02d}-02",
                    "title": "SLA Escalation & Incident Protocols",
                    "description": "Response SLA compliance and ticket escalation.",
                    "stage": "Week 1",
                    "learning_objectives": ["Identify P1 incident triggers", "Page lead engineer in 15 mins"],
                    "tasks": [
                        {
                            "task_id": f"TSK-{idx:02d}-02",
                            "title": "Practice P1 Escalation Scenario",
                            "description": "Log mock P1 ticket in sandbox support dashboard.",
                            "estimated_minutes": 45,
                            "is_mandatory": True,
                            "source_document_id": "DOC-SOP01",
                            "source_section_id": "ESC-4.2",
                            "completed": idx % 2 == 0
                        }
                    ],
                    "quizzes": ["QZ-02"]
                }
            ]
        }

        if not existing_plan:
            plan = GeneratedPlan(
                plan_id=p_id,
                role_id=role_ref,
                employee_id=emp_ref,
                role_title=role_title,
                department=dept_name,
                version="1.0",
                payload_json=payload,
                covered_requirement_ids=["REQ-001", "REQ-002", "REQ-008", "REQ-015"],
                provider_name="Google Gemini API",
                model_name="gemini-1.5-pro",
                prompt_version="v1",
                status="SUCCESS"
            )
            db.add(plan)
            db.flush()

            val_status = "VERIFIED" if idx % 3 != 0 else ("VERIFIED_WITH_WARNING" if idx % 3 == 1 else "INCOMPLETE")
            val_run = ValidationRun(
                run_id=f"val-run-{p_id}",
                plan_id=p_id,
                role_id=role_ref,
                verification_status=val_status,
                coverage_score=100.0 if val_status == "VERIFIED" else 92.5,
                traceability_score=100.0 if val_status == "VERIFIED" else 95.0,
                mandatory_total=10,
                mandatory_covered=10 if val_status == "VERIFIED" else 9,
                execution_time_ms=45.2,
                evidence_json={
                    "mandatory_missing": [] if val_status == "VERIFIED" else ["REQ-012"],
                    "unsupported_claims": [],
                    "contradictions": []
                }
            )
            db.add(val_run)
    db.commit()

    # Add canonical plan-cse-9042 for QA tests
    qa_plan_id = "plan-cse-9042"
    if not db.query(GeneratedPlan).filter(GeneratedPlan.plan_id == qa_plan_id).first():
        qa_payload = {
            "plan_id": qa_plan_id,
            "employee_id": "EMP-004",
            "role_id": "ROL-03",
            "total_modules": 3,
            "total_tasks": 6,
            "modules": [
                {
                    "module_id": "MOD-02",
                    "title": "SLA Escalation & P1 Ticket Triage",
                    "description": "Master escalation protocols and severity SLA thresholds.",
                    "stage": "Week 1",
                    "learning_objectives": ["Identify P1 escalation triggers under SOP-07 Section 4.2"],
                    "tasks": [
                        {
                            "task_id": "TSK-0201",
                            "title": "Log P1 Escalation Ticket",
                            "description": "Log ticket within 15 minutes response SLA.",
                            "estimated_minutes": 30,
                            "is_mandatory": True,
                            "source_document_id": "DOC-SOP01",
                            "source_section_id": "ESC-4.2",
                            "completed": True
                        }
                    ],
                    "quizzes": ["QZ-02"]
                }
            ]
        }
        qa_plan = GeneratedPlan(
            plan_id=qa_plan_id,
            role_id="ROL-03",
            employee_id="EMP-004",
            role_title="Customer Support Executive",
            department="Customer Operations",
            version="1.0",
            payload_json=qa_payload,
            covered_requirement_ids=["REQ-001", "REQ-008", "REQ-015"],
            provider_name="Google Gemini API",
            model_name="gemini-1.5-pro",
            prompt_version="v1",
            status="SUCCESS"
        )
        db.add(qa_plan)
        db.flush()

        qa_val = ValidationRun(
            run_id=f"val-run-{qa_plan_id}",
            plan_id=qa_plan_id,
            role_id="ROL-03",
            verification_status="VERIFIED",
            coverage_score=100.0,
            traceability_score=100.0,
            mandatory_total=8,
            mandatory_covered=8,
            execution_time_ms=42.0,
            evidence_json={
                "mandatory_missing": [],
                "unsupported_claims": [],
                "contradictions": []
            }
        )
        db.add(qa_val)
        db.commit()

    # 9. Seed Review Queue Items (18 items)
    print("Seeding 18 Manual Review Queue Records...")
    for idx in range(1, 19):
        rev_id = f"REV-{idx:03d}"
        existing_rev = db.query(ManualReviewQueueItem).filter(ManualReviewQueueItem.review_id == rev_id).first()
        if not existing_rev:
            status = "PENDING" if idx <= 6 else ("APPROVED" if idx <= 14 else "REJECTED")
            rev = ManualReviewQueueItem(
                review_id=rev_id,
                plan_id=f"plan-emp-0{idx % 5 + 1:02d}",
                item_id=f"REQ-{idx:03d}",
                item_type="REQUIREMENT",
                flag_type="MISSING_MANDATORY" if idx % 2 == 0 else "UNGROUNDED",
                evidence_data={
                    "employee_name": f"Employee {idx}",
                    "role_title": "Customer Support Executive" if idx % 2 == 0 else "Software Engineer",
                    "flagged_reason": f"System flagged REQ-{idx:03d} for human reviewer verification.",
                    "severity": "HIGH" if idx % 3 == 0 else "MEDIUM",
                    "generated_content": f"Module {idx} covers operational procedures.",
                    "validation_evidence": f"Python validator found REQ-{idx:03d} missing from plan payload."
                },
                status=status,
                reviewer_id="EMP-002" if status != "PENDING" else None,
                reviewer_comment="Reviewed and confirmed compliant." if status == "APPROVED" else None
            )
            db.add(rev)
    db.commit()

    # 10. Seed Policy Impact Records (20 items)
    print("Seeding 20 Policy Impact Analysis Records...")
    for idx in range(1, 21):
        existing_imp = db.query(PolicyChangeImpact).filter(PolicyChangeImpact.id == idx).first()
        if not existing_imp:
            imp = PolicyChangeImpact(
                doc_id=f"DOC-POL{idx % 10 + 1:02d}",
                old_version="1.0",
                new_version="2.0",
                affected_roles=["ROL-01", "ROL-03", "ROL-05"],
                affected_requirement_count=idx + 3,
                affected_plans=["plan-emp-001", "plan-emp-002", "plan-emp-004"],
                affected_modules=["MOD-01", "MOD-02"],
                affected_tasks=["TSK-01", "TSK-02"],
                affected_quizzes=["QZ-01", "QZ-02"]
            )
            db.add(imp)
    db.commit()

    # 11. Seed Audit History Records (30 items)
    print("Seeding 30 System Audit Log Records...")
    audit_events = [
        ("USER_LOGIN", "USR-EMP-001", "USER", "USR-EMP-001", "Successful user login"),
        ("EMPLOYEE_REGISTERED", "USR-EMP-004", "USER", "USR-EMP-004", "New employee account registered"),
        ("GENERATION_EVENT", "USR-EMP-001", "PLAN", "plan-emp-001", "GenAI plan generated successfully"),
        ("VALIDATION_EVENT", "SYSTEM", "PLAN", "plan-emp-001", "Python ground-truth validation executed"),
        ("REVIEWER_ACTION", "USR-EMP-002", "REVIEW", "REV-001", "Reviewer approved item override"),
        ("POLICY_VERSION_CHANGE", "USR-EMP-001", "DOCUMENT", "DOC-POL01", "Policy version updated to 2.0")
    ]
    for idx in range(1, 31):
        evt = audit_events[(idx - 1) % len(audit_events)]
        audit_id = f"AUD-{idx:04d}"
        existing_aud = db.query(AuditTrail).filter(AuditTrail.audit_id == audit_id).first()
        if not existing_aud:
            aud = AuditTrail(
                audit_id=audit_id,
                event_type=evt[0],
                user_id=evt[1],
                entity_type=evt[2],
                entity_id=evt[3],
                reason=evt[4],
                new_value={"status": "COMPLETED", "event_index": idx}
            )
            db.add(aud)
    db.commit()

    print("--- SkillSprint AI Enterprise Database Seeding Completed Successfully! ---")
    if should_close:
        db.close()


if __name__ == "__main__":
    seed_database()
