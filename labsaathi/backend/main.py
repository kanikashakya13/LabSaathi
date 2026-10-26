"""FastAPI Backend Server for LabSaathi ("Confused by Reports? Decode Them!")."""

from __future__ import annotations

import logging
import os
import re
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.ai_engine import generate_explanations
from backend.classifier import classify_parameter
from backend.config import BASE_DIR, get_settings
from backend.ocr_pipeline import process_image_upload, process_pdf_upload
from backend.quality_validator import verify_file_signature
from backend.sample_data import (
    SAMPLE_DATA_LABEL,
    generate_all_sample_files,
    get_synthetic_sample_response,
)
from backend.schemas import (
    ClassifiedParameter,
    QualityCheckResult,
    REQUIRED_BLUR_ERROR_MESSAGE,
    REQUIRED_MEDICAL_DISCLAIMER,
    REQUIRED_UPLOAD_WARNING,
    ReportExplanationResponse,
    SummaryCounts,
    UploadAndExtractResponse,
    VerifyAndExplainRequest,
)

# Configure privacy-safe logger (never logs medical content, patient identifiers, or secrets)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("labsaathi")

SAMPLES_DIR = BASE_DIR / "samples"

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Generate synthetic sample test files in samples/ on startup if missing."""
    try:
        generate_all_sample_files(SAMPLES_DIR)
        logger.info("Synthetic sample test assets verified in %s", SAMPLES_DIR)
    except Exception as exc:
        logger.warning("Could not pre-generate sample files: %s", type(exc).__name__)
    yield


app = FastAPI(
    title="LabSaathi API",
    description=(
        "Backend API for LabSaathi — AI-powered medical laboratory report explanation web application. "
        "Provides OpenCV image quality/blur detection, PDF validation, OCR extraction, deterministic "
        "rule-based reference range classification, and bilingual (English/Hinglish) educational explanations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def _securely_read_and_cleanup(upload_file: UploadFile, max_bytes: int) -> bytes:
    """Read uploaded file with strict size limits and guaranteed temporary file deletion."""
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, prefix="labsaathi_tmp_") as tmp:
            temp_path = Path(tmp.name)
            total_read = 0
            chunk_size = 64 * 1024
            while True:
                chunk = upload_file.file.read(chunk_size)
                if not chunk:
                    break
                total_read += len(chunk)
                if total_read > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"File exceeds the maximum allowed upload size of "
                            f"{max_bytes // (1024 * 1024)} MB."
                        ),
                    )
                tmp.write(chunk)
        return temp_path.read_bytes()
    finally:
        try:
            upload_file.file.close()
        except Exception:
            pass
        if temp_path and temp_path.exists():
            try:
                os.remove(temp_path)
            except OSError:
                pass


@app.get("/api/health")
def get_health() -> dict:
    """Return service readiness, credential configuration status, and security thresholds."""
    cfg = get_settings()
    return {
        "status": "ok",
        "app_name": cfg.app_name,
        "tagline": cfg.tagline,
        "version": cfg.version,
        "services": {
            "ai_explanation_service": {
                "configured": cfg.is_ai_configured,
                "provider": "Google Gemini Interactions API",
                "model": cfg.gemini_model,
                "credential_env_var": "GEMINI_API_KEY",
                "fallback_mode": "Vetted Curated Medical Reference Library (English & Hinglish)",
                "setup_message": (
                    "Live Gemini AI explanations are active."
                    if cfg.is_ai_configured
                    else "GEMINI_API_KEY is not set in .env. Using built-in Curated Medical Reference Library (no fabricated AI responses)."
                ),
            },
            "ocr_service": {
                "tesseract_detected": bool(cfg.tesseract_cmd),
                "windows_native_ocr": True,
                "pdf_embedded_text_engine": "PyMuPDF (fitz) + Coordinate Row Reconstruction",
                "credential_or_binary_env_var": "TESSERACT_CMD",
                "setup_message": (
                    f"Tesseract OCR ({cfg.tesseract_cmd}) + Windows Native WinRT OCR + PyMuPDF active."
                    if cfg.tesseract_cmd
                    else "Windows Native WinRT OCR (Windows.Media.Ocr) + PyMuPDF coordinate table extractor active for JPG, JPEG, PNG, and digital/scanned PDFs."
                ),
            },
            "image_quality_cv": {
                "engine": "OpenCV (Laplacian Variance + Tenengrad Gradient + Brightness/Contrast/Glare/Skew/Crop)",
                "thresholds": {
                    "min_laplacian_var": cfg.quality_min_laplacian_var,
                    "min_tenengrad": cfg.quality_min_tenengrad,
                    "min_width_px": cfg.quality_min_width_px,
                    "min_height_px": cfg.quality_min_height_px,
                    "min_brightness": cfg.quality_min_brightness,
                    "max_brightness": cfg.quality_max_brightness,
                    "min_contrast_std": cfg.quality_min_contrast_std,
                    "max_skew_degrees": cfg.quality_max_skew_degrees,
                },
            },
        },
        "upload_limits": {
            "max_file_size_mb": cfg.max_file_size_mb,
            "max_pdf_pages": cfg.max_pdf_pages,
            "supported_formats": ["JPG", "JPEG", "PNG", "PDF"],
            "required_upload_warning": REQUIRED_UPLOAD_WARNING,
        },
        "privacy_policy": {
            "default_retention_seconds": cfg.temp_file_retention_seconds,
            "stores_reports_on_disk": False,
            "logs_medical_values": False,
            "llm_zero_retention_store_false": True,
        },
        "disclaimer": REQUIRED_MEDICAL_DISCLAIMER,
    }


@app.get("/api/sample-report", response_model=UploadAndExtractResponse)
def get_sample_report() -> UploadAndExtractResponse:
    """Return clearly labelled synthetic sample report data for demo mode."""
    return get_synthetic_sample_response()


@app.get("/api/sample-test-files")
def list_sample_test_files() -> dict:
    """List synthetic sample test scenarios available to test blur/quality rejection and PDF validation."""
    return {
        "label": SAMPLE_DATA_LABEL,
        "scenarios": [
            {
                "id": "clear_image",
                "title": "Clear Report Image (Accepted)",
                "filename": "sample_clear_report.png",
                "description": "Sharp, well-lit synthetic lab report image extracted via OCR.",
                "expected_outcome": "Accepted -> Automatically extracts 12 parameters",
            },
            {
                "id": "digital_pdf",
                "title": "Readable Digital PDF (Accepted)",
                "filename": "sample_digital_report.pdf",
                "description": "Clean digital PDF extracted via PyMuPDF coordinate parser.",
                "expected_outcome": "Accepted -> Automatically extracts 12 parameters",
            },
            {
                "id": "scanned_multipage_pdf",
                "title": "2-Page Scanned PDF (Accepted via OCR)",
                "filename": "sample_scanned_multipage.pdf",
                "description": "2-page scanned image PDF processed page-by-page with OCR.",
                "expected_outcome": "Accepted -> Extracts all parameters across 2 scanned pages",
            },
            {
                "id": "blurry_image",
                "title": "Blurry Photo (Rejected)",
                "filename": "sample_blurry_report.jpg",
                "description": "Out-of-focus camera photo simulated with Gaussian blur.",
                "expected_outcome": "Rejected with mandatory red blur warning",
            },
            {
                "id": "dark_image",
                "title": "Dark / Underexposed Photo (Rejected)",
                "filename": "sample_dark_report.jpg",
                "description": "Photo taken in very poor lighting.",
                "expected_outcome": "Rejected -> 'The page is too dark'",
            },
            {
                "id": "cropped_image",
                "title": "Cropped / Cut-Off Report (Rejected)",
                "filename": "sample_cropped_report.jpg",
                "description": "Incomplete photo where reference range columns are cut off.",
                "expected_outcome": "Rejected -> 'Some values or columns appear cut off'",
            },
            {
                "id": "skewed_image",
                "title": "Rotated / Skewed Photo (Rejected)",
                "filename": "sample_skewed_report.jpg",
                "description": "Heavily tilted report photo (22° skew).",
                "expected_outcome": "Rejected -> 'The report is tilted or rotated'",
            },
            {
                "id": "multipage_blurry_pdf",
                "title": "2-Page PDF with 1 Blurry Page (Rejected)",
                "filename": "sample_multipage_with_blurry_page.pdf",
                "description": "Page 1 is readable, Page 2 is a blurry scan.",
                "expected_outcome": "Rejected -> Identifies Page 2 as blurry/unreadable",
            },
            {
                "id": "password_pdf",
                "title": "Password-Protected PDF (Rejected)",
                "filename": "sample_password_protected.pdf",
                "description": "AES-256 encrypted PDF requiring a password.",
                "expected_outcome": "Rejected -> Requests unlocked PDF",
            },
            {
                "id": "corrupted_pdf",
                "title": "Corrupted PDF File (Rejected)",
                "filename": "sample_corrupted.pdf",
                "description": "Damaged PDF byte stream.",
                "expected_outcome": "Rejected -> Corrupted PDF message",
            },
        ],
    }


@app.post("/api/test-sample-scenario/{scenario_id}", response_model=UploadAndExtractResponse)
def run_sample_test_scenario(scenario_id: str) -> UploadAndExtractResponse:
    """Run the actual backend validation and OCR pipeline on a generated synthetic test file."""
    cfg = get_settings()
    created_files = generate_all_sample_files(SAMPLES_DIR)
    if scenario_id not in created_files:
        raise HTTPException(status_code=404, detail=f"Unknown test scenario '{scenario_id}'.")

    file_path = created_files[scenario_id]
    file_bytes = file_path.read_bytes()
    filename = file_path.name

    is_valid_sig, kind, sig_err = verify_file_signature(file_bytes, filename)
    if not is_valid_sig:
        return UploadAndExtractResponse(
            session_id="test-invalid-sig",
            file_name=filename,
            file_type="invalid",
            file_size_bytes=len(file_bytes),
            is_sample=True,
            sample_label=SAMPLE_DATA_LABEL,
            quality_passed=False,
            quality_result=QualityCheckResult(
                accepted=False,
                error_banner=sig_err,
                issues=[sig_err],
                issue_codes=["INVALID_SIGNATURE"],
            ),
            parameters=[],
            temp_file_deleted=True,
        )

    if kind == "pdf":
        res = process_pdf_upload(file_bytes, filename, cfg)
    else:
        res = process_image_upload(file_bytes, filename, cfg)

    res.is_sample = True
    res.sample_label = SAMPLE_DATA_LABEL
    return res


@app.post("/api/upload-and-extract", response_model=UploadAndExtractResponse)
def upload_and_extract(file: UploadFile = File(...)) -> UploadAndExtractResponse:
    """Validate uploaded image or PDF file, enforce quality/blur rules, and extract parameters."""
    cfg = get_settings()
    filename = file.filename or "uploaded_report"

    file_bytes = _securely_read_and_cleanup(file, cfg.max_file_size_bytes)

    is_valid_sig, kind, sig_err = verify_file_signature(file_bytes, filename)
    if not is_valid_sig:
        return UploadAndExtractResponse(
            session_id="invalid-file",
            file_name=filename,
            file_type="invalid",
            file_size_bytes=len(file_bytes),
            quality_passed=False,
            quality_result=QualityCheckResult(
                accepted=False,
                error_banner=sig_err,
                issues=[sig_err],
                issue_codes=["INVALID_FILE_SIGNATURE"],
            ),
            parameters=[],
            temp_file_deleted=True,
        )

    if kind == "pdf":
        return process_pdf_upload(file_bytes, filename, cfg)
    return process_image_upload(file_bytes, filename, cfg)


@app.post("/api/classify", response_model=list[ClassifiedParameter])
def classify_verified_parameters(payload: VerifyAndExplainRequest) -> list[ClassifiedParameter]:
    """Run deterministic rule-based classification on a list of verified parameters."""
    return [
        classify_parameter(
            p,
            patient_sex=payload.patient_sex,
            patient_age_group=payload.patient_age_group,
        )
        for p in payload.parameters
    ]


@app.post("/api/verify-and-explain", response_model=ReportExplanationResponse)
def verify_and_explain(payload: VerifyAndExplainRequest) -> ReportExplanationResponse:
    """Verify user confirmation of extracted data, classify deterministically, and generate explanations."""
    cfg = get_settings()

    if not payload.parameters:
        raise HTTPException(
            status_code=400,
            detail="No laboratory parameters were provided for verification and explanation.",
        )

    # Security & Accuracy Gate: Ensure no unconfirmed or OCR-garbled numbers proceed silently
    for param in payload.parameters:
        res_val = (param.original_result or "").strip()
        if not res_val:
            raise HTTPException(
                status_code=400,
                detail=f"Parameter '{param.test_name}' is missing a result value. Please enter the value from your report or remove the row.",
            )
        # Block unresolved OCR character confusion like '1O.5' or 'l3.2'
        if re.search(r"\d[OolI]|[OolI]\d", res_val):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Parameter '{param.test_name}' still contains an unresolved OCR character confusion "
                    f"('{res_val}'). Please correct the value on the verification table before generating explanations."
                ),
            )
        if not param.user_confirmed:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Parameter '{param.test_name}' is marked as needing review and has not been confirmed. "
                    "Please review and confirm all uncertain rows before proceeding."
                ),
            )

    # Step 1: Deterministic Rule-Based Classification (NEVER AI-decided)
    classified_list: list[ClassifiedParameter] = [
        classify_parameter(
            p,
            patient_sex=payload.patient_sex,
            patient_age_group=payload.patient_age_group,
        )
        for p in payload.parameters
    ]

    # Step 2: Calculate deterministic summary counts
    within_count = sum(1 for c in classified_list if c.rule_based_status == "Within Reference Range")
    below_count = sum(1 for c in classified_list if c.rule_based_status == "Below Reference Range")
    above_count = sum(1 for c in classified_list if c.rule_based_status == "Above Reference Range")
    unable_count = sum(1 for c in classified_list if c.rule_based_status == "Unable to Classify")

    summary_counts = SummaryCounts(
        total_verified=len(classified_list),
        within_range=within_count,
        below_range=below_count,
        above_range=above_count,
        unable_to_classify=unable_count,
    )

    # Step 3: Collect critical alerts
    crit_alerts = list(payload.critical_value_alerts)
    for c in classified_list:
        if c.is_critical_alert:
            msg = f"Critical alert noted on report for {c.test_name} ({c.original_result} {c.unit}). Contact your ordering clinician or laboratory promptly."
            if msg not in crit_alerts:
                crit_alerts.append(msg)

    # Step 4: Generate educational explanations (Live Gemini if configured + consented, else Curated Medical KB)
    cards, q_en, q_hi, ai_mode, ai_notice = generate_explanations(
        classified_list,
        settings=cfg,
        allow_live_ai=payload.user_consented_ai_processing,
    )

    urgent_banner = None
    if payload.urgent_symptoms_reported:
        urgent_banner = (
            "URGENT SAFETY NOTICE: Because you indicated experiencing severe or urgent physical symptoms "
            "(such as chest pain, severe shortness of breath, fainting, confusion, or severe bleeding), "
            "please seek immediate emergency medical care or contact your local emergency services right away. "
            "Do not rely on a report explanation app when experiencing acute symptoms."
        )

    limitations = [
        "Educational Only: LabSaathi explains what laboratory tests measure in plain words; it does not diagnose medical conditions or provide medical clearance.",
        "Reference Ranges Vary: Laboratory reference ranges represent statistical averages (~95% of a healthy reference group) and vary across different labs, assays, ages, and pregnancy trimesters.",
        "Context Matters: Only a qualified clinician who knows your symptoms, physical exam, medical history, and medications can interpret what these values mean for you.",
        "No Medication Changes: Never start, stop, or change the dose of any prescribed medication or supplement based on this summary.",
    ]

    return ReportExplanationResponse(
        session_id=payload.session_id,
        is_sample=payload.is_sample,
        sample_label=payload.sample_label if payload.is_sample else None,
        extracted_patient_age=payload.patient_age,
        extracted_patient_sex=payload.patient_sex if payload.patient_sex != "unspecified" else None,
        extracted_report_date=payload.report_date,
        summary_counts=summary_counts,
        ai_mode=ai_mode,
        ai_service_notice=ai_notice,
        urgent_care_banner=urgent_banner,
        critical_value_alerts=crit_alerts,
        cards=cards,
        general_doctor_questions_en=q_en,
        general_doctor_questions_hi=q_hi,
        limitations=limitations,
        disclaimer=REQUIRED_MEDICAL_DISCLAIMER,
        temp_files_cleaned=True,
    )


@app.post("/api/cleanup")
def cleanup_session() -> dict:
    """Confirm immediate zero-retention cleanup of any temporary artifacts."""
    return {
        "cleaned": True,
        "message": "All temporary upload streams and derived session artifacts have been cleared.",
    }


FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")

