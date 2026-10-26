"""Pydantic schemas for LabSaathi API requests and responses."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


REQUIRED_UPLOAD_WARNING = (
    "IMPORTANT: Please upload a clear and readable lab report. Ensure all test names, "
    "values, units, and reference ranges are visible. Blurry or unreadable images will "
    "not be accepted. Please click the photo again clearly."
)

REQUIRED_BLUR_ERROR_MESSAGE = (
    "IMAGE IS BLURRY OR UNREADABLE. We couldn't clearly read your lab report. Please "
    "retake the photo in good lighting, keep your phone steady, and click again clearly."
)

REQUIRED_MEDICAL_DISCLAIMER = (
    "LabSaathi provides educational explanations and is not a substitute for professional "
    "medical advice, diagnosis, or treatment."
)

ClassificationStatus = Literal[
    "Within Reference Range",
    "Below Reference Range",
    "Above Reference Range",
    "Unable to Classify",
]

VerificationStatus = Literal[
    "Verified",
    "Needs Review",
    "Unable to verify",
    "User Corrected",
]


class QualityMetrics(BaseModel):
    laplacian_variance: float = Field(..., description="Variance of Laplacian sharpness metric")
    tenengrad_score: float = Field(..., description="Sobel gradient magnitude energy")
    brightness_mean: float = Field(..., description="Mean grayscale intensity (0-255)")
    contrast_std: float = Field(..., description="Standard deviation of grayscale intensity")
    glare_ratio: float = Field(..., description="Fraction of image pixels saturated (>248)")
    skew_degrees: float = Field(..., description="Estimated document skew angle in degrees")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    edge_cut_ratio: float = Field(..., description="Ratio of border ink indicating cropped/cut-off content")
    text_density_score: float = Field(..., description="Estimated density of text-like morphological regions")


class QualityCheckResult(BaseModel):
    accepted: bool
    error_banner: str | None = None
    issues: list[str] = Field(default_factory=list)
    issue_codes: list[str] = Field(default_factory=list)
    actions: list[str] = Field(
        default_factory=lambda: ["Retake Photo", "Upload Again", "Choose Another File"]
    )
    metrics: QualityMetrics | None = None


class PageValidationResult(BaseModel):
    page_number: int
    extraction_method: Literal["embedded_text", "scanned_ocr", "unreadable"]
    accepted: bool
    issues: list[str] = Field(default_factory=list)
    quality: QualityCheckResult | None = None
    character_count: int = 0


class ExtractedParameter(BaseModel):
    id: str
    test_name: str
    original_result: str
    unit: str = ""
    reference_range: str = ""
    lab_interpretation: str = ""
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    verification_status: VerificationStatus = "Verified"
    rule_based_status: ClassificationStatus = "Unable to Classify"
    classification_reason: str = ""
    ocr_warnings: list[str] = Field(default_factory=list)
    original_extracted_text: str = ""
    original_extracted_result: str = ""
    original_extracted_unit: str = ""
    original_extracted_range: str = ""
    user_edited: bool = False
    user_confirmed: bool = True
    page_number: int = 1


class ExtractionCounts(BaseModel):
    extracted: int = 0
    total_extracted: int = 0
    verified: int = 0
    verified_count: int = 0
    flagged: int = 0
    flagged_count: int = 0
    unprocessed: int = 0
    unprocessed_count: int = 0


class UploadAndExtractResponse(BaseModel):
    session_id: str
    file_name: str
    file_type: str
    file_size_bytes: int
    is_sample: bool = False
    sample_label: str | None = None
    quality_passed: bool
    quality_result: QualityCheckResult
    pdf_pages: list[PageValidationResult] = Field(default_factory=list)
    ocr_engine_used: str = "none"
    ocr_service_notice: str | None = None
    extracted_patient_age: str | None = None
    extracted_patient_sex: Literal["unspecified", "female", "male"] | None = "unspecified"
    extracted_report_date: str | None = None
    requires_demographic_input: bool = False
    demographic_prompt_reason: str | None = None
    extraction_counts: ExtractionCounts = Field(default_factory=ExtractionCounts)
    critical_value_alerts: list[str] = Field(default_factory=list)
    multi_patient_warning: str | None = None
    unsupported_format_notice: str | None = None
    parameters: list[ExtractedParameter] = Field(default_factory=list)
    requires_user_confirmation: bool = False
    temp_file_deleted: bool = True
    disclaimer: str = REQUIRED_MEDICAL_DISCLAIMER


class VerifyAndExplainRequest(BaseModel):
    session_id: str = "session-1"
    is_sample: bool = False
    sample_label: str | None = None
    patient_age: str | None = None
    patient_sex: Literal["unspecified", "female", "male"] = "unspecified"
    patient_age_group: Literal["unspecified", "adult", "child", "senior"] = "unspecified"
    report_date: str | None = None
    critical_value_alerts: list[str] = Field(default_factory=list)
    user_consented_ai_processing: bool = True
    urgent_symptoms_reported: bool = False
    parameters: list[ExtractedParameter]


class ClassifiedParameter(BaseModel):
    id: str
    test_name: str
    original_result: str
    unit: str
    reference_range: str
    lab_interpretation: str = ""
    rule_based_status: ClassificationStatus
    classification_reason: str
    parsed_numeric_value: float | None = None
    parsed_range_low: float | None = None
    parsed_range_high: float | None = None
    original_extracted_result: str = ""
    user_edited: bool = False
    is_critical_alert: bool = False
    page_number: int = 1


class ParameterExplanationCard(BaseModel):
    id: str
    test_name: str
    original_result: str
    unit: str
    reference_range: str
    lab_interpretation: str = ""
    rule_based_status: ClassificationStatus
    classification_reason: str
    what_it_measures_en: str
    what_it_measures_hi: str
    result_context_en: str
    result_context_hi: str
    factors_affecting_en: list[str]
    factors_affecting_hi: list[str]
    doctor_question_en: str
    doctor_question_hi: str
    source_attribution: str
    original_extracted_result: str = ""
    original_extracted_unit: str = ""
    original_extracted_range: str = ""
    user_edited: bool = False
    is_critical_alert: bool = False
    page_number: int = 1


class SummaryCounts(BaseModel):
    total_verified: int
    within_range: int
    below_range: int
    above_range: int
    unable_to_classify: int


class ReportExplanationResponse(BaseModel):
    session_id: str
    is_sample: bool = False
    sample_label: str | None = None
    patient_age: str | None = None
    patient_sex: str = "unspecified"
    report_date: str | None = None
    summary_counts: SummaryCounts
    ai_mode: Literal["live_gemini", "curated_medical_kb"]
    ai_service_notice: str
    urgent_care_banner: str | None = None
    critical_value_alerts: list[str] = Field(default_factory=list)
    cards: list[ParameterExplanationCard]
    general_doctor_questions_en: list[str]
    general_doctor_questions_hi: list[str]
    range_education_note_en: str = (
        "An out-of-range result does not automatically mean a disease is present, and an "
        "in-range result does not guarantee complete health. Laboratory reference ranges "
        "represent typical values seen in roughly 95% of a healthy reference population."
    )
    range_education_note_hi: str = (
        "Reference range se bahar value aane ka matlab hamesha koi bimari nahi hota, aur "
        "range ke andar value aane ka matlab poori tarah swasth hona guarantee nahi karta. "
        "Har vyakti ki health history ke hisaab se doctor hi sahi matlab bata sakte hain."
    )
    limitations: list[str]
    disclaimer: str = REQUIRED_MEDICAL_DISCLAIMER
    temp_files_cleaned: bool = True
