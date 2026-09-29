"""
SkillSprint AI — Production Pydantic Schemas for API Requests & Responses
Defines typed DTOs and validation schemas for authentication, users, documents, requirements, roles,
employees, generation, validation, verification, human review, audit, policy impact, analytics, and reporting.
"""

from typing import List, Dict, Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime

T = TypeVar("T")


# ==========================================
# Reusable Pagination Schemas
# ==========================================

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number starting from 1")
    page_size: int = Field(20, ge=1, le=100, description="Items per page (max 100)")
    search: Optional[str] = Field(None, description="Global search query string")
    sort_by: Optional[str] = Field(None, description="Field name to sort by")
    sort_order: Optional[str] = Field("asc", description="Sort direction: 'asc' or 'desc'")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==========================================
# Authentication & User Schemas
# ==========================================

class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str
    expires_in: int


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)
    role: str = Field("EMPLOYEE", description="ADMIN, REVIEWER, MANAGER, TRAINING_MANAGER, EMPLOYEE")
    department: Optional[str] = None
    employee_id: Optional[str] = None


class EmployeeSignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Enterprise employee work email")
    password: str = Field(..., min_length=6)
    employee_id: Optional[str] = Field(None, description="Optional employee ID e.g. EMP-001")


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    department: Optional[str] = None
    employee_id: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    user_id: str
    username: str
    email: str
    role: str
    is_active: bool
    department: Optional[str] = None
    employee_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Document Processing Schemas
# ==========================================

class DocumentBase(BaseModel):
    doc_id: str
    title: str
    category: str
    file_type: str
    version: str = "1.0"
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None


class DocumentCreate(DocumentBase):
    file_path: str
    file_size_bytes: int
    checksum: str


class DocumentResponse(DocumentBase):
    id: int
    file_size_bytes: int
    checksum: str
    is_active: bool
    validation_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentSectionSchema(BaseModel):
    id: int
    section_id: str
    document_id: int
    title: str
    heading_level: int = 1
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    paragraph_start: Optional[int] = None
    paragraph_end: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentChunkSchema(BaseModel):
    chunk_id: str
    doc_id: Optional[str] = None
    section_id: Optional[Any] = None
    heading: Optional[str] = None
    text_content: str
    page_number: Optional[int] = None
    paragraph_ref: Optional[str] = None
    chunk_index: int
    token_count: int
    checksum: str
    id: Optional[int] = None
    document_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentResponse):
    sections: List[DocumentSectionSchema] = []
    chunk_count: int = 0


class DocumentVersionInfo(BaseModel):
    doc_id: str
    title: str
    category: str
    version: str
    is_active: bool
    created_at: datetime


# ==========================================
# Requirements & Roles Schemas
# ==========================================

class RequirementSchema(BaseModel):
    requirement_id: str
    doc_id: Optional[str] = None
    section_ref: str
    title: str
    requirement_text: str
    category: str
    priority: str
    modal_verb: str
    is_mandatory: bool
    target_roles: Optional[List[str]] = None
    department: Optional[str] = None
    sub_category: str = "policy"
    id: Optional[int] = None
    document_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RequirementDetailSchema(RequirementSchema):
    doc_title: Optional[str] = None
    doc_version: Optional[str] = None


class RoleSchema(BaseModel):
    id: int
    role_id: str
    title: str
    department: str
    experience_level: str = "All"
    description: Optional[str] = None
    required_skills: List[str] = []
    mandatory_requirements_count: int = 0
    total_requirements_count: int = 0
    coverage_percentage: float = 100.0

    model_config = ConfigDict(from_attributes=True)


class RoleMatrixItem(BaseModel):
    mapping_id: int
    requirement_id: str
    title: str
    requirement_text: str
    category: str
    priority: str
    is_mandatory: bool
    due_stage: str
    doc_id: Optional[str] = None
    section_ref: Optional[str] = None


class RoleDetailSchema(RoleSchema):
    requirement_matrix: List[RoleMatrixItem] = []
    mandatory_count: int = 0
    total_requirement_count: int = 0


# ==========================================
# Employee Schemas
# ==========================================

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    email: str
    role_id: int
    department: str
    experience_level: str = "Junior"
    joining_date: str
    manager_id: Optional[str] = None
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None
    department: Optional[str] = None
    experience_level: Optional[str] = None
    manager_id: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    id: int
    role_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeOnboardingStatusResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    role_id: str
    role_title: str
    plan_id: Optional[str] = None
    verification_status: Optional[str] = "NOT_STARTED"
    coverage_score: Optional[float] = 0.0
    traceability_score: Optional[float] = 0.0
    overall_progress_pct: float = 0.0
    onboarding_status: str = "NOT_STARTED"


# ==========================================
# Generation & Plan Schemas
# ==========================================

class GenerationRequest(BaseModel):
    role_id: str = Field(..., description="Target role ID e.g. ROL-01")
    employee_id: Optional[str] = Field(None, description="Optional target employee ID")
    experience_level: Optional[str] = Field("Junior", description="Junior, Mid, Senior, All")
    department: Optional[str] = Field(None, description="Department context")


class GenerationStatusResponse(BaseModel):
    plan_id: str
    role_id: str
    employee_id: Optional[str] = None
    role_title: str
    department: str
    version: str
    status: str
    created_at: datetime


class GeneratedPlanResponse(BaseModel):
    id: int
    plan_id: str
    role_id: str
    employee_id: Optional[str] = None
    role_title: str
    department: str
    version: str
    status: str
    provider_name: str
    model_name: str
    prompt_version: str
    payload_json: Dict[str, Any]
    covered_requirement_ids: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Review & Audit Schemas
# ==========================================

class ReviewQueueItemResponse(BaseModel):
    id: Optional[int] = None
    review_id: str
    plan_id: str
    item_id: str
    item_type: str
    flag_type: str
    evidence_data: Dict[str, Any]
    status: str
    reviewer_id: Optional[str] = None
    reviewer_comment: Optional[str] = None
    override_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewerActionRequest(BaseModel):
    review_id: str = Field(..., description="Review item ID")
    action: str = Field(..., description="APPROVE, REJECT, REQUEST_REVISION, OVERRIDE")
    reviewer_id: str = Field(..., description="ID of reviewer taking action")
    comment: str = Field(..., description="Reviewer commentary")
    override_reason: Optional[str] = Field(None, description="Reason for override if applicable")
    plan_id: Optional[str] = Field(None, description="Target plan ID")
    item_id: Optional[str] = Field(None, description="Target item ID")


class AuditLogResponse(BaseModel):
    audit_id: str
    event_type: str
    user_id: str
    entity_type: str
    entity_id: str
    original_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Analytics & Metrics Schemas
# ==========================================

class SystemMetricsResponse(BaseModel):
    document_count: int
    requirement_count: int
    role_count: int
    employee_count: int
    plan_count: int
    avg_coverage_score: float
    avg_traceability_score: float
    pending_reviews_count: int
    verification_status_distribution: Dict[str, int]


class OnboardingProgressAnalytics(BaseModel):
    total_enrolled: int
    completed_count: int
    on_track_count: int
    behind_schedule_count: int
    requires_attention_count: int


# ==========================================
# Legacy Document Validation Schemas
# ==========================================

class DocumentValidationResult(BaseModel):
    is_valid: bool
    file_name: str
    file_type: str
    file_size_bytes: int
    checksum: str
    error_messages: List[str] = []
    warnings: List[str] = []
    is_adversarial: bool = False
    adversarial_details: Optional[str] = None


class DatasetValidationSummary(BaseModel):
    document_count: int
    pdf_count: int
    docx_count: int
    role_count: int
    requirement_count: int
    mandatory_requirement_count: int
    role_specific_requirement_count: int
    conflicting_cases_count: int
    policy_version_updates_count: int
    adversarial_fixtures_count: int
    is_srs_compliant: bool
    validation_messages: List[str] = []

