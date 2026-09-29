"""
SkillSprint AI — Unit Tests for GenAI Pydantic Schemas
"""

import pytest
from pydantic import ValidationError
from genai.schemas.generation_schemas import (
    SourceCitation,
    RequirementMapping,
    OnboardingTask,
    QuizOption,
    QuizQuestion,
    Quiz,
    LearningModule,
    OnboardingPlan,
    GeneratedContentMetadata,
    RequirementExplanation,
)


def test_source_citation_schema_valid():
    cite = SourceCitation(
        doc_id="DOC-POL-01",
        doc_version="1.0",
        section_id="SEC-02",
        page_number=3,
        paragraph_ref="Para 4.2",
        requirement_id="REQ-001"
    )
    assert cite.doc_id == "DOC-POL-01"
    assert cite.requirement_id == "REQ-001"


def test_source_citation_missing_required_field():
    with pytest.raises(ValidationError):
        # Missing doc_id
        SourceCitation(
            section_id="SEC-02",
            requirement_id="REQ-001"
        )


def test_quiz_question_schema_validation():
    opt1 = QuizOption(option_id="A", option_text="Answer A", is_correct=True, explanation="Correct")
    opt2 = QuizOption(option_id="B", option_text="Answer B", is_correct=False, explanation="Incorrect")
    cite = SourceCitation(doc_id="DOC-POL-01", section_id="SEC-01", requirement_id="REQ-001")

    question = QuizQuestion(
        question_id="QST-101",
        question_text="What is safety policy?",
        question_type="MULTIPLE_CHOICE",
        options=[opt1, opt2],
        correct_answer_id="A",
        explanation="Safety is priority.",
        requirement_id="REQ-001",
        source_citation=cite,
    )
    assert question.question_id == "QST-101"
    assert len(question.options) == 2


def test_onboarding_plan_schema_validation():
    cite = SourceCitation(doc_id="DOC-POL-01", section_id="SEC-01", requirement_id="REQ-001")
    req_map = RequirementMapping(requirement_id="REQ-001", is_mandatory=True, justification="Direct task")

    task = OnboardingTask(
        task_id="TSK-01",
        title="Setup MFA",
        description="Configure MFA",
        due_stage="Day 1",
        estimated_minutes=15,
        is_mandatory=True,
        source_citations=[cite],
        requirement_mappings=[req_map]
    )

    module = LearningModule(
        module_id="MOD-01",
        title="Day 1 Orientation",
        summary="Orientation module",
        learning_objectives=["Complete setup"],
        stage="Day 1",
        tasks=[task],
        quizzes=[],
        requirement_mappings=[req_map],
        source_citations=[cite]
    )

    metadata = GeneratedContentMetadata(
        prompt_version="v1",
        provider="Mock",
        model="mock-model",
        generation_timestamp="2026-09-27T20:00:00Z",
        input_requirement_ids=["REQ-001"],
        source_versions={"DOC-POL-01": "1.0"},
        output_schema_version="1.0",
        generation_status="SUCCESS"
    )

    plan = OnboardingPlan(
        plan_id="PLAN-001",
        employee_id="EMP-101",
        role_id="ROL-01",
        role_title="Engineer",
        department="Engineering",
        generated_at="2026-09-27T20:00:00Z",
        modules=[module],
        total_modules=1,
        total_tasks=1,
        total_quizzes=0,
        covered_requirement_ids=["REQ-001"],
        source_citations=[cite],
        metadata=metadata
    )

    assert plan.plan_id == "PLAN-001"
    assert len(plan.stages) == 6
    assert "Preboarding" in plan.stages
    assert "Day 1" in plan.stages
