# SkillSprint AI — Production Backend Deployment Guide

## Overview
This document provides instructions for deploying, configuring, and running the **SkillSprint AI** production FastAPI backend server.

---

## 1. Environment Configuration

The application requires environment variables defined in `.env`:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Execution mode (`development` / `production`) | `production` |
| `SECRET_KEY` | HMAC-SHA256 secret key for signing JWT tokens | `skillsprint-ai-super-secret-jwt-key-...` |
| `DATABASE_URL` | SQLAlchemy database URI (SQLite or PostgreSQL) | `sqlite:///./skillsprint.db` or `postgresql://user:pass@localhost:5432/skillsprint` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `CORS_ORIGINS` | Allowed CORS origins for frontend client | `["http://localhost:3000"]` |

---

## 2. Local Startup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Seed Database & Run Migrations
```bash
python scripts/seed_dataset.py
```

### Step 3: Launch FastAPI Backend Server
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 3. Docker Container Deployment

### Option A: Docker Compose
```bash
docker-compose up -d --build
```

### Option B: Single Docker Container Build & Run
```bash
docker build -t skillsprint-api:latest .
docker run -d -p 8000:8000 -e GEMINI_API_KEY="your_api_key" skillsprint-api:latest
```

---

## 4. Verification & Health Monitoring

- **Health Check**: `GET http://localhost:8000/healthz`
- **Readiness Check**: `GET http://localhost:8000/readiness`
- **OpenAPI Documentation**: `http://localhost:8000/docs`
- **ReDoc Interactive Spec**: `http://localhost:8000/redoc`
