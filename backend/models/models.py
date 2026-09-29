"""
SkillSprint AI — Database ORM Models
Defines all SQLAlchemy tables for documents, sections, chunks, roles, requirements, versioning, precedence, conflicts, and audit trails.
"""

from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database import Base


class RequirementCategoryEnum(str, enum.Enum):
    MUST_KNOW = "MUST_KNOW"
    MUST_COMPLETE = "MUST_COMPLETE"
    MUST_DEMONSTRATE = "MUST_DEMONSTRATE"
    MUST_ACKNOWLEDGE = "MUST_ACKNOWLEDGE"
    RECOMMENDED = "RECOMMENDED"
    OPTIONAL = "OPTIONAL"


class PriorityEnum(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ValidationStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    FLAGGED_ADVERSARIAL = "FLAGGED_ADVERSARIAL"


class ConflictTypeEnum(str, enum.Enum):
    CONTRADICTION = "CONTRADICTION"
    OUTDATED_SOURCE = "OUTDATED_SOURCE"
    AMBIGUOUS_CLAUSE = "AMBIGUOUS_CLAUSE"
    DUPLICATE_REQUIREMENT = "DUPLICATE_REQUIREMENT"
    SUPERSEDED_POLICY = "SUPERSEDED_POLICY"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True) # e.g. Policy, SOP, FAQ, Informal Guidance
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False) # .pdf, .docx
    file_size_bytes = Column(Integer, nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_date = Column(String(20), nullable=True)
    expiry_date = Column(String(20), nullable=True)
    checksum = Column(String(64), nullable=False, index=True)
    validation_status = Column(Enum(ValidationStatusEnum), default=ValidationStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    sections = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    requirements = relationship("PolicyRequirement", back_populates="document", cascade="all, delete-orphan")


class DocumentSection(Base):
    __tablename__ = "document_sections"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(String(64), index=True, nullable=False) # e.g. SEC-01, SEC-02
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    heading_level = Column(Integer, default=1)
    page_start = Column(Integer, nullable=True)
    page_end = Column(Integer, nullable=True)
    paragraph_start = Column(Integer, nullable=True)
    paragraph_end = Column(Integer, nullable=True)

    document = relationship("Document", back_populates="sections")
    chunks = relationship("DocumentChunk", back_populates="section")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(64), unique=True, index=True, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("document_sections.id", ondelete="SET NULL"), nullable=True)
    heading = Column(String(255), nullable=True)
    text_content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True) # PDF page ref
    paragraph_ref = Column(String(50), nullable=True) # DOCX paragraph ref e.g. Para 4.2
    chunk_index = Column(Integer, nullable=False)
    token_count = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("Document", back_populates="chunks")
    section = relationship("DocumentSection", back_populates="chunks")


class PolicyRequirement(Base):
    __tablename__ = "policy_requirements"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(String(64), unique=True, index=True, nullable=False) # REQ-001 ... REQ-165
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    section_ref = Column(String(100), nullable=False) # e.g. SEC-02 (Para 3)
    title = Column(String(255), nullable=False)
    requirement_text = Column(Text, nullable=False)
    category = Column(Enum(RequirementCategoryEnum), nullable=False, index=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.HIGH, nullable=False)
    modal_verb = Column(String(20), nullable=False) # must, shall, should, may, optional
    is_mandatory = Column(Boolean, default=True, nullable=False, index=True)
    target_roles = Column(JSON, nullable=True) # List of role_ids or ["ALL"]
    department = Column(String(100), nullable=True)
    sub_category = Column(String(100), default="policy", nullable=False) # policy, procedural, knowledge, task, compliance
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("Document", back_populates="requirements")
    role_mappings = relationship("RoleRequirementMapping", back_populates="requirement")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. ROL-01, ROL-02
    title = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    experience_level = Column(String(50), default="All", nullable=False)
    description = Column(Text, nullable=True)

    mappings = relationship("RoleRequirementMapping", back_populates="role")
    employees = relationship("Employee", back_populates="role")


class RoleRequirementMapping(Base):
    __tablename__ = "role_requirement_mappings"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("policy_requirements.id", ondelete="CASCADE"), nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    due_stage = Column(String(50), default="Day 1", nullable=False) # Day 1, Week 1, Week 2, 30 Days, 60 Days, 90 Days

    role = relationship("Role", back_populates="mappings")
    requirement = relationship("PolicyRequirement", back_populates="role_mappings")


class PolicyPrecedenceRule(Base):
    __tablename__ = "policy_precedence_rules"

    id = Column(Integer, primary_key=True, index=True)
    doc_category = Column(String(100), unique=True, nullable=False) # Policy, SOP, FAQ, Informal Guidance
    precedence_rank = Column(Integer, nullable=False) # 1 (Highest) -> 4 (Lowest)
    description = Column(Text, nullable=True)


class PolicyConflictFlag(Base):
    __tablename__ = "policy_conflict_flags"

    id = Column(Integer, primary_key=True, index=True)
    conflict_id = Column(String(64), unique=True, index=True, nullable=False)
    conflict_type = Column(Enum(ConflictTypeEnum), nullable=False, index=True)
    requirement_id_1 = Column(String(64), nullable=False)
    requirement_id_2 = Column(String(64), nullable=True)
    doc_id_1 = Column(String(64), nullable=False)
    doc_id_2 = Column(String(64), nullable=True)
    section_ref_1 = Column(String(100), nullable=True)
    section_ref_2 = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    resolution_status = Column(String(50), default="UNRESOLVED", nullable=False) # UNRESOLVED, RESOLVED_BY_PRECEDENCE, REVIEWER_OVERRIDDEN
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    department = Column(String(100), nullable=False)
    experience_level = Column(String(50), default="Junior", nullable=False)
    joining_date = Column(String(20), nullable=False)
    manager_id = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    role = relationship("Role", back_populates="employees")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="EMPLOYEE")  # ADMIN, REVIEWER, MANAGER, TRAINING_MANAGER, EMPLOYEE
    is_active = Column(Boolean, default=True, nullable=False)
    department = Column(String(100), nullable=True)
    employee_id = Column(String(64), ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)



class PolicyVersionHistory(Base):
    __tablename__ = "policy_version_history"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(64), index=True, nullable=False)
    old_version = Column(String(20), nullable=False)
    new_version = Column(String(20), nullable=False)
    replaced_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    change_summary = Column(Text, nullable=True)


class PolicyChangeImpact(Base):
    __tablename__ = "policy_change_impacts"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(64), index=True, nullable=False)
    old_version = Column(String(20), nullable=True)
    new_version = Column(String(20), nullable=False)
    affected_roles = Column(JSON, nullable=False)
    affected_requirement_count = Column(Integer, default=0, nullable=False)
    affected_plans = Column(JSON, nullable=True)
    affected_modules = Column(JSON, nullable=True)
    affected_tasks = Column(JSON, nullable=True)
    affected_quizzes = Column(JSON, nullable=True)
    impact_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class SecurityAuditLog(Base):
    __tablename__ = "security_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True) # e.g. PROMPT_INJECTION_FLAGGED, ADVERSARIAL_DOC_DETECTED
    source_document = Column(String(255), nullable=True)
    severity = Column(String(20), default="HIGH", nullable=False)
    details = Column(Text, nullable=False)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class GeneratedPlan(Base):
    __tablename__ = "generated_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(64), unique=True, index=True, nullable=False)
    role_id = Column(String(64), nullable=False, index=True)
    employee_id = Column(String(64), nullable=True, index=True)
    role_title = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    payload_json = Column(JSON, nullable=False)
    covered_requirement_ids = Column(JSON, nullable=False)
    provider_name = Column(String(50), nullable=False)
    model_name = Column(String(50), nullable=False)
    prompt_version = Column(String(20), nullable=False)
    status = Column(String(50), default="SUCCESS", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class GenAIGenerationAuditLog(Base):
    __tablename__ = "genai_generation_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    prompt_version = Column(String(20), nullable=False)
    provider = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    generation_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    input_requirement_ids = Column(JSON, nullable=False)
    source_versions = Column(JSON, nullable=False)
    output_schema_version = Column(String(20), default="1.0", nullable=False)
    generation_status = Column(String(50), nullable=False)
    error_info = Column(Text, nullable=True)


class ValidationRun(Base):
    __tablename__ = "validation_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    plan_id = Column(String(64), index=True, nullable=False)
    role_id = Column(String(64), index=True, nullable=False)
    verification_status = Column(String(50), nullable=False, index=True)
    coverage_score = Column(Float, nullable=False)
    traceability_score = Column(Float, nullable=False)
    mandatory_total = Column(Integer, default=0, nullable=False)
    mandatory_covered = Column(Integer, default=0, nullable=False)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    evidence_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ComparisonResultModel(Base):
    __tablename__ = "comparison_results"

    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(String(64), unique=True, index=True, nullable=False)
    plan_id = Column(String(64), index=True, nullable=False)
    role_id = Column(String(64), index=True, nullable=False)
    requirement_id = Column(String(64), index=True, nullable=False)
    requirement_text = Column(Text, nullable=True)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    generated_behavior = Column(Text, nullable=False)
    generated_content = Column(Text, nullable=True)
    generated_coverage = Column(Text, nullable=True)
    source_doc_id = Column(String(64), nullable=True)
    source_version = Column(String(20), nullable=True)
    source_location = Column(String(100), nullable=True)
    validation_rule = Column(String(100), nullable=False)
    validation_result = Column(String(50), default="PASSED", nullable=False)
    result_status = Column(String(50), nullable=False) # COVERED, MISSING, PARTIALLY_COVERED, UNSUPPORTED, CONTRADICTORY, OUTDATED_SOURCE, IRRELEVANT, NEEDS_REVIEW
    evidence = Column(Text, nullable=True)
    reviewer_status = Column(String(50), nullable=True) # APPROVED, REJECTED, REVISED, OVERRIDDEN
    reviewer_id = Column(String(64), nullable=True)
    reviewer_comment = Column(Text, nullable=True)
    override_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ManualReviewQueueItem(Base):
    __tablename__ = "manual_review_queue"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String(64), unique=True, index=True, nullable=False)
    plan_id = Column(String(64), index=True, nullable=False)
    item_id = Column(String(64), nullable=False) # requirement_id, task_id, quiz_id, etc.
    item_type = Column(String(50), nullable=False) # TASK, QUIZ, REQUIREMENT, MODULE
    flag_type = Column(String(100), nullable=False, index=True) # MISSING_MANDATORY, UNGROUNDED, CONTRADICTION, DUPLICATE, ROLE_IRRELEVANCE, SEQUENCE_ERROR, OUTDATED_SOURCE
    evidence_data = Column(JSON, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False, index=True) # PENDING, APPROVED, REJECTED, REVISED, OVERRIDDEN
    reviewer_id = Column(String(64), nullable=True)
    reviewer_comment = Column(Text, nullable=True)
    override_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String(64), unique=True, index=True, nullable=False)
    event_type = Column(String(100), nullable=False, index=True) # DOCUMENT_CHANGE, POLICY_VERSION_CHANGE, GENERATION_EVENT, VALIDATION_EVENT, COMPARISON_EVENT, VERIFICATION_DECISION, REVIEWER_ACTION, OVERRIDE, REGENERATION_EVENT
    user_id = Column(String(64), nullable=False) # Reviewer ID or SYSTEM
    entity_type = Column(String(50), nullable=False) # PLAN, ITEM, REQUIREMENT, DOCUMENT, MODULE
    entity_id = Column(String(64), nullable=False)
    original_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    dept_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), nullable=False)
    location = Column(String(100), default="San Francisco HQ", nullable=False)
    manager_name = Column(String(100), nullable=True)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False) # Technical, Business, Leadership, Compliance, Soft Skills
    description = Column(Text, nullable=True)


class Competency(Base):
    __tablename__ = "competencies"

    id = Column(Integer, primary_key=True, index=True)
    competency_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(64), ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(64), ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False, index=True)
    proficiency_level = Column(String(50), default="Intermediate", nullable=False) # Beginner, Intermediate, Advanced, Expert
    score = Column(Float, default=80.0, nullable=False)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(64), unique=True, index=True, nullable=False)
    course_code = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(50), default="Intermediate", nullable=False)
    duration_hours = Column(Float, default=2.0, nullable=False)
    description = Column(Text, nullable=False)
    passing_score = Column(Float, default=80.0, nullable=False)
    target_role_id = Column(String(64), nullable=True)


class CourseModule(Base):
    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(String(64), unique=True, index=True, nullable=False)
    course_id = Column(String(64), ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, default=1, nullable=False)
    content = Column(Text, nullable=True)


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    course_id = Column(String(64), nullable=True)
    module_id = Column(String(64), nullable=True)
    role_id = Column(String(64), nullable=True)
    requirement_id = Column(String(64), nullable=True)
    passing_score = Column(Float, default=80.0, nullable=False)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String(64), unique=True, index=True, nullable=False)
    quiz_id = Column(String(64), ForeignKey("quizzes.quiz_id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="SINGLE_CHOICE", nullable=False)
    options_json = Column(JSON, nullable=False)
    correct_option_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty = Column(String(50), default="MEDIUM", nullable=False)
    source_document_id = Column(String(64), nullable=True)
    source_section_id = Column(String(100), nullable=True)
    page_number = Column(Integer, nullable=True)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(String(64), nullable=False, index=True)
    employee_id = Column(String(64), nullable=True, index=True)
    quiz_id = Column(String(64), ForeignKey("quizzes.quiz_id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    answers_json = Column(JSON, nullable=False)
    attempted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)




