"""
SkillSprint AI — Pydantic Schemas for GenAI Generation Pipeline
Defines strict output schemas for onboarding plans, learning modules, tasks, quizzes, source citations, and generation metadata.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SourceCitation(BaseModel):
    """Source provenance tracking for grounded items."""
    doc_id: str = Field(..., description="Unique document ID, e.g. DOC-POL-01")
    doc_version: str = Field(default="1.0", description="Document version number")
    section_id: str = Field(..., description="Section reference, e.g. SEC-02")
    page_number: Optional[int] = Field(None, description="Page number for PDF documents")
    paragraph_ref: Optional[str] = Field(None, description="Paragraph ref for DOCX documents")
    requirement_id: str = Field(..., description="Associated policy requirement ID, e.g. REQ-001")

    model_config = ConfigDict(from_attributes=True)


class RequirementMapping(BaseModel):
    """Maps generated content to Role Requirement Matrix items."""
    requirement_id: str = Field(..., description="Requirement ID covered by this content")
    is_mandatory: bool = Field(default=True, description="Whether this requirement is mandatory")
    coverage_type: str = Field(default="DIRECT_TASK", description="Type of coverage: DIRECT_TASK, QUIZ_ASSESSMENT, MODULE_LESSON")
    justification: str = Field(..., description="Explanation of how content satisfies the requirement")

    model_config = ConfigDict(from_attributes=True)


class OnboardingTask(BaseModel):
    """Individual action item within an onboarding module."""
    task_id: str = Field(..., description="Unique task identifier, e.g. TSK-101")
    title: str = Field(..., description="Clear action title")
    description: str = Field(..., description="Detailed instructions for the employee")
    due_stage: str = Field(..., description="Onboarding stage: Preboarding, Day 1, Week 1, Week 2, Month 1, Month 2+")
    estimated_minutes: int = Field(default=30, description="Estimated completion time in minutes")
    is_mandatory: bool = Field(default=True, description="Mandatory vs optional task")
    prerequisite_task_ids: List[str] = Field(default_factory=list, description="Prerequisite tasks before starting")
    source_citations: List[SourceCitation] = Field(default_factory=list, description="Source policy citations")
    requirement_mappings: List[RequirementMapping] = Field(default_factory=list, description="Covered requirement IDs")

    model_config = ConfigDict(from_attributes=True)


class QuizOption(BaseModel):
    """Single option choice in a multiple-choice question."""
    option_id: str = Field(..., description="Option identifier, e.g. A, B, C, D")
    option_text: str = Field(..., description="Text of the choice option")
    is_correct: bool = Field(..., description="True if this is the ground-truth correct option")
    explanation: str = Field(..., description="Explanation of why option is correct or incorrect")

    model_config = ConfigDict(from_attributes=True)


class QuizQuestion(BaseModel):
    """Individual question within a quiz."""
    question_id: str = Field(..., description="Unique question identifier, e.g. QST-201")
    question_text: str = Field(..., description="Question statement")
    question_type: str = Field(default="MULTIPLE_CHOICE", description="MULTIPLE_CHOICE or TRUE_FALSE")
    options: List[QuizOption] = Field(..., description="List of answer choices (minimum 2)")
    correct_answer_id: str = Field(..., description="Option ID of the correct answer")
    explanation: str = Field(..., description="Detailed explanation of the correct answer based on source policy")
    requirement_id: str = Field(..., description="Target policy requirement ID tested")
    source_citation: SourceCitation = Field(..., description="Direct source policy reference")

    model_config = ConfigDict(from_attributes=True)


class Quiz(BaseModel):
    """Assessment quiz module."""
    quiz_id: str = Field(..., description="Unique quiz identifier, e.g. QZ-301")
    title: str = Field(..., description="Quiz title")
    description: str = Field(..., description="Overview of topics evaluated in this quiz")
    passing_score_percentage: float = Field(default=80.0, description="Required score percentage to pass")
    questions: List[QuizQuestion] = Field(..., description="Questions contained in this quiz")
    requirement_ids: List[str] = Field(default_factory=list, description="Requirement IDs assessed by this quiz")

    model_config = ConfigDict(from_attributes=True)


class LearningModule(BaseModel):
    """Multi-stage learning module containing tasks and assessments."""
    module_id: str = Field(..., description="Unique module ID, e.g. MOD-01")
    title: str = Field(..., description="Module title")
    summary: str = Field(..., description="High-level module summary")
    learning_objectives: List[str] = Field(..., description="List of learning outcomes")
    stage: str = Field(..., description="Target stage: Preboarding, Day 1, Week 1, Week 2, Month 1, Month 2+")
    estimated_duration_minutes: int = Field(default=60, description="Total duration for this module")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite module IDs")
    tasks: List[OnboardingTask] = Field(default_factory=list, description="Tasks included in this module")
    quizzes: List[Quiz] = Field(default_factory=list, description="Quizzes included in this module")
    requirement_mappings: List[RequirementMapping] = Field(default_factory=list, description="Requirements addressed")
    source_citations: List[SourceCitation] = Field(default_factory=list, description="Underlying source citations")

    model_config = ConfigDict(from_attributes=True)


class GeneratedContentMetadata(BaseModel):
    """Audit metadata attached to generated plans."""
    prompt_version: str = Field(..., description="Version of the prompt template used")
    provider: str = Field(..., description="GenAI provider name, e.g. Gemini")
    model: str = Field(..., description="Model identifier, e.g. gemini-2.5-flash")
    generation_timestamp: str = Field(..., description="ISO 8601 timestamp of generation")
    input_requirement_ids: List[str] = Field(..., description="List of input requirement IDs from matrix")
    source_versions: Dict[str, str] = Field(default_factory=dict, description="Map of doc_id to active version")
    output_schema_version: str = Field(default="1.0", description="Schema version of generated payload")
    generation_status: str = Field(default="SUCCESS", description="SUCCESS, RETRIED, FAILED, PARTIAL")
    error_info: Optional[str] = Field(None, description="Error message if generation required retry or failed")

    model_config = ConfigDict(from_attributes=True)


class OnboardingPlan(BaseModel):
    """Complete personalized multi-stage onboarding plan."""
    plan_id: str = Field(..., description="Unique onboarding plan ID, e.g. PLAN-9001")
    employee_id: str = Field(..., description="Target employee ID or EMP-UNASSIGNED")
    role_id: str = Field(..., description="Target role ID, e.g. ROL-01")
    role_title: str = Field(..., description="Human readable role title")
    department: str = Field(..., description="Department name")
    generated_at: str = Field(..., description="ISO 8601 timestamp")
    version: str = Field(default="1.0", description="Plan version")
    stages: List[str] = Field(
        default_factory=lambda: ["Preboarding", "Day 1", "Week 1", "Week 2", "Month 1", "Month 2+"],
        description="Supported onboarding stages"
    )
    modules: List[LearningModule] = Field(..., description="Modules making up the plan")
    total_modules: int = Field(..., description="Total count of modules")
    total_tasks: int = Field(..., description="Total count of tasks across modules")
    total_quizzes: int = Field(..., description="Total count of quizzes across modules")
    covered_requirement_ids: List[str] = Field(..., description="List of requirement IDs covered by this plan")
    source_citations: List[SourceCitation] = Field(..., description="Aggregated source citations for transparency")
    metadata: GeneratedContentMetadata = Field(..., description="Generation audit metadata")

    model_config = ConfigDict(from_attributes=True)


class RequirementExplanation(BaseModel):
    """Detailed humanized explanation of a policy requirement."""
    requirement_id: str = Field(..., description="Policy requirement ID explained")
    explanation: str = Field(..., description="Clear humanized explanation of why this policy exists and what it means")
    practical_examples: List[str] = Field(..., description="Concrete workplace scenarios/examples")
    compliance_notes: str = Field(..., description="Key compliance guidelines and do's/don'ts")
    target_audience: str = Field(..., description="Intended role/department audience")
    source_citation: SourceCitation = Field(..., description="Source policy document reference")

    model_config = ConfigDict(from_attributes=True)
