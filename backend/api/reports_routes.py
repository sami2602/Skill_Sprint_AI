"""
SkillSprint AI — Reports & Data Export API Endpoints
Generates validation, comparison, security, and exportable CSV/JSON reports (FR-58, FR-59).
"""

import io
import csv
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.models.models import (
    ValidationRun,
    ComparisonResultModel,
    SecurityAuditLog,
    Document,
    GeneratedPlan,
    User
)
from security.auth import get_current_active_user, require_role

router = APIRouter(prefix="/api/v1/reports", tags=["Reports & Exports"])


@router.get("/validation")
def get_validation_report(
    plan_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generates ground-truth validation report from actual DB validation runs (FR-58)."""
    query = db.query(ValidationRun)
    if plan_id:
        query = query.filter(ValidationRun.plan_id == plan_id)

    runs = query.all()
    report_data = [
        {
            "run_id": r.run_id,
            "plan_id": r.plan_id,
            "role_id": r.role_id,
            "verification_status": r.verification_status,
            "coverage_score": r.coverage_score,
            "traceability_score": r.traceability_score,
            "mandatory_total": r.mandatory_total,
            "mandatory_covered": r.mandatory_covered,
            "execution_time_ms": r.execution_time_ms,
            "created_at": r.created_at.isoformat()
        } for r in runs
    ]

    return {
        "report_type": "VALIDATION_SUMMARY_REPORT",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_runs": len(runs),
        "data": report_data
    }


@router.get("/security")
def get_security_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "REVIEWER"]))
):
    """Generates security and prompt injection audit report (FR-58)."""
    logs = db.query(SecurityAuditLog).order_by(SecurityAuditLog.detected_at.desc()).all()
    return {
        "report_type": "SECURITY_ADVERSARIAL_REPORT",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "incident_count": len(logs),
        "incidents": [
            {
                "id": l.id,
                "event_type": l.event_type,
                "source_document": l.source_document,
                "severity": l.severity,
                "details": l.details,
                "detected_at": l.detected_at.isoformat()
            } for l in logs
        ]
    }


@router.get("/export")
def export_report_data(
    report_type: str = Query("validation", description="validation, comparison, security"),
    format: str = Query("json", description="json, csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Exports system report data in JSON or CSV format (FR-59)."""
    if report_type == "validation":
        runs = db.query(ValidationRun).all()
        rows = [
            {
                "run_id": r.run_id,
                "plan_id": r.plan_id,
                "role_id": r.role_id,
                "status": r.verification_status,
                "coverage_score": r.coverage_score,
                "traceability_score": r.traceability_score
            } for r in runs
        ]
    elif report_type == "security":
        logs = db.query(SecurityAuditLog).all()
        rows = [
            {
                "id": l.id,
                "event_type": l.event_type,
                "severity": l.severity,
                "details": l.details,
                "detected_at": l.detected_at.isoformat()
            } for l in logs
        ]
    else:
        docs = db.query(Document).all()
        rows = [
            {
                "doc_id": d.doc_id,
                "title": d.title,
                "category": d.category,
                "version": d.version,
                "is_active": d.is_active
            } for d in docs
        ]

    if format.lower() == "csv":
        output = io.StringIO()
        if rows:
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=skillsprint_{report_type}_report.csv"}
        )

    return {
        "export_type": report_type,
        "format": "json",
        "row_count": len(rows),
        "rows": rows
    }
