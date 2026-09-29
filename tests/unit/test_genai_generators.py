"""
SkillSprint AI — Unit Tests for Generators (Plan, Quiz, Explanation)
"""

import pytest
from genai.providers.mock_provider import MockLLMProvider
from genai.generators.quiz_generator import QuizGenerator
from genai.generators.explanation_generator import RequirementExplanationGenerator
from genai.schemas.generation_schemas import Quiz, RequirementExplanation


def test_quiz_generator_creation():
    provider = MockLLMProvider()
    generator = QuizGenerator(provider=provider)

    reqs = [
        {
            "requirement_id": "REQ-001",
            "title": "MFA Security Requirement",
            "source_doc_id": "DOC-POL-01",
            "source_version": "1.0",
            "source_section_ref": "SEC-01",
            "requirement_text": "MFA is required for all server logins."
        }
    ]

    quiz = generator.generate_quiz_for_requirements(reqs, quiz_title="Security Assessment")
    assert isinstance(quiz, Quiz)
    assert len(quiz.questions) > 0
    assert quiz.questions[0].requirement_id == "REQ-001"
    assert quiz.questions[0].source_citation.doc_id == "DOC-POL-01"


def test_explanation_generator_creation():
    provider = MockLLMProvider()
    generator = RequirementExplanationGenerator(provider=provider)

    req = {
        "requirement_id": "REQ-002",
        "title": "Data Encryption at Rest",
        "source_doc_id": "DOC-POL-02",
        "source_version": "1.0",
        "source_section_ref": "SEC-03",
        "requirement_text": "All customer databases must be encrypted using AES-256."
    }

    explanation = generator.generate_explanation(req)
    assert isinstance(explanation, RequirementExplanation)
    assert explanation.requirement_id == "REQ-002"
    assert explanation.source_citation.doc_id == "DOC-POL-02"
    assert len(explanation.practical_examples) > 0
