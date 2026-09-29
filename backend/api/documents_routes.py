"""
SkillSprint AI — Document Management API Endpoints
Handles document upload, file validation, parsing, semantic chunking, version tracking, and metadata lookup.
"""

import os
import uuid
import re
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.models.models import Document, DocumentSection, DocumentChunk, PolicyVersionHistory, User
from backend.schemas.schemas import (
    DocumentResponse,
    DocumentDetailResponse,
    DocumentSectionSchema,
    DocumentChunkSchema,
    DocumentVersionInfo,
    PaginatedResponse
)
from security.auth import get_current_active_user, require_permission, require_role
from security.audit_service import AuditService
from document_processing.validation.validator import DocumentValidator
from document_processing.parsers.pdf_parser import PDFParser
from document_processing.parsers.docx_parser import DOCXParser
from document_processing.chunking.semantic_chunker import SemanticChunker

router = APIRouter(prefix="/api/v1/documents", tags=["Documents Management"])

UPLOAD_DIR = os.path.join(os.getcwd(), "data", "documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """Protects against path traversal attacks by extracting basename and sanitizing characters."""
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', clean_name)
    return clean_name


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: str = Form("Policy"),
    version: str = Form("1.0"),
    effective_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("upload_document"))
):
    """
    Uploads, validates, parses, chunks, and registers a company policy document (PDF/DOCX).
    Enforces security checks (path traversal, size, format, adversarial prompt injection).
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file missing filename.")

    safe_filename = sanitize_filename(file.filename)
    ext = os.path.splitext(safe_filename)[1].lower()
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed extensions: {settings.ALLOWED_EXTENSIONS}"
        )

    # Read bytes and check size
    file_bytes = file.file.read()
    if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
        )

    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty (0 bytes).")

    # Save to upload folder
    doc_uuid = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    file_path = os.path.join(UPLOAD_DIR, f"{doc_uuid}_{safe_filename}")
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Validate file and check existing checksums
    existing_checksums = [d.checksum for d in db.query(Document.checksum).all()]
    validator = DocumentValidator(existing_checksums=existing_checksums)
    val_result = validator.validate_file(file_path)

    if not val_result.is_valid:
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if val_result.is_adversarial:
            AuditService(db).log_event(
                event_type="PROMPT_INJECTION_FLAGGED",
                user_id=current_user.user_id,
                entity_type="DOCUMENT",
                entity_id=doc_uuid,
                reason=f"Adversarial document upload blocked: {val_result.adversarial_details}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Adversarial prompt injection content detected: {val_result.adversarial_details}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document validation failed: {'; '.join(val_result.error_messages)}"
        )

    doc_title = title or os.path.splitext(safe_filename)[0].replace("_", " ").title()

    # Create Document record
    doc_record = Document(
        doc_id=doc_uuid,
        title=doc_title,
        category=category,
        file_path=file_path,
        file_type=ext,
        file_size_bytes=len(file_bytes),
        version=version,
        is_active=True,
        effective_date=effective_date,
        expiry_date=expiry_date,
        checksum=val_result.checksum,
        validation_status="VALIDATED"
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Parse sections and text
    raw_sections = []
    if ext == ".pdf":
        parser = PDFParser()
        parsed_doc = parser.parse(file_path)
        raw_sections = parsed_doc.get("sections", [])
    elif ext == ".docx":
        parser = DOCXParser()
        parsed_doc = parser.parse(file_path)
        raw_sections = parsed_doc.get("sections", [])

    db_sections = []
    for sec in raw_sections:
        db_sec = DocumentSection(
            section_id=sec.get("section_id", f"SEC-{uuid.uuid4().hex[:6].upper()}"),
            document_id=doc_record.id,
            title=sec.get("title", "Untitled Section"),
            heading_level=sec.get("heading_level", 1),
            page_start=sec.get("page_start"),
            page_end=sec.get("page_end"),
            paragraph_start=sec.get("paragraph_start"),
            paragraph_end=sec.get("paragraph_end")
        )
        db.add(db_sec)
        db_sections.append(db_sec)
    
    db.commit()

    # Chunking
    chunker = SemanticChunker(target_chunk_words=200, overlap_words=30)
    for sec in db_sections:
        sec_text = sec.title
        chunks = chunker.chunk_text(
            text=sec_text,
            doc_id=doc_uuid,
            section_id=sec.section_id
        )
        for chk in chunks:
            db_chk = DocumentChunk(
                chunk_id=chk.chunk_id,
                document_id=doc_record.id,
                section_id=sec.id,
                heading=sec.title,
                text_content=chk.text_content,
                page_number=sec.page_start,
                paragraph_ref=f"Para {sec.paragraph_start}" if sec.paragraph_start else None,
                chunk_index=chk.chunk_index,
                token_count=chk.token_count,
                checksum=chk.checksum
            )
            db.add(db_chk)

    db.commit()

    # Audit logging
    AuditService(db).log_event(
        event_type="DOCUMENT_UPLOADED",
        user_id=current_user.user_id,
        entity_type="DOCUMENT",
        entity_id=doc_uuid,
        new_value={"title": doc_title, "category": category, "version": version}
    )

    return doc_record


@router.get("", response_model=PaginatedResponse[DocumentResponse])
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lists company documents with filtering, search, and pagination."""
    query = db.query(Document)
    if category:
        query = query.filter(Document.category.ilike(f"%{category}%"))
    if is_active is not None:
        query = query.filter(Document.is_active == is_active)
    if search:
        pattern = f"%{search}%"
        query = query.filter((Document.title.ilike(pattern)) | (Document.doc_id.ilike(pattern)))

    total = query.count()
    docs = query.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse[DocumentResponse](
        items=docs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{doc_id}", response_model=DocumentDetailResponse)
def get_document_detail(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves document detail including sections and total chunk count."""
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{doc_id}' not found.")

    sections = db.query(DocumentSection).filter(DocumentSection.document_id == doc.id).all()
    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()

    resp = DocumentDetailResponse.model_validate(doc)
    resp.sections = [DocumentSectionSchema.model_validate(s) for s in sections]
    resp.chunk_count = chunk_count
    return resp


@router.get("/{doc_id}/versions", response_model=List[DocumentVersionInfo])
def get_document_version_history(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves version history for a specific document."""
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{doc_id}' not found.")

    # Find documents with matching title or doc_id stem
    related_docs = db.query(Document).filter(
        (Document.title == doc.title) | (Document.doc_id == doc_id)
    ).order_by(Document.created_at.desc()).all()

    return [
        DocumentVersionInfo(
            doc_id=d.doc_id,
            title=d.title,
            category=d.category,
            version=d.version,
            is_active=d.is_active,
            created_at=d.created_at
        ) for d in related_docs
    ]


@router.get("/{doc_id}/sections", response_model=List[DocumentSectionSchema])
def get_document_sections(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves all sections belonging to a document."""
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{doc_id}' not found.")

    return db.query(DocumentSection).filter(DocumentSection.document_id == doc.id).all()


@router.get("/{doc_id}/chunks", response_model=List[DocumentChunkSchema])
def get_document_chunks(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves all text chunks belonging to a document (Authorized roles)."""
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{doc_id}' not found.")

    return db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index).all()
