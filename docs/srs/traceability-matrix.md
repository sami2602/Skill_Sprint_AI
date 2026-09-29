# SkillSprint AI — Requirements Traceability Matrix

## Overview
This Traceability Matrix maps every requirement extracted from the **SkillSprint AI SRS Version 1.0** to its corresponding architecture module, database tables, API endpoints, frontend UI components, test suite, and deterministic Python validation rules.

---

## 1. Functional Requirements Traceability

| Requirement ID | Module / Package | Database Entity / Tables | API Endpoint(s) | UI Component / View | Test Suite File | Python Validation Rule ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-01** (Authentication) | `security.auth` | `users` | `POST /api/v1/auth/login`<br>`GET /api/v1/auth/me` | `LoginForm.jsx` | `tests/test_auth.py` | `SEC_VAL_01` |
| **FR-02** (RBAC) | `security.rbac` | `users.role` | Auth Middleware Header | `ProtectedContainer.jsx` | `tests/test_rbac.py` | `SEC_VAL_02` |
| **FR-03** (Employee Profile) | `database.employee` | `employees` | `GET/POST/PUT /api/v1/employees` | `EmployeeManagement.jsx` | `tests/test_employee.py` | `EMP_VAL_01` |
| **FR-04** (Role Management) | `role_matrix.role_mgr` | `roles` | `GET/POST /api/v1/roles` | `RoleManagement.jsx` | `tests/test_roles.py` | `ROLE_VAL_01` |
| **FR-05** (Document Upload) | `document_processing.uploader` | `documents` | `POST /api/v1/documents/upload` | `DocumentUploadDropzone.jsx` | `tests/test_upload.py` | `DOC_VAL_01` |
| **FR-06** (Document Validation)| `document_validation.validator`| `documents.validation_status` | `POST /api/v1/documents/validate` | `UploadValidationModal.jsx` | `tests/test_doc_validation.py` | `DOC_VAL_02` |
| **FR-07** (Document Parsing) | `document_processing.parser` | `document_sections` | `POST /api/v1/documents/parse` | `ParsedDocumentViewer.jsx` | `tests/test_parser.py` | `DOC_VAL_03` |
| **FR-08** (Document Chunking) | `document_processing.chunker` | `document_chunks` | Internal Service Call | `ChunkInspectorModal.jsx` | `tests/test_chunker.py` | `DOC_VAL_04` |
| **FR-09** (Metadata Management)| `document_processing.metadata`| `document_chunks` | Internal Service Call | `SourceMetadataBadge.jsx` | `tests/test_metadata.py` | `DOC_VAL_05` |
| **FR-10** (Version Control) | `document_processing.versioning`| `documents.is_active` | `GET /api/v1/documents/versions` | `DocumentVersionHistory.jsx` | `tests/test_versioning.py` | `DOC_VAL_06` |
| **FR-11** (Requirement Extract)| `role_matrix.extractor` | `policy_requirements` | `POST /api/v1/requirements/extract` | `RequirementCatalog.jsx` | `tests/test_requirement_extractor.py` | `REQ_VAL_01` |
| **FR-12** (Role Matrix) | `role_matrix.matrix_builder` | `role_requirement_matrix` | `GET/POST /api/v1/role-matrix` | `RoleRequirementMatrixGrid.jsx` | `tests/test_role_matrix.py` | `REQ_VAL_02` |
| **FR-13** (GenAI API Integration)|`genai_pipeline.client` | `genai_logs` | GenAI Outbound API | N/A (Backend Service) | `tests/test_genai_client.py` | `GEN_VAL_01` |
| **FR-14** (Prompt Templates) | `prompt_templates.manager` | `prompt_templates` | `GET/PUT /api/v1/prompts` | `PromptTemplateEditor.jsx` | `tests/test_prompts.py` | `GEN_VAL_02` |
| **FR-15** (Structured JSON Out)| `genai_pipeline.json_parser` | N/A | GenAI Struct Output | N/A (Backend Service) | `tests/test_genai_json.py` | `GEN_VAL_03` |
| **FR-16** (JSON Schema Val) | `python_validation.schema_val` | `validation_results` | Internal Validation Call | `SchemaErrorBanner.jsx` | `tests/test_schema_validator.py` | `PY_VAL_01` |
| **FR-17** (Personalized Plan) | `genai_pipeline.plan_builder` | `onboarding_plans` | `POST /api/v1/plans/generate` | `OnboardingPlanView.jsx` | `tests/test_plan_generator.py` | `PLAN_VAL_01` |
| **FR-18** (Multi-Stage Plan) | `genai_pipeline.stage_builder`| `plan_stages` | Internal Plan Service | `PlanStageTimeline.jsx` | `tests/test_stages.py` | `PLAN_VAL_02` |
| **FR-19** (Learning Modules) | `genai_pipeline.module_gen` | `learning_modules` | `GET /api/v1/modules/{id}` | `LearningModuleCard.jsx` | `tests/test_modules.py` | `MOD_VAL_01` |
| **FR-20** (Learning Objectives)| `genai_pipeline.module_gen` | `learning_objectives` | Internal Module Service | `LearningObjectiveList.jsx` | `tests/test_objectives.py` | `MOD_VAL_02` |
| **FR-21** (Checklists) | `genai_pipeline.checklist_gen`| `checklists` | `GET /api/v1/checklists/{id}` | `OnboardingChecklistWidget.jsx` | `tests/test_checklists.py` | `CHK_VAL_01` |
| **FR-22** (Task Generation) | `genai_pipeline.task_gen` | `tasks` | `GET /api/v1/tasks/{id}` | `TaskListWidget.jsx` | `tests/test_tasks.py` | `TSK_VAL_01` |
| **FR-23** (Scenario Tasks) | `genai_pipeline.scenario_gen` | `tasks.is_scenario` | Internal Task Service | `ScenarioTaskCard.jsx` | `tests/test_scenarios.py` | `TSK_VAL_02` |
| **FR-24** (Quiz Generation) | `genai_pipeline.quiz_gen` | `quizzes`, `quiz_questions` | `GET /api/v1/quizzes/{id}` | `QuizRunnerWidget.jsx` | `tests/test_quizzes.py` | `QUIZ_VAL_01` |
| **FR-25** (Quiz Validation) | `python_validation.quiz_val` | `quiz_questions` | `POST /api/v1/quizzes/validate` | `QuizFeedbackModal.jsx` | `tests/test_quiz_validation.py` | `QUIZ_VAL_02` |
| **FR-26** (Assessment Gen) | `genai_pipeline.assessment_gen`| `assessments` | `GET /api/v1/assessments` | `AssessmentContainer.jsx` | `tests/test_assessments.py` | `ASM_VAL_01` |
| **FR-27** (Assessment Rubric) | `genai_pipeline.rubric_gen` | `assessment_rubrics` | `GET /api/v1/assessments/{id}/rubric`| `AssessmentRubricTable.jsx` | `tests/test_rubrics.py` | `ASM_VAL_02` |
| **FR-28** (Prerequisites) | `python_validation.sequence` | `module_prerequisites` | `GET /api/v1/modules/prerequisites` | `PrerequisiteDAGGraph.jsx` | `tests/test_prerequisites.py` | `SEQ_VAL_01` |
| **FR-29** (Sequence Val) | `python_validation.sequence` | `validation_results` | `POST /api/v1/validation/sequence` | `SequenceWarningBanner.jsx` | `tests/test_sequence_validation.py` | `SEQ_VAL_02` |
| **FR-30** (Source Citation) | `python_validation.traceability`| `content_citations` | `GET /api/v1/citations/{id}` | `SourceCitationBadge.jsx` | `tests/test_citations.py` | `TRC_VAL_01` |
| **FR-31** (Python Pipeline) | `python_validation.engine` | `validation_runs` | `POST /api/v1/validation/run` | `ValidationSummaryCard.jsx` | `tests/test_python_validation.py` | `PY_VAL_00` |
| **FR-32** (Mandatory Coverage)| `python_validation.coverage` | `validation_results` | `GET /api/v1/validation/coverage` | `CoverageProgressBar.jsx` | `tests/test_coverage.py` | `COV_VAL_01` |
| **FR-33** (Coverage Score) | `python_validation.scoring` | `onboarding_plans.coverage_score`| `GET /api/v1/plans/{id}/score` | `CoverageScoreGauge.jsx` | `tests/test_scoring.py` | `COV_VAL_02` |
| **FR-34** (Traceability Score)| `python_validation.scoring` | `onboarding_plans.traceability_score`|`GET /api/v1/plans/{id}/traceability`| `TraceabilityScoreGauge.jsx` | `tests/test_scoring.py` | `TRC_VAL_02` |
| **FR-35** (Hallucination Detect)|`hallucination_checks.detector`| `hallucination_flags` | `GET /api/v1/validation/hallucinations`|`HallucinationAlertBanner.jsx`| `tests/test_hallucination.py` | `HAL_VAL_01` |
| **FR-36** (Contradiction Detect)|`contradiction_checks.engine` | `contradiction_flags` | `GET /api/v1/validation/contradictions`|`ContradictionAlertPanel.jsx`| `tests/test_contradiction.py` | `CON_VAL_01` |
| **FR-37** (Policy Precedence) | `contradiction_checks.rules` | `policy_precedence_rules` | `GET/PUT /api/v1/precedence-rules` | `PrecedenceConfigView.jsx` | `tests/test_precedence.py` | `CON_VAL_02` |
| **FR-38** (Duplicate Detect) | `python_validation.duplicate` | `duplicate_flags` | `GET /api/v1/validation/duplicates` | `DuplicateHighlightView.jsx` | `tests/test_duplicates.py` | `DUP_VAL_01` |
| **FR-39** (Role Relevance) | `python_validation.role_relevance`| `relevance_flags` | `GET /api/v1/validation/relevance` | `RelevanceBadge.jsx` | `tests/test_role_relevance.py` | `REL_VAL_01` |
| **FR-40** (GenAI Consistency)| `genai_pipeline.consistency` | `consistency_runs` | `POST /api/v1/genai/test-consistency`| `GenAIConsistencyDiffView.jsx`| `tests/test_consistency.py` | `CNS_VAL_01` |
| **FR-41** (Consistency Score) | `python_validation.scoring` | `onboarding_plans.consistency_score`|`GET /api/v1/plans/{id}/consistency` | `ConsistencyScoreBadge.jsx` | `tests/test_scoring.py` | `CNS_VAL_02` |
| **FR-42** (Result Comparison) | `comparison_engine.comparator` | `comparison_results` | `GET /api/v1/comparison/{id}` | `ComparisonMatrixTable.jsx` | `tests/test_comparison_engine.py` | `CMP_VAL_01` |
| **FR-43** (Verification Status)| `comparison_engine.decision` | `onboarding_plans.verification_status`|`GET /api/v1/plans/{id}/status` | `VerificationStatusHeader.jsx` | `tests/test_verification_decision.py`|`CMP_VAL_02` |
| **FR-44** (Manual Review) | `comparison_engine.review_queue`| `manual_review_queue` | `GET/POST /api/v1/review-queue` | `ReviewQueueWorkflow.jsx` | `tests/test_review_queue.py` | `REV_VAL_01` |
| **FR-45** (Reviewer Override) | `security.audit` | `audit_trail` | `POST /api/v1/review-queue/override` | `AuditTrailTimeline.jsx` | `tests/test_audit_trail.py` | `REV_VAL_02` |
| **FR-46** (Employee Dashboard) | `frontend.employee_dash` | N/A | `GET /api/v1/employee/dashboard` | `EmployeeDashboard.jsx` | `tests/test_ui_dashboards.py` | N/A |
| **FR-47** (Admin Dashboard) | `frontend.admin_dash` | N/A | `GET /api/v1/admin/dashboard` | `AdminDashboard.jsx` | `tests/test_ui_dashboards.py` | N/A |
| **FR-48** (Role Dashboard) | `frontend.role_dash` | N/A | `GET /api/v1/roles/dashboard` | `RoleDashboard.jsx` | `tests/test_ui_dashboards.py` | N/A |
| **FR-49** (Progress Tracking) | `database.progress` | `employee_progress` | `GET/POST /api/v1/progress` | `ProgressBarWidget.jsx` | `tests/test_progress.py` | `PRG_VAL_01` |
| **FR-50** (Progress Assessment)| `python_validation.progress_eval`|`employee_progress.status` | `GET /api/v1/progress/assessment` | `ProgressStatusBadge.jsx` | `tests/test_progress_assessment.py`|`PRG_VAL_02` |
| **FR-51** (Weak Area Detect) | `python_validation.analytics` | `learner_weak_areas` | `GET /api/v1/analytics/weak-areas` | `WeakAreasCard.jsx` | `tests/test_weak_areas.py` | `PRG_VAL_03` |
| **FR-52** (Adaptive Recom) | `genai_pipeline.recommendation` | `learning_recommendations` | `GET /api/v1/recommendations/{id}` | `AdaptiveRecommendationsCard.jsx`| `tests/test_recommendations.py` | `REC_VAL_01` |
| **FR-53** (Policy Change Detect)|`document_processing.impact` | `policy_change_impacts` | `POST /api/v1/documents/policy-update`|`PolicyImpactAlert.jsx` | `tests/test_policy_update.py` | `IMP_VAL_01` |
| **FR-54** (Impact Analysis) | `document_processing.impact` | `onboarding_plans.is_outdated` | `GET /api/v1/impact-analysis/{id}` | `ImpactAnalysisTreeView.jsx` | `tests/test_impact_analysis.py` | `IMP_VAL_02` |
| **FR-55** (Selective Regen) | `genai_pipeline.regeneration` | `learning_modules` | `POST /api/v1/plans/regenerate-selective`|`SelectiveRegenerationButton.jsx`| `tests/test_selective_regen.py` | `REGEN_VAL_01`|
| **FR-56** (Plan Comparison) | `frontend.plan_compare` | N/A | `GET /api/v1/plans/compare` | `PlanComparisonTable.jsx` | `tests/test_plan_comparison.py` | N/A |
| **FR-57** (Search and Filter) | `database.search` | Indexes on all entities | `GET /api/v1/search` | `SearchFilterDrawer.jsx` | `tests/test_search.py` | N/A |
| **FR-58** (Reports Generation) | `reports_engine.generator` | N/A | `GET /api/v1/reports/{type}` | `ReportsAnalyticsViewer.jsx` | `tests/test_reports.py` | N/A |
| **FR-59** (Export Reports) | `reports_engine.exporter` | N/A | `GET /api/v1/reports/export` | `ExportButtonDropdown.jsx` | `tests/test_export.py` | N/A |
| **FR-60** (API Error Handling)| `genai_pipeline.retry` | `genai_error_logs` | Outbound Interceptor | `ApiErrorToast.jsx` | `tests/test_retry_manager.py` | `ERR_VAL_01` |
| **FR-61** (Model/Prompt Log) | `genai_pipeline.logger` | `genai_logs` | Internal Logging | `GenAILogViewer.jsx` | `tests/test_genai_logger.py` | `LOG_VAL_01` |
| **FR-62** (Responsive UI) | `frontend` | N/A | All API Endpoints | Responsive Layout Shell | `tests/test_ui_responsive.py` | N/A |

---

## 2. Non-Functional & Security Requirements Traceability

| Requirement ID | Module / Package | Subsystem / Mechanism | Verification / Test Suite File | Acceptance Threshold |
| :--- | :--- | :--- | :--- | :--- |
| **NFR-01** (Performance) | `genai_pipeline`, `python_validation` | Async execution & connection pooling | `tests/test_performance.py` | Plan generation + validation <= 30s |
| **NFR-02** (Scalability) | `database`, `document_processing` | Indexing & paginated queries | `tests/test_scalability.py` | Support 1,000 docs / 1,000 users < 200ms DB latency |
| **NFR-03** (Usability) | `frontend` | User design system & workflow feedback | `tests/test_usability.py` | Zero workflow blocking UX bugs |
| **NFR-04** (Accuracy & Grounding)|`python_validation.coverage` | Ground-truth matrix enforcement | `tests/test_accuracy.py` | 100% mandatory requirement coverage enforced |
| **NFR-05** (Availability) | `infrastructure` | Health check endpoint `/healthz` | `tests/test_availability.py` | 99% uptime target during competition |
| **SEC-01** (Prompt Injection) | `security.prompt_sanitizer` | Delimiter wrapping & system prompt isolation | `tests/test_prompt_injection.py` | Zero document instruction execution |
| **SEC-02** (Adversarial Scanner)| `security.adversarial_detector` | Regex & keyword injection scanner | `tests/test_adversarial_docs.py` | 100% adversarial docs flagged during parsing |
| **SEC-03** (Secure API Keys) | `config` | Environment variables (`.env`) loading | `tests/test_security_config.py` | Zero API keys committed in git repo |
| **SEC-04** (Audit Trail) | `security.audit` | Append-only database table (`audit_trail`) | `tests/test_audit_trail.py` | Override history preserved without mutation |
| **SEC-05** (PII Scrubbing) | `security.pii_scrubber` | Regex PII masking on outbound payloads | `tests/test_pii_scrubber.py` | Zero sensitive PII present in GenAI requests |
