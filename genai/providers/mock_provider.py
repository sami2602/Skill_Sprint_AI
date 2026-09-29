"""
SkillSprint AI — Mock LLM Provider Implementation
Provides deterministic, schema-compliant mock responses for unit tests, offline evaluation, and dry-run execution.
"""

import json
import logging
from typing import Optional, Type, Dict, Any, List
from pydantic import BaseModel
from genai.providers.base_provider import (
    BaseLLMProvider,
    LLMProviderError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMInvalidResponseError,
)

logger = logging.getLogger(__name__)


class MockLLMProvider(BaseLLMProvider):
    """Mock Provider that dynamically creates schema-conforming JSON responses for testing."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash-mock",
        simulate_invalid_json: bool = False,
        simulate_schema_failure: bool = False,
        simulate_timeout: bool = False,
        simulate_rate_limit: bool = False,
    ):
        self._model_name = model
        self.simulate_invalid_json = simulate_invalid_json
        self.simulate_schema_failure = simulate_schema_failure
        self.simulate_timeout = simulate_timeout
        self.simulate_rate_limit = simulate_rate_limit
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "Mock"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        self.call_count += 1

        if self.simulate_timeout:
            raise LLMTimeoutError("Simulated LLM API request timeout.")

        if self.simulate_rate_limit:
            raise LLMRateLimitError("Simulated HTTP 429 Rate Limit Exceeded.")

        if self.simulate_invalid_json:
            return "{ invalid json payload: [ "

        if self.simulate_schema_failure:
            return json.dumps({"incomplete_data": True})

        if not response_schema:
            return json.dumps({"status": "SUCCESS", "message": "Mock generation completed successfully."})

        # Generate schema-compliant mock JSON payload based on schema type
        schema_name = response_schema.__name__
        mock_data = self._generate_mock_payload_for_schema(schema_name, prompt)

        # Validate with Pydantic schema before returning
        try:
            response_schema.model_validate(mock_data)
            return json.dumps(mock_data, indent=2)
        except Exception as val_err:
            raise LLMInvalidResponseError(f"Mock generated invalid schema object: {str(val_err)}")

    def _generate_mock_payload_for_schema(self, schema_name: str, prompt: str) -> Dict[str, Any]:
        """Generates realistic mock data structure matching the schema specification."""
        
        # Try to parse requirement IDs or employee info from prompt if present
        req_id = "REQ-001"
        if "REQ-" in prompt:
            import re
            match = re.search(r"REQ-\d+", prompt)
            if match:
                req_id = match.group(0)

        role_id = "ROL-01"
        if "ROL-" in prompt:
            import re
            match = re.search(r"ROL-\d+", prompt)
            if match:
                role_id = match.group(0)

        emp_id = "EMP-101"
        if "EMP-" in prompt:
            import re
            match = re.search(r"EMP-\d+", prompt)
            if match:
                emp_id = match.group(0)

        source_cite = {
            "doc_id": "DOC-POL-01",
            "doc_version": "1.0",
            "section_id": "SEC-01",
            "page_number": 1,
            "paragraph_ref": "Para 2",
            "requirement_id": req_id
        }

        req_map = {
            "requirement_id": req_id,
            "is_mandatory": True,
            "coverage_type": "DIRECT_TASK",
            "justification": f"Covers mandatory requirement {req_id} via interactive module."
        }

        if schema_name == "RequirementExplanation":
            return {
                "requirement_id": req_id,
                "explanation": f"Requirement {req_id} establishes mandatory compliance protocols for all operations personnel.",
                "practical_examples": [
                    "Completing identity verification prior to accessing client records.",
                    "Filing incident reports within 24 hours of security detection."
                ],
                "compliance_notes": "Failure to follow this requirement results in immediate compliance escalation.",
                "target_audience": "Operations Personnel",
                "source_citation": source_cite
            }

        elif schema_name == "QuizQuestion":
            return {
                "question_id": "QST-101",
                "question_text": f"Under company policy ({req_id}), what is the required timeline for reporting safety incidents?",
                "question_type": "MULTIPLE_CHOICE",
                "options": [
                    {"option_id": "A", "option_text": "Within 24 hours", "is_correct": True, "explanation": "Policy requires reporting within 24 hours."},
                    {"option_id": "B", "option_text": "Within 7 business days", "is_correct": False, "explanation": "Incorrect timeline."},
                    {"option_id": "C", "option_text": "End of month", "is_correct": False, "explanation": "Too late for compliance."},
                    {"option_id": "D", "option_text": "Reporting is optional", "is_correct": False, "explanation": "Direct violation of mandatory policy."}
                ],
                "correct_answer_id": "A",
                "explanation": f"According to policy {req_id}, all safety incidents must be logged within 24 hours.",
                "requirement_id": req_id,
                "source_citation": source_cite
            }

        elif schema_name in ("Quiz", "QuizSchema"):
            return {
                "quiz_id": "QZ-301",
                "title": "Security & Compliance Evaluation Quiz",
                "description": "Verifies understanding of core corporate compliance procedures.",
                "passing_score_percentage": 80.0,
                "questions": [
                    {
                        "question_id": "QST-101",
                        "question_text": f"What is the primary objective of requirement {req_id}?",
                        "question_type": "MULTIPLE_CHOICE",
                        "options": [
                            {"option_id": "A", "option_text": "To ensure mandatory compliance and safety", "is_correct": True, "explanation": "Direct match with policy objective."},
                            {"option_id": "B", "option_text": "To reduce internal documentation", "is_correct": False, "explanation": "Incorrect objective."}
                        ],
                        "correct_answer_id": "A",
                        "explanation": "Policy mandates safety compliance.",
                        "requirement_id": req_id,
                        "source_citation": source_cite
                    }
                ],
                "requirement_ids": [req_id]
            }

        elif schema_name == "OnboardingTask":
            return {
                "task_id": "TSK-101",
                "title": "Complete Mandatory Security Policy Acknowledgment",
                "description": "Read and digitally sign the corporate information security agreement.",
                "due_stage": "Day 1",
                "estimated_minutes": 30,
                "is_mandatory": True,
                "prerequisite_task_ids": [],
                "source_citations": [source_cite],
                "requirement_mappings": [req_map]
            }

        elif schema_name == "LearningModule":
            return {
                "module_id": "MOD-01",
                "title": "Day 1 Fundamentals & Security Orientation",
                "summary": "Core introduction to company policies, data privacy, and workplace security.",
                "learning_objectives": [
                    "Understand core compliance standards",
                    "Complete mandatory Day 1 security sign-offs"
                ],
                "stage": "Day 1",
                "estimated_duration_minutes": 60,
                "prerequisites": [],
                "tasks": [
                    {
                        "task_id": "TSK-101",
                        "title": "Review Security SOP",
                        "description": "Read security guidelines document.",
                        "due_stage": "Day 1",
                        "estimated_minutes": 30,
                        "is_mandatory": True,
                        "prerequisite_task_ids": [],
                        "source_citations": [source_cite],
                        "requirement_mappings": [req_map]
                    }
                ],
                "quizzes": [
                    {
                        "quiz_id": "QZ-301",
                        "title": "Security Basics Quiz",
                        "description": "Check your understanding of basic security rules.",
                        "passing_score_percentage": 80.0,
                        "questions": [
                            {
                                "question_id": "QST-101",
                                "question_text": "What is required before logging into production servers?",
                                "question_type": "MULTIPLE_CHOICE",
                                "options": [
                                    {"option_id": "A", "option_text": "Enable Multi-Factor Authentication", "is_correct": True, "explanation": "MFA is strictly required."},
                                    {"option_id": "B", "option_text": "Disable logging", "is_correct": False, "explanation": "Violates audit policy."}
                                ],
                                "correct_answer_id": "A",
                                "explanation": "MFA is mandatory per security policy.",
                                "requirement_id": req_id,
                                "source_citation": source_cite
                            }
                        ],
                        "requirement_ids": [req_id]
                    }
                ],
                "requirement_mappings": [req_map],
                "source_citations": [source_cite]
            }

        elif schema_name == "OnboardingPlan":
            return {
                "plan_id": f"PLAN-{role_id}-001",
                "employee_id": emp_id,
                "role_id": role_id,
                "role_title": "Software Engineering Specialist",
                "department": "Engineering",
                "generated_at": "2026-09-27T20:00:00Z",
                "version": "1.0",
                "stages": ["Preboarding", "Day 1", "Week 1", "Week 2", "Month 1", "Month 2+"],
                "modules": [
                    {
                        "module_id": "MOD-01",
                        "title": "Day 1 Security & System Access",
                        "summary": "Immediate onboarding requirements for account provisioning and policy acknowledgment.",
                        "learning_objectives": ["Set up corporate credentials", "Acknowledge IT security policy"],
                        "stage": "Day 1",
                        "estimated_duration_minutes": 60,
                        "prerequisites": [],
                        "tasks": [
                            {
                                "task_id": "TSK-101",
                                "title": "Setup Multi-Factor Authentication",
                                "description": "Configure authenticator app for company single sign-on.",
                                "due_stage": "Day 1",
                                "estimated_minutes": 20,
                                "is_mandatory": True,
                                "prerequisite_task_ids": [],
                                "source_citations": [source_cite],
                                "requirement_mappings": [req_map]
                            }
                        ],
                        "quizzes": [],
                        "requirement_mappings": [req_map],
                        "source_citations": [source_cite]
                    },
                    {
                        "module_id": "MOD-02",
                        "title": "Week 1 Core Operational Training",
                        "summary": "Deep dive into role-specific workflows and compliance guidelines.",
                        "learning_objectives": ["Master standard operating procedures"],
                        "stage": "Week 1",
                        "estimated_duration_minutes": 120,
                        "prerequisites": ["MOD-01"],
                        "tasks": [
                            {
                                "task_id": "TSK-102",
                                "title": "Complete Code Review Standard Training",
                                "description": "Review repository branch rules and PR guidelines.",
                                "due_stage": "Week 1",
                                "estimated_minutes": 45,
                                "is_mandatory": True,
                                "prerequisite_task_ids": ["TSK-101"],
                                "source_citations": [source_cite],
                                "requirement_mappings": [req_map]
                            }
                        ],
                        "quizzes": [
                            {
                                "quiz_id": "QZ-301",
                                "title": "Engineering Standards Quiz",
                                "description": "Evaluate understanding of code review requirements.",
                                "passing_score_percentage": 80.0,
                                "questions": [
                                    {
                                        "question_id": "QST-101",
                                        "question_text": "How many approvals are required before merging a PR?",
                                        "question_type": "MULTIPLE_CHOICE",
                                        "options": [
                                            {"option_id": "A", "option_text": "Two peer reviews", "is_correct": True, "explanation": "Policy requires 2 peer reviews."},
                                            {"option_id": "B", "option_text": "Zero reviews", "is_correct": False, "explanation": "Not allowed."}
                                        ],
                                        "correct_answer_id": "A",
                                        "explanation": "Minimum 2 approvals required.",
                                        "requirement_id": req_id,
                                        "source_citation": source_cite
                                    }
                                ],
                                "requirement_ids": [req_id]
                            }
                        ],
                        "requirement_mappings": [req_map],
                        "source_citations": [source_cite]
                    }
                ],
                "total_modules": 2,
                "total_tasks": 2,
                "total_quizzes": 1,
                "covered_requirement_ids": [req_id],
                "source_citations": [source_cite],
                "metadata": {
                    "prompt_version": "v1.0",
                    "provider": "Mock",
                    "model": self._model_name,
                    "generation_timestamp": "2026-09-27T20:00:00Z",
                    "input_requirement_ids": [req_id],
                    "source_versions": {"DOC-POL-01": "1.0"},
                    "output_schema_version": "1.0",
                    "generation_status": "SUCCESS",
                    "error_info": None
                }
            }

        # Fallback dictionary for arbitrary models
        return {
            "status": "SUCCESS",
            "requirement_id": req_id,
            "role_id": role_id,
            "message": f"Mock data for schema {schema_name}"
        }
