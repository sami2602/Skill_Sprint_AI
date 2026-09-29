# SkillSprint AI — Human Architectural & Product Decisions Required

## Overview
This document logs architectural, technology, and product decisions that require explicit alignment and confirmation from the human engineering team as required by Step 16 of the SRS Discovery Phase.

Where the SRS permits multiple implementation options, the Lead Architect has provided recommended defaults based on performance, security, and competition compliance.

---

## Decisions Table

| Decision ID | Area | Options Specified in SRS §1.9.2 | Lead Architect Recommendation | Rationale & Trade-offs | Human Team Decision Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEC-01** | **Backend Framework** | Flask, Django, FastAPI, Streamlit | **FastAPI (Python 3.14.7)** | High-performance async REST API, native Pydantic schema validation, automatic OpenAPI interactive docs. Clean decoupling from frontend. | **RECOMMENDED — PENDING TEAM SIGN-OFF** |
| **DEC-02** | **Frontend UI Tech Stack**| HTML5/CSS3/JS, Bootstrap, Streamlit, React | **React (Vite + TailwindCSS / Bootstrap)** | Rich interactive dashboards, drag-and-drop file upload, side-by-side diff matrices, and stateful review workflow UI. Streamlit lacks granular stateful comparison views. | **RECOMMENDED — PENDING TEAM SIGN-OFF** |
| **DEC-03** | **Database Engine** | MongoDB, PostgreSQL, MySQL, Firebase, SQLite | **SQLite (Dev) / PostgreSQL (Prod) via SQLAlchemy ORM** | Relational schema ensures strict referential integrity for audit trail & role matrix. ORM enables zero-code migration between SQLite and PostgreSQL. | **RECOMMENDED — PENDING TEAM SIGN-OFF** |
| **DEC-04** | **Primary GenAI Model** | Google Gemini API, OpenAI API, Anthropic API | **Google Gemini API (`gemini-2.5-flash`)** | Native structured JSON response schema enforcement, large context window for policy docs, fast execution latency. | **RECOMMENDED — PENDING TEAM SIGN-OFF** |
| **DEC-05** | **DOCX Line/Paragraph Citation Format** | Page numbers vs Paragraph indices | **Section Heading + Paragraph Index (e.g. `Para 4.2`)** | DOCX files lack fixed physical page numbers. Paragraph index provides exact text location reference. | **RECOMMENDED — PENDING TEAM SIGN-OFF** |
| **DEC-06** | **Cloud Deployment Hosting Provider** | Render, Railway, PythonAnywhere, Streamlit Cloud | **Render / Railway (Dockerized Deployment)** | Supports dual-container setup (FastAPI + React build) with PostgreSQL database integration. | **RECOMMENDED — PENDING TEAM SIGN-OFF** |
