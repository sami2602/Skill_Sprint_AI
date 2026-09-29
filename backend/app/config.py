"""
SkillSprint AI — Configuration & Environment Handling
"""

import os
from typing import List
from pydantic import BaseModel


def get_cors_origins() -> List[str]:
    cors_env = os.getenv("CORS_ORIGINS", "*")
    if not cors_env or cors_env.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in cors_env.split(",") if origin.strip()]


def get_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL", "sqlite:///./skillsprint.db")
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url


class Settings(BaseModel):
    APP_NAME: str = "SkillSprint AI REST API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "skillsprint-ai-super-secret-jwt-key-2026-phase7-production-secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = get_database_url()
    CORS_ORIGINS: List[str] = get_cors_origins()
    MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB max document upload size
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


settings = Settings()
