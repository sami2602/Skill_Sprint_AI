"""
SkillSprint AI — Production FastAPI Backend Application Entrypoint
Exposes comprehensive REST API routes for authentication, RBAC, document management, requirements,
job roles, employees, GenAI plan generation, ground-truth Python validation, verification, human review,
audit trails, policy impact analysis, analytics, and data export reports.
"""

import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.database import init_db, SessionLocal
from backend.models.models import User
from security.auth import hash_password
from security.rbac import RBACPermissionError

# Routers
from backend.api.health_routes import router as health_router
from backend.api.auth_routes import router as auth_router
from backend.api.users_routes import router as users_router
from backend.api.documents_routes import router as documents_router
from backend.api.requirements_routes import router as requirements_router
from backend.api.roles_routes import router as roles_router
from backend.api.employees_routes import router as employees_router
from backend.api.generation_routes import router as generation_router
from backend.api.validation_routes import router as validation_router
from backend.api.verification_routes import router as verification_router
from backend.api.review_routes import router as review_router
from backend.api.audit_routes import router as audit_router
from backend.api.policy_impact_routes import router as policy_impact_router
from backend.api.analytics_routes import router as analytics_router
from backend.api.reports_routes import router as reports_router
from backend.api.learning_routes import router as learning_router
from backend.api.portal_routes import router as portal_router

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("skillsprint_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database tables and default user accounts on launch."""
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Seeding default authentication user accounts...")
    seed_default_users()
    logger.info("SkillSprint AI Backend API initialized and online.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Generative AI PowerPlay — Corporate Onboarding Intelligence Platform with Independent Ground-Truth Python Validation Engine",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Structured Global Error Handling
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        headers=exc.headers
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload or query parameters.",
                "details": exc.errors()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(RBACPermissionError)
async def rbac_exception_handler(request: Request, exc: RBACPermissionError):
    logger.warning(f"RBAC Permission denied on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": {
                "code": "FORBIDDEN",
                "message": str(exc.detail if hasattr(exc, 'detail') else exc)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred."
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# ==========================================
# Register Routers
# ==========================================

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(documents_router)
app.include_router(requirements_router)
app.include_router(roles_router)
app.include_router(employees_router)
app.include_router(generation_router)
app.include_router(validation_router)
app.include_router(verification_router)
app.include_router(review_router)
app.include_router(audit_router)
app.include_router(policy_impact_router)
app.include_router(analytics_router)
app.include_router(reports_router)
app.include_router(learning_router)
app.include_router(portal_router)



# ==========================================
# Startup Lifecycle & Database Seeding
# ==========================================

def seed_default_users():
    """Seeds default accounts and enterprise dataset if database is fresh."""
    db = SessionLocal()
    try:
        from scripts.seed_dataset import seed_database
        seed_database(db_session=db)
    except Exception as e:
        logger.error(f"User/Employee seeding error: {e}")
        db.rollback()
    finally:
        db.close()






@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "ONLINE",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/healthz"
    }
