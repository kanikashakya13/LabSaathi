export type ClassificationStatus =
  | 'Within Reference Range'
  | 'Below Reference Range'
  | 'Above Reference Range'
  | 'Unable to Classify';

export type VerificationStatus =
  | 'Verified'
  | 'Needs Review'
  | 'Unable to verify'
  | 'User Corrected';

export interface QualityMetrics {
  laplacian_variance: number;
  tenengrad_score: number;
  brightness_mean: number;
  contrast_std: number;
  glare_ratio: number;
  skew_degrees: number;
  width: number;
  height: number;
  edge_cut_ratio: number;
  text_density_score: number;
}

export interface QualityCheckResult {
  accepted: boolean;
  error_banner: string | null;
  issues: string[];
  issue_codes: string[];
  actions: string[];
  metrics: QualityMetrics | null;
}

export interface PageValidationResult {
  page_number: number;
  extraction_method: 'embedded_text' | 'scanned_ocr' | 'unreadable';
  accepted: boolean;
  issues: string[];
  quality: QualityCheckResult | null;
  character_count: number;
}

export interface ExtractedParameter {
  id: string;
  test_name: string;
  original_result: string;
  unit: string;
  reference_range: string;
  lab_interpretation: string;
  confidence: number;
  verification_status: VerificationStatus;
  rule_based_status: ClassificationStatus;
  classification_reason: string;
  ocr_warnings: string[];
  original_extracted_text: string;
  original_extracted_result: string;
  original_extracted_unit: string;
  original_extracted_range: string;
  user_edited: boolean;
  user_confirmed: boolean;
  page_number: number;
}

export interface ExtractionCounts {
  total_extracted: number;
  verified_count: number;
  flagged_count: number;
  unprocessed_count: number;
}

export interface UploadAndExtractResponse {
  session_id: string;
  file_name: string;
  file_type: string;
  file_size_bytes: number;
  is_sample: boolean;
  sample_label: string | null;
  quality_passed: boolean;
  quality_result: QualityCheckResult;
  pdf_pages: PageValidationResult[];
  ocr_engine_used: string;
  ocr_service_notice: string | null;
  extracted_patient_age: string | null;
  extracted_patient_sex: string | null;
  extracted_report_date: string | null;
  requires_demographic_input: boolean;
  demographic_prompt_reason: string | null;
  extraction_counts: ExtractionCounts;
  critical_value_alerts: string[];
  multi_patient_warning: string | null;
  unsupported_format_notice: string | null;
  parameters: ExtractedParameter[];
  requires_user_confirmation: boolean;
  temp_file_deleted: boolean;
  disclaimer: string;
}

export interface ParameterExplanationCard {
  id: string;
  test_name: string;
  original_result: string;
  unit: string;
  reference_range: string;
  lab_interpretation: string;
  rule_based_status: ClassificationStatus;
  classification_reason: string;
  what_it_measures_en: string;
  what_it_measures_hi: string;
  result_context_en: string;
  result_context_hi: string;
  factors_affecting_en: string[];
  factors_affecting_hi: string[];
  doctor_question_en: string;
  doctor_question_hi: string;
  source_attribution: string;
  original_extracted_result: string;
  original_extracted_unit: string;
  original_extracted_range: string;
  user_edited: boolean;
  is_critical_alert: boolean;
  page_number: number;
}

export interface SummaryCounts {
  total_verified: number;
  within_range: number;
  below_range: number;
  above_range: number;
  unable_to_classify: number;
}

export interface ReportExplanationResponse {
  session_id: string;
  is_sample: boolean;
  sample_label: string | null;
  extracted_patient_age: string | null;
  extracted_patient_sex: string | null;
  extracted_report_date: string | null;
  summary_counts: SummaryCounts;
  ai_mode: 'live_gemini' | 'curated_medical_kb';
  ai_service_notice: string;
  urgent_care_banner: string | null;
  critical_value_alerts: string[];
  cards: ParameterExplanationCard[];
  general_doctor_questions_en: string[];
  general_doctor_questions_hi: string[];
  range_education_note_en: string;
  range_education_note_hi: string;
  limitations: string[];
  disclaimer: string;
  temp_files_cleaned: boolean;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  tagline: string;
  version: string;
  services: {
    ai_explanation_service: {
      configured: boolean;
      provider: string;
      model: string;
      credential_env_var: string;
      fallback_mode: string;
      setup_message: string;
    };
    ocr_service: {
      tesseract_detected: boolean;
      windows_native_ocr?: boolean;
      pdf_embedded_text_engine: string;
      credential_or_binary_env_var: string;
      setup_message: string;
    };
    image_quality_cv: {
      engine: string;
      thresholds: Record<string, number>;
    };
  };
  upload_limits: {
    max_file_size_mb: number;
    max_pdf_pages: number;
    supported_formats: string[];
    required_upload_warning: string;
  };
  privacy_policy: {
    default_retention_seconds: number;
    stores_reports_on_disk: boolean;
    logs_medical_values: boolean;
    llm_zero_retention_store_false: boolean;
  };
  disclaimer: string;
}

export interface SampleScenario {
  id: string;
  title: string;
  filename: string;
  description: string;
  expected_outcome: string;
}
