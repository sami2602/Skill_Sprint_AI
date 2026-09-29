"""
SkillSprint AI — Validation Evidence & Comparison Schemas
Defines structured Pydantic schemas for ground-truth validation evidence, requirement comparison items, and reviewer overrides.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class VerificationStatusEnum(str, Enum):
    VERIFIED = "VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    REJECTED = "REJECTED"


class ComparisonResultStatusEnum(str, Enum):
    COVERED = "COVERED"
    MISSING = "MISSING"
    PARTIALLY_COVERED = "PARTIALLY_COVERED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTORY = "CONTRADICTORY"
    OUTDATED_SOURCE = "OUTDATED_SOURCE"
    IRRELEVANT = "IRRELEVANT"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNGROUNDED = "UNGROUNDED"
    CONTRADICTION = "CONTRADICTION"


class ValidationEvidenceSchema(BaseModel):
    """Complete structured evidence schema produced by independent Python validation."""
    plan_id: str = Field(..., description="ID of the plan validated")
    role_id: str = Field(..., description="Target job role ID")
    mandatory_total: int = Field(default=0, description="Total mandatory requirements for role")
    mandatory_covered: int = Field(default=0, description="Covered mandatory requirements")
    mandatory_missing: List[str] = Field(default_factory=list, description="Missing mandatory requirement IDs")
    coverage_score: float = Field(default=0.0, description="Calculated coverage percentage (0.0 - 100.0)")

    traceable_items: int = Field(default=0, description="Count of validly cited items")
    untraceable_items: int = Field(default=0, description="Count of uncited/invalidly cited items")
    traceability_score: float = Field(default=0.0, description="Calculated traceability percentage (0.0 - 100.0)")

    unsupported_items: List[Dict[str, Any]] = Field(default_factory=list, description="Detected ungrounded content/hallucinations")
    duplicate_items: List[Dict[str, Any]] = Field(default_factory=list, description="Detected duplicate requirements/modules/tasks")
    contradictions: List[Dict[str, Any]] = Field(default_factory=list, description="Detected policy contradictions or outdated sources")
    outdated_sources: List[Dict[str, Any]] = Field(default_factory=list, description="Outdated document version references")
    role_irrelevance_flags: List[Dict[str, Any]] = Field(default_factory=list, description="Role-inappropriate content items")
    sequence_errors: List[Dict[str, Any]] = Field(default_factory=list, description="Prerequisite/stage ordering errors")
    quiz_errors: List[Dict[str, Any]] = Field(default_factory=list, description="Quiz answer or distractor validation errors")

    verification_status: VerificationStatusEnum = Field(..., description="Final deterministic verification status")
    execution_time_ms: float = Field(default=0.0, description="Validation engine execution time in milliseconds")

    model_config = ConfigDict(from_attributes=True)


class RequirementComparisonItem(BaseModel):
    """Itemized requirement-level comparison entry (SRS FR-42)."""
    requirement_id: str = Field(..., description="Requirement ID e.g. REQ-001")
    title: str = Field(..., description="Requirement title")
    requirement_text: Optional[str] = Field(None, description="Exact requirement wording")
    is_mandatory: bool = Field(default=True, description="Whether requirement is mandatory")
    role_id: str = Field(..., description="Job role ID")
    expected_behavior: str = Field(..., description="Ground-truth matrix expectation")
    generated_behavior: str = Field(..., description="Actual GenAI output summary")
    generated_content: Optional[str] = Field(None, description="Actual generated text/content")
    generated_coverage: Optional[str] = Field(None, description="Generated item coverage description")
    source_doc_id: str = Field(..., description="Source document code e.g. DOC-POL01")
    source_version: str = Field(..., description="Source document version e.g. 2.0")
    source_location: Optional[str] = Field(None, description="Source page/paragraph location ref")
    validation_rule: str = Field(..., description="Validation rule applied")
    validation_result: str = Field(default="PASSED", description="PASSED, FAILED, WARNING")
    result_status: ComparisonResultStatusEnum = Field(..., description="COVERED, MISSING, PARTIALLY_COVERED, UNSUPPORTED, CONTRADICTORY, OUTDATED_SOURCE, IRRELEVANT, NEEDS_REVIEW")
    evidence: str = Field(..., description="Detailed evidence description (Expected -> Generated -> Validated -> Decision)")
    reviewer_status: Optional[str] = Field(None, description="Reviewer decision: APPROVED, REJECTED, REVISED, OVERRIDDEN")
    reviewer_id: Optional[str] = Field(None, description="ID of authorized reviewer")
    reviewer_comment: Optional[str] = Field(None, description="Reviewer commentary")
    override_reason: Optional[str] = Field(None, description="Justification for override")

    model_config = ConfigDict(from_attributes=True)


class VerificationSummarySchema(BaseModel):
    """Calculated dynamic verification summary for an onboarding plan."""
    plan_id: str = Field(..., description="Target plan ID")
    role_id: str = Field(..., description="Target role ID")
    total_requirements: int = Field(default=0, description="Total requirements evaluated")
    mandatory_requirements: int = Field(default=0, description="Total mandatory requirements")
    mandatory_covered: int = Field(default=0, description="Covered mandatory requirements")
    mandatory_missing: int = Field(default=0, description="Missing mandatory requirements count")
    coverage_percentage: float = Field(default=0.0, description="Mandatory coverage percentage")
    traceable_items: int = Field(default=0, description="Count of traceable content items")
    untraceable_items: int = Field(default=0, description="Count of untraceable items")
    traceability_percentage: float = Field(default=0.0, description="Traceability percentage")
    unsupported_items: int = Field(default=0, description="Count of ungrounded/hallucinated items")
    duplicate_items: int = Field(default=0, description="Count of duplicate content items")
    contradictions: int = Field(default=0, description="Count of detected policy contradictions")
    outdated_sources: int = Field(default=0, description="Count of outdated document version references")
    role_irrelevance: int = Field(default=0, description="Count of role-irrelevant content items")
    sequence_errors: int = Field(default=0, description="Count of sequence/prerequisite errors")
    verification_status: VerificationStatusEnum = Field(..., description="VERIFIED, NEEDS_REVIEW, REJECTED")
    explanation: str = Field(..., description="Human-readable decision explanation")

    model_config = ConfigDict(from_attributes=True)


class RequirementComparisonReport(BaseModel):
    """Full requirement-level comparison report across all role matrix items."""
    plan_id: str = Field(..., description="Target onboarding plan ID")
    role_id: str = Field(..., description="Target job role ID")
    generated_at: str = Field(..., description="Timestamp of report generation")
    summary: Dict[str, Any] = Field(..., description="Match/mismatch statistics summary")
    items: List[RequirementComparisonItem] = Field(..., description="List of itemized comparisons")

    model_config = ConfigDict(from_attributes=True)


class ReviewerOverrideRequest(BaseModel):
    """Request payload for manual review override (SRS FR-44, FR-45)."""
    plan_id: str = Field(..., description="Plan ID")
    item_id: str = Field(..., description="Item ID flagged for review")
    review_id: Optional[str] = Field(None, description="Review item ID")
    action: str = Field(..., description="APPROVE, REJECT, REQUEST_REVISION, or OVERRIDE")
    reviewer_id: str = Field(..., description="ID/name of authorized reviewer")
    comment: str = Field(..., description="Mandatory justification comment")
    override_reason: Optional[str] = Field(None, description="Detailed override justification")

    model_config = ConfigDict(from_attributes=True)


class PolicyImpactAnalysisRequest(BaseModel):
    """Request payload for policy update impact analysis."""
    doc_id: str = Field(..., description="Target document ID e.g. DOC-POL01")
    old_version: Optional[str] = Field(None, description="Previous document version e.g. 1.0")
    new_version: str = Field(..., description="Updated document version e.g. 2.0")


class PolicyImpactAnalysisResponse(BaseModel):
    """Structured impact analysis result before selective regeneration."""
    doc_id: str = Field(..., description="Document ID analyzed")
    old_version: Optional[str] = Field(None, description="Previous version")
    new_version: str = Field(..., description="New version")
    affected_requirement_ids: List[str] = Field(default_factory=list)
    affected_roles: List[str] = Field(default_factory=list)
    affected_plan_ids: List[str] = Field(default_factory=list)
    affected_module_ids: List[str] = Field(default_factory=list)
    affected_task_ids: List[str] = Field(default_factory=list)
    affected_quiz_ids: List[str] = Field(default_factory=list)
    impact_timestamp: str = Field(..., description="Analysis timestamp")

    model_config = ConfigDict(from_attributes=True)


class SelectiveRegenerationRequest(BaseModel):
    """Request payload for selective module/task regeneration."""
    plan_id: str = Field(..., description="Target onboarding plan ID")
    doc_id: str = Field(..., description="Updated document ID")
    old_version: str = Field(..., description="Previous version")
    new_version: str = Field(..., description="New version")
    affected_module_ids: List[str] = Field(..., description="Modules targeted for regeneration")
    reason: str = Field(..., description="Reason for selective regeneration")
    requested_by: str = Field("SYSTEM", description="Reviewer/User ID requesting regeneration")


class SelectiveRegenerationResponse(BaseModel):
    """Result of selective regeneration."""
    plan_id: str = Field(..., description="Plan ID")
    regenerated_modules: List[str] = Field(..., description="IDs of modules regenerated")
    preserved_modules: List[str] = Field(..., description="IDs of modules preserved untouched")
    version_transition: str = Field(..., description="e.g. 1.0 -> 2.0")
    generation_event_id: str = Field(..., description="GenAI audit log entry ID")
    validation_status: str = Field(..., description="New verification status")
    audit_id: str = Field(..., description="Audit record ID")

    model_config = ConfigDict(from_attributes=True)

