export type UserRole = 'ADMIN' | 'REVIEWER' | 'MANAGER' | 'EMPLOYEE' | 'TRAINING_MANAGER';

export interface User {
  id: number | string;
  user_id?: string;
  username?: string;
  email: string;
  full_name?: string;
  name?: string;
  role: UserRole;
  department?: string;
  employee_id?: string;
  is_active: boolean;
  created_at?: string;
}

export interface DocumentMeta {
  id: string;
  filename: string;
  file_path: string;
  file_type: 'PDF' | 'DOCX';
  file_size_bytes: number;
  version: string;
  effective_date: string;
  is_active: boolean;
  sections_count: number;
  chunks_count: number;
  uploaded_by?: string;
  created_at: string;
}

export interface DocumentSection {
  id: string;
  document_id: string;
  section_id: string;
  title: string;
  content: string;
  page_number?: number;
  paragraph_ref?: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_id: string;
  content: string;
  section_id: string;
  tokens_count?: number;
}

export interface RequirementItem {
  id: string;
  requirement_id: string;
  title: string;
  description: string;
  category: string;
  is_mandatory: boolean;
  target_roles: string[];
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  due_stage: string;
  assessment_type: string;
  source_document_id: string;
  source_section_id: string;
  page_number?: number;
  paragraph_ref?: string;
  version: string;
  is_conflicting?: boolean;
  conflict_notes?: string;
}

export interface RoleMatrixItem {
  mapping_id: string;
  requirement_id: string;
  title: string;
  requirement_text?: string;
  category: string;
  priority: string;
  is_mandatory: boolean;
  due_stage: string;
  doc_id?: string;
  section_ref?: string;
}

export interface RoleItem {
  id: string;
  role_id: string;
  title: string;
  department: string;
  description: string;
  required_skills: string[];
  mandatory_requirements_count: number;
  total_requirements_count: number;
  coverage_percentage: number;
  requirement_matrix?: RoleMatrixItem[];
}

export interface EmployeeItem {
  id: string;
  employee_id: string;
  name: string;
  email: string;
  role_id: string;
  role_title: string;
  department: string;
  experience_level: 'Junior' | 'Mid' | 'Senior';
  onboarding_status: 'NOT_STARTED' | 'IN_PROGRESS' | 'VERIFIED' | 'ACTION_NEEDED' | 'COMPLETED';
  progress_percentage: number;
  current_stage: string;
  plan_id?: string;
  assigned_reviewer?: string;
}

export interface PlanTask {
  task_id: string;
  title: string;
  description: string;
  estimated_minutes: number;
  is_mandatory: boolean;
  source_document_id: string;
  source_section_id: string;
  page_number?: number;
  paragraph_ref?: string;
  completed: boolean;
}

export interface QuizQuestion {
  question_id: string;
  question_text: string;
  options: string[];
  correct_option_index: number;
  explanation: string;
  source_document_id: string;
  source_section_id: string;
  user_selected_index?: number;
}

export interface PlanModule {
  module_id: string;
  title: string;
  description: string;
  stage: 'Day 1' | 'Week 1' | 'Week 2' | '30 Days' | '60 Days' | '90 Days';
  learning_objectives: string[];
  tasks: PlanTask[];
  quiz?: QuizQuestion[];
  source_document_id: string;
  source_section_id: string;
  page_number?: number;
  paragraph_ref?: string;
  is_completed?: boolean;
}

export interface OnboardingPlan {
  plan_id: string;
  employee_id: string;
  role_id: string;
  experience_level: string;
  total_modules: number;
  total_tasks: number;
  modules: PlanModule[];
  created_at: string;
  status: 'GENERATED' | 'VALIDATING' | 'VERIFIED' | 'NEEDS_REVIEW' | 'REJECTED';
}

export type VerificationStatus =
  | 'VERIFIED'
  | 'VERIFIED_WITH_WARNING'
  | 'INCOMPLETE'
  | 'UNSUPPORTED'
  | 'CONTRADICTORY'
  | 'MANUAL_REVIEW_REQUIRED';

export interface GroundTruthEvidence {
  requirement_id: string;
  title: string;
  is_mandatory: boolean;
  covered_in_plan: boolean;
  matching_module_id?: string;
  matching_task_id?: string;
  source_document_id: string;
  source_section_id: string;
  evidence_text: string;
  validation_status: 'GROUNDED' | 'MISSING' | 'UNSUPPORTED' | 'CONTRADICTORY';
}

export interface ValidationRun {
  run_id: string;
  plan_id: string;
  coverage_score: number;
  traceability_score: number;
  missing_mandatory_count: number;
  unsupported_items_count: number;
  contradictions_count: number;
  outdated_sources_count: number;
  verification_status: VerificationStatus;
  evidences: GroundTruthEvidence[];
  validated_at: string;
}

export interface RequirementComparison {
  requirement_id: string;
  requirement_title: string;
  category: string;
  is_mandatory: boolean;
  expected_source: string;
  generated_module?: string;
  generated_task?: string;
  python_validation_status: 'GROUNDED' | 'MISSING' | 'UNSUPPORTED' | 'CONTRADICTORY';
  evidence_quote?: string;
  mismatch_reason?: string;
}

export interface ReviewQueueItem {
  id: string;
  plan_id: string;
  employee_name: string;
  role_title: string;
  flagged_reason: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'REVISED';
  requirement_id: string;
  requirement_title: string;
  generated_content: string;
  validation_evidence: string;
  reviewer_comments?: string;
  override_used?: boolean;
  override_reason?: string;
  created_at: string;
}

export interface PolicyImpactItem {
  document_id: string;
  filename: string;
  old_version: string;
  new_version: string;
  effective_date: string;
  affected_requirements_count: number;
  affected_roles: string[];
  affected_employees_count: number;
  affected_plans_count: number;
  changes_summary: string[];
}

export interface SystemAnalytics {
  total_documents?: number;
  document_count?: number;
  total_requirements?: number;
  requirement_count?: number;
  total_roles?: number;
  role_count?: number;
  total_employees?: number;
  employee_count?: number;
  total_plans?: number;
  total_plans_generated?: number;
  plan_count?: number;
  average_coverage_score?: number;
  avg_coverage_score?: number;
  verification_rate_percentage?: number;
  average_traceability_score?: number;
  avg_traceability_score?: number;
  pending_reviews_count: number;
  verification_status_counts?: Record<string, number>;
  verification_status_distribution?: Record<string, number>;
  role_coverage_scores?: { role_title: string; coverage: number }[];
  weak_compliance_areas?: { category: string; missing_count: number }[];
}

export interface ReportSummary {
  report_type: 'VALIDATION' | 'COMPARISON' | 'SECURITY' | 'ONBOARDING';
  title: string;
  generated_at: string;
  summary_metrics: Record<string, any>;
  data: any[];
}
