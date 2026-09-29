# SkillSprint AI — GenAI Generation Pipeline API Specification

## Overview
The GenAI Generation Pipeline (`genai/`) produces structured, multi-stage, personalized onboarding plans, learning modules, tasks, quizzes, and requirement explanations derived from the database-backed Role Requirement Matrix.

---

## Key Interfaces & Components

### 1. Provider Abstraction Interface (`genai.providers`)
- `BaseLLMProvider`: Abstract base class defining `generate(prompt, response_schema, temperature)`.
- `GeminiProvider`: Production provider for **Gemini 2.5 Flash** using `google-genai` SDK.
- `MockLLMProvider`: Offline/testing provider with deterministic, schema-compliant outputs.
- `get_llm_provider(provider_name)`: Factory resolving provider based on `GENAI_PROVIDER` and `GEMINI_API_KEY`.

### 2. Pydantic Output Schemas (`genai.schemas`)
- `SourceCitation`: Provenance tracking (`doc_id`, `doc_version`, `section_id`, `page_number`, `paragraph_ref`, `requirement_id`).
- `RequirementMapping`: Maps content to requirement matrix (`requirement_id`, `is_mandatory`, `coverage_type`, `justification`).
- `OnboardingTask`: Individual action item with stage, duration, citations, and requirement mappings.
- `QuizOption`: Choice option with ground-truth correctness flag and explanation.
- `QuizQuestion`: Question object linked to target requirement ID and source citation.
- `Quiz`: Assessment module containing questions and passing score threshold.
- `LearningModule`: Sequential module containing tasks and quizzes.
- `OnboardingPlan`: Complete multi-stage plan (`Preboarding`, `Day 1`, `Week 1`, `Week 2`, `Month 1`, `Month 2+`).
- `RequirementExplanation`: Humanized workplace explanation with practical examples and compliance notes.
- `GeneratedContentMetadata`: Generation metadata (`prompt_version`, `provider`, `model`, `input_requirement_ids`, `source_versions`, `status`).

### 3. Versioned Prompt Engine (`genai.prompts`)
- Versioned Jinja2 prompt templates (`onboarding_plan.jinja2`, `learning_module.jinja2`, `task_generation.jinja2`, `quiz_generation.jinja2`, `distractor_generation.jinja2`, `personalization.jinja2`, `requirement_explanation.jinja2`).
- Security framing: Treats document text as data inside `<untrusted_document_data>` XML tags.

### 4. Bounded Retry & Execution Handler (`genai.utils`)
- `RetryHandler`: Executes model calls with exponential backoff (max 3 retries). Handles JSON parsing errors, schema validation failures, timeouts, and rate limits without fabricating fake data.

### 5. Security & Injection Defense (`genai.security`)
- `PromptInjectionDefender`: Pre-scans input text using `AdversarialScanner` and enforces untrusted data boundary framing.
