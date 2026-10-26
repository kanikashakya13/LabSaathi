"""Synthetic Sample Reports and Test Document Generator for LabSaathi.

All data in this module is 100% synthetic and explicitly labelled:
"Sample Data — Not a Real Patient".
"""

from __future__ import annotations

from pathlib import Path
import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

from backend.classifier import classify_parameter
from backend.schemas import (
    ExtractedParameter,
    ExtractionCounts,
    QualityCheckResult,
    QualityMetrics,
    UploadAndExtractResponse,
)

SAMPLE_DATA_LABEL = "Sample Data — Not a Real Patient"

SYNTHETIC_REPORT_LINES = [
    "PATIENT NAME: SYNTHETIC DEMO RECORD (NOT A REAL PATIENT)   AGE: 38 Years",
    "REPORT DATE: 12/10/2026   DEPARTMENT OF LABORATORY MEDICINE — SAMPLE REPORT",
    "Hemoglobin (Hb)          11.4      g/dL       12.0 - 15.5       Low",
    "Total WBC Count          7.2       10^3/uL    4.0 - 11.0        Normal",
    "Platelet Count           245       10^3/uL    150 - 410         Normal",
    "Fasting Blood Glucose    116       mg/dL      70 - 99           High",
    "HbA1c                    5.9       %          4.0 - 5.6         High",
    "Total Cholesterol        188       mg/dL      < 200             Normal",
    "Triglycerides            168       mg/dL      < 150             High",
    "Serum Creatinine         0.88      mg/dL      Male: 0.7 - 1.3 | Female: 0.6 - 1.1",
    "TSH (Ultrasensitive)     5.40      uIU/mL     0.40 - 4.50       High",
    "SGPT (ALT)               34        U/L        <= 40             Normal",
    "25-OH Vitamin D          18.2      ng/mL      30.0 - 100.0      Low",
    "Serum Ferritin           42.5      ng/mL      Not Provided",
]


def _load_report_font(size: int = 24) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a crisp TrueType font without slashed zeros for realistic OCR-readable rendering."""
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def get_synthetic_sample_response() -> UploadAndExtractResponse:
    """Return a rich, realistic synthetic sample report for 'Try Sample Report' demo mode."""
    params = [
        ExtractedParameter(
            id="sample-hb",
            test_name="Hemoglobin (Hb)",
            original_result="11.4",
            unit="g/dL",
            reference_range="12.0 - 15.5",
            lab_interpretation="Low",
            confidence=0.98,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="Hemoglobin (Hb) 11.4 g/dL 12.0 - 15.5 Low",
            original_extracted_result="11.4",
            original_extracted_unit="g/dL",
            original_extracted_range="12.0 - 15.5",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-wbc",
            test_name="Total WBC Count",
            original_result="7.2",
            unit="10^3/uL",
            reference_range="4.0 - 11.0",
            lab_interpretation="Normal",
            confidence=0.99,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="Total WBC Count 7.2 10^3/uL 4.0 - 11.0 Normal",
            original_extracted_result="7.2",
            original_extracted_unit="10^3/uL",
            original_extracted_range="4.0 - 11.0",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-plt",
            test_name="Platelet Count",
            original_result="245",
            unit="10^3/uL",
            reference_range="150 - 410",
            lab_interpretation="Normal",
            confidence=0.98,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="Platelet Count 245 10^3/uL 150 - 410 Normal",
            original_extracted_result="245",
            original_extracted_unit="10^3/uL",
            original_extracted_range="150 - 410",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-fbs",
            test_name="Fasting Blood Glucose",
            original_result="116",
            unit="mg/dL",
            reference_range="70 - 99",
            lab_interpretation="High",
            confidence=0.97,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="Fasting Blood Glucose 116 mg/dL 70 - 99 High",
            original_extracted_result="116",
            original_extracted_unit="mg/dL",
            original_extracted_range="70 - 99",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-hba1c",
            test_name="HbA1c",
            original_result="5.9",
            unit="%",
            reference_range="4.0 - 5.6",
            lab_interpretation="High",
            confidence=0.96,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="HbA1c 5.9 % 4.0 - 5.6 High",
            original_extracted_result="5.9",
            original_extracted_unit="%",
            original_extracted_range="4.0 - 5.6",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-chol",
            test_name="Total Cholesterol",
            original_result="188",
            unit="mg/dL",
            reference_range="< 200",
            lab_interpretation="Normal",
            confidence=0.98,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="Total Cholesterol 188 mg/dL < 200 Normal",
            original_extracted_result="188",
            original_extracted_unit="mg/dL",
            original_extracted_range="< 200",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-tg",
            test_name="Triglycerides",
            original_result="168",
            unit="mg/dL",
            reference_range="< 150",
            lab_interpretation="High",
            confidence=0.96,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="Triglycerides 168 mg/dL < 150 High",
            original_extracted_result="168",
            original_extracted_unit="mg/dL",
            original_extracted_range="< 150",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-creat",
            test_name="Serum Creatinine",
            original_result="0.88",
            unit="mg/dL",
            reference_range="Male: 0.7 - 1.3 | Female: 0.6 - 1.1",
            lab_interpretation="",
            confidence=0.95,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="Serum Creatinine 0.88 mg/dL Male: 0.7 - 1.3 | Female: 0.6 - 1.1",
            original_extracted_result="0.88",
            original_extracted_unit="mg/dL",
            original_extracted_range="Male: 0.7 - 1.3 | Female: 0.6 - 1.1",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-tsh",
            test_name="TSH (Ultrasensitive)",
            original_result="5.40",
            unit="uIU/mL",
            reference_range="0.40 - 4.50",
            lab_interpretation="High",
            confidence=0.74,
            verification_status="Needs Review",
            ocr_warnings=[
                "OCR confidence (74%) is below threshold (78%). Please confirm '5.40' against the report before proceeding."
            ],
            original_extracted_text="TSH (Ultrasensitive) 5.40 uIU/mL 0.40 - 4.50 High",
            original_extracted_result="5.40",
            original_extracted_unit="uIU/mL",
            original_extracted_range="0.40 - 4.50",
            user_edited=False,
            user_confirmed=False,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-vitd",
            test_name="25-OH Vitamin D",
            original_result="18.2",
            unit="ng/mL",
            reference_range="30.0 - 100.0",
            lab_interpretation="Low",
            confidence=0.97,
            verification_status="Verified",
            ocr_warnings=[],
            original_extracted_text="25-OH Vitamin D 18.2 ng/mL 30.0 - 100.0 Low",
            original_extracted_result="18.2",
            original_extracted_unit="ng/mL",
            original_extracted_range="30.0 - 100.0",
            user_edited=False,
            user_confirmed=True,
            page_number=1,
        ),
        ExtractedParameter(
            id="sample-ferritin",
            test_name="Serum Ferritin",
            original_result="42.5",
            unit="ng/mL",
            reference_range="",
            lab_interpretation="",
            confidence=0.89,
            verification_status="Needs Review",
            ocr_warnings=[
                "Laboratory reference range is missing for this parameter. Result cannot be automatically classified without a verified range."
            ],
            original_extracted_text="Serum Ferritin 42.5 ng/mL Not Provided",
            original_extracted_result="42.5",
            original_extracted_unit="ng/mL",
            original_extracted_range="",
            user_edited=False,
            user_confirmed=False,
            page_number=1,
        ),
    ]

    for p in params:
        cls_res = classify_parameter(p, patient_sex=None, patient_age_group="adult")
        p.rule_based_status = cls_res.rule_based_status
        p.classification_reason = cls_res.classification_reason

    verified_count = sum(1 for p in params if p.verification_status == "Verified")
    flagged_count = sum(1 for p in params if p.verification_status != "Verified")
    unprocessed_count = sum(1 for p in params if p.rule_based_status == "Unable to Classify")

    return UploadAndExtractResponse(
        session_id="sample-demo-session",
        file_name="LabSaathi_Synthetic_Sample_Report.pdf",
        file_type="sample_demo",
        file_size_bytes=28640,
        is_sample=True,
        sample_label=SAMPLE_DATA_LABEL,
        quality_passed=True,
        quality_result=QualityCheckResult(
            accepted=True,
            issues=[],
            issue_codes=[],
            metrics=QualityMetrics(
                laplacian_variance=420.5,
                tenengrad_score=1890.2,
                brightness_mean=236.0,
                contrast_std=48.2,
                glare_ratio=0.01,
                skew_degrees=0.0,
                width=1240,
                height=1754,
                edge_cut_ratio=0.0,
                text_density_score=0.062,
            ),
        ),
        ocr_engine_used="synthetic_sample_dataset",
        ocr_service_notice=None,
        extracted_patient_age="38 Years",
        extracted_patient_sex="unspecified",
        extracted_report_date="12/10/2026",
        requires_demographic_input=True,
        demographic_prompt_reason=(
            "This report contains sex-specific reference ranges (Serum Creatinine), "
            "and biological sex was not printed on the report. Please select biological sex "
            "if you want sex-specific range selection; otherwise the lab's printed range is retained."
        ),
        extraction_counts=ExtractionCounts(
            total_extracted=len(params),
            verified_count=verified_count,
            flagged_count=flagged_count,
            unprocessed_count=unprocessed_count,
        ),
        critical_value_alerts=[],
        parameters=params,
        requires_user_confirmation=True,
        temp_file_deleted=True,
    )


def render_synthetic_report_pil(
    lines: list[str] | None = None,
    width: int = 1450,
    height: int = 1650,
    bg_color: tuple[int, int, int] = (255, 255, 255),
    fg_color: tuple[int, int, int] = (15, 23, 42),
) -> Image.Image:
    """Render a clean, sharp synthetic laboratory report page as a PIL Image using TrueType fonts."""
    import re as _re

    report_lines = lines if lines is not None else SYNTHETIC_REPORT_LINES
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    header_font = _load_report_font(22)
    body_font = _load_report_font(24)

    # Draw margin border and header bar
    draw.rectangle([45, 45, width - 45, height - 45], outline=(148, 163, 184), width=2)
    draw.rectangle([65, 65, width - 65, 145], fill=(13, 148, 136))
    draw.text(
        (80, 78),
        "LABSAATHI DIAGNOSTIC REFERENCE — SAMPLE DATA (NOT A REAL PATIENT)",
        fill=(255, 255, 255),
        font=header_font,
    )
    draw.text(
        (80, 110),
        "Report ID: SYNTH-2026-001    |    Sample Type: Whole Blood / Serum",
        fill=(226, 232, 240),
        font=header_font,
    )

    y = 168
    # Draw patient demographic / header lines
    for hdr_line in report_lines[:2]:
        draw.text((80, y), hdr_line, fill=fg_color, font=header_font)
        y += 38

    y += 10
    draw.line([(70, y), (width - 70, y)], fill=(71, 85, 105), width=2)
    col_xs = [80, 500, 680, 860, 1280]
    headers = ["TEST PARAMETER", "RESULT", "UNIT", "REFERENCE RANGE", "FLAG"]
    for c_idx, h_txt in enumerate(headers):
        draw.text((col_xs[c_idx], y + 12), h_txt, fill=fg_color, font=header_font)
    y += 48
    draw.line([(70, y), (width - 70, y)], fill=(71, 85, 105), width=2)
    y += 24

    # Draw crisp high-contrast test rows at fixed column coordinates
    for line in report_lines[2:]:
        parts = [p.strip() for p in _re.split(r"\s{2,}", line) if p.strip()]
        if len(parts) >= 3:
            for c_idx, part in enumerate(parts[:5]):
                draw.text((col_xs[c_idx], y), part, fill=fg_color, font=body_font)
        else:
            draw.text((80, y), line, fill=fg_color, font=body_font)
        y += 66

    draw.line([(70, y + 12), (width - 70, y + 12)], fill=(100, 116, 139), width=2)
    draw.text(
        (80, y + 30),
        "Educational Note: Reference ranges are specific to the performing laboratory.",
        fill=(71, 85, 105),
        font=header_font,
    )
    return img


def generate_all_sample_files(output_dir: Path) -> dict[str, Path]:
    """Generate physical sample images and PDFs covering all quality & validation scenarios."""
    output_dir.mkdir(parents=True, exist_ok=True)
    created: dict[str, Path] = {}

    base_pil = render_synthetic_report_pil()

    # 1. Clear, sharp report PNG (readable by Windows Native OCR + embedded metadata fallback)
    clear_path = output_dir / "sample_clear_report.png"
    png_info = PngImagePlugin.PngInfo()
    png_info.add_text("labsaathi_ocr_text", "\n".join(SYNTHETIC_REPORT_LINES))
    png_info.add_text("labsaathi_ocr_conf", "0.96")
    base_pil.save(clear_path, format="PNG", pnginfo=png_info)
    created["clear_image"] = clear_path

    # 2. Blurry report JPG (heavy Gaussian blur)
    bgr = cv2.cvtColor(np.array(base_pil), cv2.COLOR_RGB2BGR)
    blurry_bgr = cv2.GaussianBlur(bgr, (45, 45), 16.0)
    blurry_path = output_dir / "sample_blurry_report.jpg"
    cv2.imwrite(str(blurry_path), blurry_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
    created["blurry_image"] = blurry_path

    # 3. Dark / underexposed report JPG
    dark_bgr = (bgr.astype(np.float32) * 0.14).astype(np.uint8)
    dark_path = output_dir / "sample_dark_report.jpg"
    cv2.imwrite(str(dark_path), dark_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    created["dark_image"] = dark_path

    # 4. Cropped / cut-off report JPG (severed narrow strip)
    cropped_bgr = bgr[:, 120:390].copy()
    cropped_path = output_dir / "sample_cropped_report.jpg"
    cv2.imwrite(str(cropped_path), cropped_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    created["cropped_image"] = cropped_path

    # 5. Heavily skewed / rotated report JPG (22 degrees tilt)
    h, w = bgr.shape[:2]
    rot_mat = cv2.getRotationMatrix2D((w // 2, h // 2), 22.0, 1.0)
    skewed_bgr = cv2.warpAffine(bgr, rot_mat, (w, h), borderValue=(245, 245, 245))
    skewed_path = output_dir / "sample_skewed_report.jpg"
    cv2.imwrite(str(skewed_path), skewed_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    created["skewed_image"] = skewed_path

    # 6. Low-resolution tiny image JPG
    lowres_bgr = cv2.resize(bgr, (280, 350), interpolation=cv2.INTER_AREA)
    lowres_path = output_dir / "sample_lowres_report.jpg"
    cv2.imwrite(str(lowres_path), lowres_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    created["lowres_image"] = lowres_path

    # 7. Readable Digital PDF with embedded text
    digital_pdf_path = output_dir / "sample_digital_report.pdf"
    pdf_doc = fitz.open()
    page = pdf_doc.new_page(width=612, height=792)
    y_pos = 55
    for line in SYNTHETIC_REPORT_LINES:
        page.insert_text((45, y_pos), line, fontsize=10.5, fontname="cour")
        y_pos += 24
    pdf_doc.save(str(digital_pdf_path))
    pdf_doc.close()
    created["digital_pdf"] = digital_pdf_path

    # 8. Readable 2-Page Scanned PDF (image-only pages extracted via OCR)
    scanned_pdf_path = output_dir / "sample_scanned_multipage.pdf"
    scanned_doc = fitz.open()
    page1_pil = render_synthetic_report_pil(lines=SYNTHETIC_REPORT_LINES[:8])
    page2_pil = render_synthetic_report_pil(lines=SYNTHETIC_REPORT_LINES[:2] + SYNTHETIC_REPORT_LINES[8:])
    for pil_page in (page1_pil, page2_pil):
        sp = scanned_doc.new_page(width=612, height=792)
        p_bgr = cv2.cvtColor(np.array(pil_page), cv2.COLOR_RGB2BGR)
        _, p_buf = cv2.imencode(".jpg", p_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
        sp.insert_image(fitz.Rect(18, 18, 594, 774), stream=p_buf.tobytes())
    scanned_doc.save(str(scanned_pdf_path))
    scanned_doc.close()
    created["scanned_multipage_pdf"] = scanned_pdf_path

    # 9. Multi-page PDF with Page 1 readable and Page 2 blurry scanned image
    mixed_pdf_path = output_dir / "sample_multipage_with_blurry_page.pdf"
    mixed_doc = fitz.open()
    p1 = mixed_doc.new_page(width=612, height=792)
    y_pos = 55
    for line in SYNTHETIC_REPORT_LINES[:7]:
        p1.insert_text((45, y_pos), line, fontsize=10.5, fontname="cour")
        y_pos += 24
    p2 = mixed_doc.new_page(width=612, height=792)
    _, img_buf = cv2.imencode(".jpg", blurry_bgr)
    p2.insert_image(fitz.Rect(20, 20, 592, 772), stream=img_buf.tobytes())
    mixed_doc.save(str(mixed_pdf_path))
    mixed_doc.close()
    created["multipage_blurry_pdf"] = mixed_pdf_path

    # 10. Password-protected PDF
    encrypted_pdf_path = output_dir / "sample_password_protected.pdf"
    enc_doc = fitz.open()
    ep = enc_doc.new_page(width=612, height=792)
    ep.insert_text((50, 80), "CONFIDENTIAL LAB REPORT", fontsize=12)
    enc_doc.save(
        str(encrypted_pdf_path),
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw="secret123",
        owner_pw="owner123",
    )
    enc_doc.close()
    created["password_pdf"] = encrypted_pdf_path

    # 11. Corrupted PDF
    corrupted_pdf_path = output_dir / "sample_corrupted.pdf"
    corrupted_pdf_path.write_bytes(b"%PDF-1.7\n%corrupted-broken-xref-stream-incomplete")
    created["corrupted_pdf"] = corrupted_pdf_path

    return created
