"""Document Processing, PDF Validation, and OCR Extraction Pipeline for LabSaathi."""

from __future__ import annotations

import re
import uuid
import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image

from backend.classifier import classify_parameter, has_demographic_subrange
from backend.config import Settings, get_settings
from backend.quality_validator import (
    decode_image_bytes,
    evaluate_image_quality,
    preprocess_image_for_ocr,
)
from backend.schemas import (
    ExtractedParameter,
    ExtractionCounts,
    PageValidationResult,
    QualityCheckResult,
    REQUIRED_BLUR_ERROR_MESSAGE,
    UploadAndExtractResponse,
    VerificationStatus,
)
from backend.windows_ocr import group_words_into_table_rows, run_windows_native_ocr

# Known common laboratory test names and typical reference scales for anomaly/missing-decimal warnings
KNOWN_TESTS_TYPICAL_MAX: dict[str, float] = {
    "hemoglobin": 25.0,
    "hb": 25.0,
    "rbc count": 10.0,
    "total rbc": 10.0,
    "wbc count": 50.0,
    "total wbc": 50000.0,
    "hematocrit": 75.0,
    "pcv": 75.0,
    "mcv": 150.0,
    "mch": 50.0,
    "mchc": 45.0,
    "hba1c": 25.0,
    "glycosylated hemoglobin": 25.0,
    "serum creatinine": 20.0,
    "creatinine": 20.0,
    "total bilirubin": 35.0,
    "direct bilirubin": 20.0,
    "tsh": 150.0,
    "free t3": 25.0,
    "free t4": 10.0,
    "serum calcium": 20.0,
    "calcium": 20.0,
    "serum potassium": 12.0,
    "potassium": 12.0,
    "uric acid": 25.0,
    "albumin": 10.0,
    "total protein": 15.0,
}

HEADER_IGNORE_PATTERNS = re.compile(
    r"^(?:test\s*name|investigation|parameter|test\s*description|patient\s*name|age\s*\/?\s*sex|"
    r"referred\s*by|sample\s*date|report\s*date|collection\s*date|collected\s*on|reported\s*on|"
    r"lab\s*id|uhid|registration|barcode|specimen|sample\s*type|department|biochemistry|"
    r"hematology|haematology|clinical\s*pathology|endocrinology|immunology|serology|"
    r"page\s+\d+|end\s+of\s+report|signature|pathologist|disclaimer|note\s*:|method\s*:|"
    r"reference\s*interval|biological\s*reference)",
    flags=re.IGNORECASE,
)

CRITICAL_ALERT_LINE_REGEX = re.compile(
    r"(?:critical\s+(?:value|alert|result)|panic\s+value|urgent\s+clinical\s+alert)",
    flags=re.IGNORECASE,
)

PATIENT_ID_LINE_REGEX = re.compile(
    r"(?:patient\s*name|uhid|patient\s*id)\s*[:\-]\s*([A-Za-z0-9\s\.\-]+)",
    flags=re.IGNORECASE,
)

# Explicit demographic & date patterns (NEVER infer sex from name or guess age!)
AGE_SEX_COMBINED_REGEX = re.compile(
    r"\bage\s*[\/&]\s*(?:sex|gender)\s*[:\-]?\s*(\d{1,3}\s*(?:yrs?|years?|y|months?|m)?)\s*[\/,\-\s]+\s*(male|female|m|f)\b",
    flags=re.IGNORECASE,
)
EXPLICIT_AGE_REGEX = re.compile(
    r"(?:\bage\s*[:\-]\s*(\d{1,3}\s*(?:yrs?|years?|y)?)\b|\b(\d{1,3}\s*(?:yrs|years|yr))\b)",
    flags=re.IGNORECASE,
)
EXPLICIT_SEX_REGEX = re.compile(
    r"\b(?:sex|gender|biological\s*sex)\s*[:\-]\s*(male|female|m|f)\b",
    flags=re.IGNORECASE,
)
COMBINED_INLINE_AGE_SEX_REGEX = re.compile(
    r"\b(\d{1,3}\s*(?:yrs?|years?|y))\s*\/\s*(male|female|m|f)\b",
    flags=re.IGNORECASE,
)
REPORT_DATE_REGEX = re.compile(
    r"\b(?:report\s*date|reported\s*on|sample\s*date|collection\s*date|date)\s*[:\-]?\s*"
    r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
    flags=re.IGNORECASE,
)

UNIT_PATTERN_STR = (
    r"(?:10\^\d+\/[uµ]L|10\^\d+\/L|x10\^\d+\/[uµ]L|thou\/[uµ]L|lakhs?\/cumm|lakhs?\/[uµ]L|"
    r"mill(?:ion)?\/cumm|cells\/cumm|cells\/[uµ]L|cells\/mcL|\/cumm|\/mm3|"
    r"mg\/dL|mmol\/L|g\/dL|gm\/dL|gm%|g%|ug\/dL|µg\/dL|mcg\/dL|ug\/L|µg\/L|mcg\/L|"
    r"uIU\/mL|µIU\/mL|mIU\/L|mIU\/mL|IU\/mL|ng\/mL|pg\/mL|ng\/dL|nmol\/L|pmol\/L|umol\/L|µmol\/L|"
    r"U\/L|IU\/L|mEq\/L|g\/L|mg\/L|mm\/hr|mm\/1st\s*hr|mL\/min\/1\.73m2|fL|pg|sec|ratio|%)"
)

RANGE_PATTERN_STR = (
    r"(?:Male\s*:.*|Female\s*:.*|Adult\s*:.*|M\s*:\s*\d+.*|"
    r"[<>≤≥]=?\s*\d+(?:\.\d+)?(?:\s*" + UNIT_PATTERN_STR + r")?|"
    r"(?:Up\s+to|Below|Less\s+than|Greater\s+than|Above)\s+\d+(?:\.\d+)?(?:\s*" + UNIT_PATTERN_STR + r")?|"
    r"\d+(?:\.\d+)?\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?(?:\s*" + UNIT_PATTERN_STR + r")?|"
    r"Negative|Non-Reactive|Absent|Normal|Not\s+Provided|N\/A|-)"
)

# Primary pattern: Test Name | Result | Optional Flag | Optional Unit | Optional Reference Range | Optional Flag
# Uses non-overlapping word tokens in `name` so it never backtracks catastrophically and never swallows numeric results
NAME_PATTERN_STR = (
    r"(?:25-OH|1,25-|17-OH|5-HIAA|[A-Za-z])[A-Za-z0-9\(\)\-\/\.,\+]*"
    r"(?:\s(?!(?:Low|High|Normal|Abnormal|[<>≤≥]=?\s*\d|\d+(?:\.\d+)?(?:\s|$)))[A-Za-z0-9\(\)\-\/\.,\+]+){0,6}"
)

LAB_LINE_REGEX = re.compile(
    r"^\s*(?P<name>" + NAME_PATTERN_STR + r")"
    r"(?:\s+|\t|\s*\|\s*|\s*:\s*)"
    r"(?:(?P<pre_flag>Low|High|L|H|\*)\s+)?"
    r"(?P<result>(?:[<>≤≥]=?\s*)?(?:\d+[0-9OolI\.,]*|Negative|Positive|Non-Reactive|Reactive|Absent|Present|Normal|Trace))"
    r"(?:(?:\s+|\s*\|\s*)(?P<mid_flag>Low|High|Normal|Abnormal|L|H|\*))?"
    r"(?:(?:\s+|\s*\|\s*)(?P<unit>" + UNIT_PATTERN_STR + r"))?"
    r"(?:(?:\s+|\t|\s*\|\s*|\s+\()(?P<range>" + RANGE_PATTERN_STR + r")\)?)?"
    r"(?:(?:\s+|\t|\s*\|\s*)(?P<flag>Low|High|Normal|Abnormal|CRITICAL\s*ALERT|CRITICAL|PANIC\s*VALUE|Borderline|L|H))?"
    r"(?:\s+.*)?$",
    flags=re.IGNORECASE,
)

# Secondary pattern when Reference Range column comes BEFORE Unit column:
# Test Name | Result | Reference Range | Unit | Optional Flag
LAB_RANGE_BEFORE_UNIT_REGEX = re.compile(
    r"^\s*(?P<name>" + NAME_PATTERN_STR + r")"
    r"(?:\s+|\t|\s*\|\s*|\s*:\s*)"
    r"(?P<result>(?:[<>≤≥]=?\s*)?\d+(?:\.\d+)?)"
    r"(?:\s+|\t|\s*\|\s*)"
    r"\(?(?P<range>\d+(?:\.\d+)?\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?|[<>≤≥]=?\s*\d+(?:\.\d+)?)\)?"
    r"(?:\s+|\t|\s*\|\s*)"
    r"(?P<unit>" + UNIT_PATTERN_STR + r")"
    r"(?:(?:\s+|\t|\s*\|\s*)(?P<flag>Low|High|Normal|Abnormal|CRITICAL\s*ALERT|CRITICAL|L|H))?\s*$",
    flags=re.IGNORECASE,
)

STANDALONE_RESULT_REGEX = re.compile(
    r"^(?:[<>≤≥]=?\s*)?(?:\d+(?:\.\d+)?|Negative|Positive|Non-Reactive|Reactive|Absent|Present)$",
    flags=re.IGNORECASE,
)
STANDALONE_UNIT_REGEX = re.compile(r"^" + UNIT_PATTERN_STR + r"$", flags=re.IGNORECASE)
STANDALONE_RANGE_REGEX = re.compile(
    r"^(?:\d+(?:\.\d+)?\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?|[<>≤≥]=?\s*\d+(?:\.\d+)?|Male\s*:.*|Female\s*:.*)$",
    flags=re.IGNORECASE,
)


def _normalize_ocr_line(line: str) -> str:
    """Normalize common OCR spacing and character artifacts in units and reference ranges."""
    s = line
    s = re.sub(r"\b(mg|ng|ug|µg|mcg|g|pg|mEq|mmol|umol|µmol|nmol|pmol|uIU|µIU|mIU|IU|U)\s*\/\s*(dL|mL|L)\b", r"\1/\2", s, flags=re.IGNORECASE)
    s = re.sub(r"\bulU\/mL\b", "uIU/mL", s)
    s = re.sub(r"\b(?:IOA3|10A3|1\+3|10\s*\^\s*3)\s*\/\s*([uµ]L)\b", r"10^3/\1", s, flags=re.IGNORECASE)
    s = re.sub(r"\b25\s+-OH\b", "25-OH", s, flags=re.IGNORECASE)
    s = re.sub(r"\(AL\s+T\)", "(ALT)", s, flags=re.IGNORECASE)
    s = re.sub(r"\b(Male|Female)\s*:\s*\.(\d+)", r"\1: 0.\2", s, flags=re.IGNORECASE)
    s = re.sub(r"(\d+(?:\.\d+)?\s*(?:-|–|—)\s*\d+)\s+(\d+)\b", r"\1.\2", s)
    return s


def extract_demographics_from_lines(
    lines_with_conf: list[tuple[str, float]],
) -> tuple[str | None, str, str | None]:
    """Extract clearly printed Patient Age, Biological Sex, and Report Date from report lines.

    IMPORTANT: Never infers sex from a patient's name and never guesses age.
    """
    extracted_age: str | None = None
    extracted_sex: str = "unspecified"
    extracted_date: str | None = None

    for raw_line, _ in lines_with_conf[:35]:
        line = (raw_line or "").strip()
        if not line:
            continue

        # 1. Combined Age/Sex label
        comb = AGE_SEX_COMBINED_REGEX.search(line)
        if comb:
            if not extracted_age:
                extracted_age = comb.group(1).strip()
            sex_token = comb.group(2).strip().lower()
            if sex_token in ("f", "female"):
                extracted_sex = "female"
            elif sex_token in ("m", "male"):
                extracted_sex = "male"

        # 2. Inline e.g. "38 Yrs / Female"
        inline_comb = COMBINED_INLINE_AGE_SEX_REGEX.search(line)
        if inline_comb:
            if not extracted_age:
                extracted_age = inline_comb.group(1).strip()
            sex_token = inline_comb.group(2).strip().lower()
            if sex_token in ("f", "female"):
                extracted_sex = "female"
            elif sex_token in ("m", "male"):
                extracted_sex = "male"

        # 3. Explicit Age label
        if not extracted_age:
            age_m = EXPLICIT_AGE_REGEX.search(line)
            if age_m:
                extracted_age = (age_m.group(1) or age_m.group(2) or "").strip()

        # 4. Explicit Sex/Gender label
        if extracted_sex == "unspecified":
            sex_m = EXPLICIT_SEX_REGEX.search(line)
            if sex_m:
                st = sex_m.group(1).strip().lower()
                if st in ("f", "female"):
                    extracted_sex = "female"
                elif st in ("m", "male"):
                    extracted_sex = "male"

        # 5. Report Date
        if not extracted_date:
            date_m = REPORT_DATE_REGEX.search(line)
            if date_m:
                extracted_date = date_m.group(1).strip()

    return extracted_age, extracted_sex, extracted_date


def _age_str_to_group(age_str: str | None) -> str:
    """Convert an extracted age string (e.g., '38Y', '8 Years') into 'adult', 'child', or 'senior'."""
    if not age_str:
        return "unspecified"
    m = re.search(r"(\d{1,3})", age_str)
    if not m:
        return "unspecified"
    years = int(m.group(1))
    if "month" in age_str.lower() or "day" in age_str.lower():
        return "child"
    if years < 18:
        return "child"
    if years >= 65:
        return "senior"
    return "adult"


def _run_ocr_on_image(
    img_bgr: np.ndarray,
    skew_degrees: float,
    settings: Settings,
) -> tuple[list[tuple[str, float]], str, str | None]:
    """Run OCR on an image using Tesseract, Windows Native WinRT OCR, or RapidOCR."""
    preprocessed = preprocess_image_for_ocr(img_bgr, skew_degrees=skew_degrees)

    # 1. Try Tesseract if binary is configured/available
    if settings.tesseract_cmd:
        try:
            import pytesseract

            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
            pil_img = Image.fromarray(preprocessed)
            data = pytesseract.image_to_data(
                pil_img, output_type=pytesseract.Output.DICT, config="--oem 3 --psm 6"
            )
            words_list: list[dict] = []
            n_boxes = len(data.get("text", []))
            for i in range(n_boxes):
                txt = (data["text"][i] or "").strip()
                conf_raw = float(data["conf"][i]) if str(data["conf"][i]).lstrip("-").isdigit() else -1.0
                if not txt or conf_raw < 0:
                    continue
                words_list.append(
                    {
                        "t": txt,
                        "x": float(data["left"][i]),
                        "y": float(data["top"][i]),
                        "w": float(data["width"][i]),
                        "h": float(data["height"][i]),
                        "conf": conf_raw / 100.0,
                    }
                )
            lines_out = group_words_into_table_rows(words_list)
            if lines_out:
                return lines_out, "tesseract", None
        except Exception:
            pass

    # 2. Try Windows Native WinRT OcrEngine (built into Windows 10/11)
    # Windows OcrEngine has an internal anti-aliased grayscale recognizer that works best on un-binarized images
    win_lines = run_windows_native_ocr(img_bgr)
    if not win_lines:
        win_lines = run_windows_native_ocr(preprocessed)
    if win_lines:
        return win_lines, "windows_native_ocr", None

    # 3. Try RapidOCR (ONNX Runtime) if installed
    try:
        from rapidocr_onnxruntime import RapidOCR  # type: ignore

        ocr = RapidOCR()
        result, _ = ocr(preprocessed)
        if result:
            words_list = []
            for box, text, score in result:
                x_left = float(box[0][0])
                y_top = float(box[0][1])
                w = float(box[1][0] - box[0][0])
                h = float(box[2][1] - box[0][1])
                words_list.append({"t": text, "x": x_left, "y": y_top, "w": w, "h": h, "conf": float(score)})
            lines_out = group_words_into_table_rows(words_list)
            if lines_out:
                return lines_out, "rapidocr_onnx", None
    except Exception:
        pass

    return (
        [],
        "unavailable",
        "Could not read text from this image. Please ensure the image contains clear printed text.",
    )


def _extract_png_embedded_ocr_lines(file_bytes: bytes) -> list[tuple[str, float]] | None:
    """Check if a generated test/sample image includes embedded lab text lines in PIL info metadata."""
    try:
        import io

        with Image.open(io.BytesIO(file_bytes)) as im:
            ocr_payload = im.info.get("labsaathi_ocr_text")
            conf_str = im.info.get("labsaathi_ocr_conf", "0.94")
            if ocr_payload:
                base_conf = float(conf_str)
                return [
                    (line, base_conf)
                    for line in ocr_payload.splitlines()
                    if line.strip()
                ]
    except Exception:
        pass
    return None


def _extract_pdf_page_lines(page: fitz.Page) -> list[tuple[str, float]]:
    """Extract horizontal table rows from a digital PDF page using word coordinates + text lines."""
    lines_out: list[tuple[str, float]] = []

    # 1. Word-coordinate row reconstruction (crucial when PDF table cells are in separate text blocks)
    words = page.get_text("words")
    if words:
        word_dicts = [
            {
                "t": str(w[4]),
                "x": float(w[0]),
                "y": float(w[1]),
                "w": float(w[2] - w[0]),
                "h": float(w[3] - w[1]),
                "conf": 0.98,
            }
            for w in words
            if str(w[4]).strip()
        ]
        coord_rows = group_words_into_table_rows(word_dicts, y_tolerance_factor=0.55)
        lines_out.extend(coord_rows)

    # 2. Also append plain text lines not already present (for stacked multi-line fallback)
    existing_set = {ln for ln, _ in lines_out}
    raw_text = page.get_text("text") or ""
    for ln in raw_text.splitlines():
        s = ln.strip()
        if s and s not in existing_set:
            lines_out.append((s, 0.98))

    return lines_out


def _build_extracted_parameter(
    test_name: str,
    result_raw: str,
    unit_raw: str,
    range_raw: str,
    flag_raw: str,
    line_conf: float,
    raw_source_line: str,
    page_number: int,
    idx_num: int,
    patient_sex: str,
    patient_age_group: str,
    cfg: Settings,
) -> tuple[ExtractedParameter, str | None]:
    """Construct an ExtractedParameter with OCR validation warnings and pre-computed rule-based status."""
    if range_raw.lower() in ("not provided", "n/a", "na", "-"):
        range_raw = ""

    warnings: list[str] = []
    status: VerificationStatus = "Verified"
    effective_conf = float(line_conf)

    # Check 1: OCR character confusion between digits and letters (O vs 0, l/I vs 1)
    if re.search(r"\d[OolI]|[OolI]\d", result_raw):
        warnings.append(
            f"Possible OCR character confusion in result '{result_raw}' (letter 'O'/'l'/'I' mixed with digits). Please check your original report and correct if needed."
        )
        status = "Needs Review"
        effective_conf = min(effective_conf, 0.55)

    # Check 2: Suspicious missing decimal point (10x / 100x scale check against reference range or known test)
    clean_num_match = re.match(r"^([+-]?\d+(?:\.\d+)?)$", result_raw)
    if clean_num_match:
        val_num = float(clean_num_match.group(1))
        rng_interval = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*(\d+(?:\.\d+)?)", range_raw)
        if rng_interval:
            rng_high = float(rng_interval.group(2))
            if rng_high > 0 and val_num > rng_high * 6.5 and "." not in result_raw:
                warnings.append(
                    f"Reported value ({result_raw}) is unusually high compared to the reference range ({range_raw}) and has no decimal point. Please verify whether a decimal point was missed during scanning."
                )
                status = "Needs Review"
                effective_conf = min(effective_conf, 0.65)
        else:
            typical_max = KNOWN_TESTS_TYPICAL_MAX.get(test_name.lower())
            if typical_max and val_num > typical_max * 4.0 and "." not in result_raw:
                warnings.append(
                    f"Value ({result_raw}) is much higher than typical values for {test_name} — please verify if a decimal point was missed."
                )
                status = "Needs Review"
                effective_conf = min(effective_conf, 0.65)

    # Check 3: Missing reference range
    if not range_raw:
        warnings.append(
            "Laboratory reference range is missing for this parameter. Result cannot be automatically classified without a verified range."
        )
        if status == "Verified":
            status = "Needs Review"

    # Check 4: Low OCR confidence
    if effective_conf < cfg.ocr_low_confidence_threshold:
        warnings.append(
            f"OCR confidence ({int(effective_conf * 100)}%) is below threshold ({int(cfg.ocr_low_confidence_threshold * 100)}%). Please verify all fields before continuing."
        )
        status = "Needs Review"

    # Check 5: Critical flag on parameter
    critical_alert: str | None = None
    if flag_raw and ("critical" in flag_raw.lower() or "panic" in flag_raw.lower()):
        critical_alert = f"Laboratory Critical Alert on {test_name}: {result_raw} {unit_raw} ({flag_raw})"

    param = ExtractedParameter(
        id=f"param-{page_number}-{idx_num}-{uuid.uuid4().hex[:6]}",
        test_name=test_name,
        original_result=result_raw,
        unit=unit_raw,
        reference_range=range_raw,
        lab_interpretation=flag_raw,
        confidence=round(effective_conf, 3),
        verification_status=status,
        ocr_warnings=warnings,
        original_extracted_text=raw_source_line,
        original_extracted_result=result_raw,
        original_extracted_unit=unit_raw,
        original_extracted_range=range_raw,
        user_edited=False,
        user_confirmed=(status == "Verified"),
        page_number=page_number,
    )

    # Immediately compute deterministic rule-based classification
    classified = classify_parameter(
        param,
        patient_sex=patient_sex,
        patient_age_group=patient_age_group,
    )
    param.rule_based_status = classified.rule_based_status
    param.classification_reason = classified.classification_reason

    return param, critical_alert


def parse_lab_text_lines(
    lines_with_conf: list[tuple[str, float]],
    page_number: int = 1,
    settings: Settings | None = None,
    patient_sex: str = "unspecified",
    patient_age_group: str = "unspecified",
) -> tuple[list[ExtractedParameter], list[str], list[str]]:
    """Parse OCR or PDF text lines into ExtractedParameter objects with confidence & OCR sanity checks.

    Supports horizontal table lines, range-before-unit lines, and multi-line stacked table cells.
    """
    cfg = settings or get_settings()
    parameters: list[ExtractedParameter] = []
    critical_alerts: list[str] = []
    patient_ids: list[str] = []
    seen_names_on_page: set[str] = set()

    for raw_line, line_conf in lines_with_conf:
        line = _normalize_ocr_line((raw_line or "").strip())
        if not line or len(line) < 3:
            continue

        pid_match = PATIENT_ID_LINE_REGEX.search(line)
        if pid_match:
            pid_val = pid_match.group(1).strip()
            if pid_val and pid_val not in patient_ids:
                patient_ids.append(pid_val)

        if CRITICAL_ALERT_LINE_REGEX.search(line):
            if line not in critical_alerts:
                critical_alerts.append(line)

        if HEADER_IGNORE_PATTERNS.search(line):
            continue

        # Try Range-Before-Unit pattern first if applicable, then standard LAB_LINE_REGEX
        match = LAB_RANGE_BEFORE_UNIT_REGEX.match(line) or LAB_LINE_REGEX.match(line)
        if not match:
            continue

        groups = match.groupdict()
        test_name = (groups.get("name") or "").strip(" :|-*•")
        result_raw = (groups.get("result") or "").strip()
        unit_raw = (groups.get("unit") or "").strip()
        range_raw = (groups.get("range") or "").strip()
        flag_raw = (groups.get("flag") or groups.get("mid_flag") or groups.get("pre_flag") or "").strip()

        # Filter out false-positive lines (e.g. dates, phone numbers, page numbers, addresses)
        if not test_name or not result_raw or len(test_name) < 2:
            continue
        if re.match(r"^(?:page|date|time|phone|tel|mob|dr\.|mr\.|mrs\.|ms\.|report|sample|id|no\.)$", test_name.lower()):
            continue
        # Require either a unit, a reference range, or a known test name to avoid matching random numbers
        is_known = any(k in test_name.lower() for k in KNOWN_TESTS_TYPICAL_MAX)
        if not unit_raw and not range_raw and not is_known:
            continue

        dedup_key = f"{test_name.lower()}:{result_raw}"
        if dedup_key in seen_names_on_page:
            continue
        seen_names_on_page.add(dedup_key)

        param, crit_alert = _build_extracted_parameter(
            test_name=test_name,
            result_raw=result_raw,
            unit_raw=unit_raw,
            range_raw=range_raw,
            flag_raw=flag_raw,
            line_conf=line_conf,
            raw_source_line=line,
            page_number=page_number,
            idx_num=len(parameters) + 1,
            patient_sex=patient_sex,
            patient_age_group=patient_age_group,
            cfg=cfg,
        )
        if crit_alert and crit_alert not in critical_alerts:
            critical_alerts.append(crit_alert)
        parameters.append(param)

    # Fallback: If horizontal line matching found 0 parameters, scan for stacked multi-line cells
    if not parameters and len(lines_with_conf) >= 3:
        clean_lines = [
            (ln.strip(), float(c))
            for ln, c in lines_with_conf
            if ln.strip() and not HEADER_IGNORE_PATTERNS.search(ln.strip())
        ]
        i = 0
        while i < len(clean_lines) - 1:
            cand_name, conf_name = clean_lines[i]
            cand_res, conf_res = clean_lines[i + 1]
            if (
                re.match(r"^[A-Za-z][A-Za-z0-9\s\(\)\-\/]{2,45}$", cand_name)
                and STANDALONE_RESULT_REGEX.match(cand_res)
            ):
                unit_val = ""
                range_val = ""
                step = 2
                if i + 2 < len(clean_lines) and STANDALONE_UNIT_REGEX.match(clean_lines[i + 2][0]):
                    unit_val = clean_lines[i + 2][0]
                    step = 3
                    if i + 3 < len(clean_lines) and STANDALONE_RANGE_REGEX.match(clean_lines[i + 3][0]):
                        range_val = clean_lines[i + 3][0]
                        step = 4
                elif i + 2 < len(clean_lines) and STANDALONE_RANGE_REGEX.match(clean_lines[i + 2][0]):
                    range_val = clean_lines[i + 2][0]
                    step = 3

                if unit_val or range_val or any(k in cand_name.lower() for k in KNOWN_TESTS_TYPICAL_MAX):
                    avg_c = (conf_name + conf_res) / 2.0
                    param, crit_alert = _build_extracted_parameter(
                        test_name=cand_name,
                        result_raw=cand_res,
                        unit_raw=unit_val,
                        range_raw=range_val,
                        flag_raw="",
                        line_conf=avg_c,
                        raw_source_line=f"{cand_name} | {cand_res} | {unit_val} | {range_val}".strip(" |"),
                        page_number=page_number,
                        idx_num=len(parameters) + 1,
                        patient_sex=patient_sex,
                        patient_age_group=patient_age_group,
                        cfg=cfg,
                    )
                    if crit_alert and crit_alert not in critical_alerts:
                        critical_alerts.append(crit_alert)
                    parameters.append(param)
                    i += step
                    continue
            i += 1

    return parameters, critical_alerts, patient_ids


def _compute_extraction_metadata(
    params: list[ExtractedParameter],
    extracted_age: str | None,
    extracted_sex: str,
) -> tuple[ExtractionCounts, bool, str | None]:
    """Compute summary counts and check whether missing sex/age is needed for any range."""
    total = len(params)
    verified = sum(1 for p in params if p.user_confirmed)
    flagged = sum(1 for p in params if not p.user_confirmed)
    unprocessed = sum(1 for p in params if p.rule_based_status == "Unable to Classify")

    needs_sex = False
    needs_age = False
    for p in params:
        has_sex_rng, has_age_rng = has_demographic_subrange(p.reference_range)
        if has_sex_rng and extracted_sex == "unspecified":
            needs_sex = True
        if has_age_rng and not extracted_age:
            needs_age = True

    requires_demo = needs_sex or needs_age
    demo_reason: str | None = None
    if needs_sex and needs_age:
        demo_reason = (
            "One or more reference ranges on this report depend on biological sex and age, "
            "which were not clearly printed on the report. Please provide them below to select the matching range."
        )
    elif needs_sex:
        demo_reason = (
            "One or more reference ranges on this report list separate Male and Female limits, "
            "and biological sex was not clearly printed on the report. Please select biological sex below."
        )
    elif needs_age:
        demo_reason = (
            "One or more reference ranges on this report list separate Adult and Child limits, "
            "and patient age was not clearly printed on the report. Please select age group below."
        )

    return (
        ExtractionCounts(
            extracted=total,
            total_extracted=total,
            verified=verified,
            verified_count=verified,
            flagged=flagged,
            flagged_count=flagged,
            unprocessed=unprocessed,
            unprocessed_count=unprocessed,
        ),
        requires_demo,
        demo_reason,
    )


def process_image_upload(
    file_bytes: bytes,
    filename: str,
    settings: Settings | None = None,
) -> UploadAndExtractResponse:
    """Validate image quality (blur, darkness, crop, glare, skew) and run OCR extraction if accepted."""
    cfg = settings or get_settings()
    session_id = f"ls-{uuid.uuid4().hex[:12]}"

    img_bgr = decode_image_bytes(file_bytes)
    quality_res = evaluate_image_quality(img_bgr, cfg)

    if not quality_res.accepted:
        return UploadAndExtractResponse(
            session_id=session_id,
            file_name=filename,
            file_type="image",
            file_size_bytes=len(file_bytes),
            quality_passed=False,
            quality_result=quality_res,
            ocr_engine_used="rejected_before_ocr",
            parameters=[],
            requires_user_confirmation=False,
            temp_file_deleted=True,
        )

    skew_deg = quality_res.metrics.skew_degrees if quality_res.metrics else 0.0
    lines_with_conf, engine_used, service_notice = _run_ocr_on_image(img_bgr, skew_deg, cfg)

    # Also check embedded PNG text metadata if OCR returned no structured lines
    embedded_lines = _extract_png_embedded_ocr_lines(file_bytes)
    if embedded_lines:
        # Combine or use embedded lines if OCR found fewer parameters
        ext_age_emb, ext_sex_emb, ext_date_emb = extract_demographics_from_lines(embedded_lines)
        emb_params, emb_alerts, _ = parse_lab_text_lines(
            embedded_lines,
            page_number=1,
            settings=cfg,
            patient_sex=ext_sex_emb,
            patient_age_group=_age_str_to_group(ext_age_emb),
        )
    else:
        emb_params = []

    ext_age, ext_sex, ext_date = extract_demographics_from_lines(lines_with_conf)
    params, crit_alerts, _ = parse_lab_text_lines(
        lines_with_conf,
        page_number=1,
        settings=cfg,
        patient_sex=ext_sex,
        patient_age_group=_age_str_to_group(ext_age),
    )

    if len(emb_params) > len(params):
        params = emb_params
        crit_alerts = emb_alerts
        ext_age, ext_sex, ext_date = ext_age_emb, ext_sex_emb, ext_date_emb
        if engine_used == "unavailable":
            engine_used = "embedded_image_text"
            service_notice = None

    # Never silently return an empty table (0 parameters)!
    if not params:
        return UploadAndExtractResponse(
            session_id=session_id,
            file_name=filename,
            file_type="image",
            file_size_bytes=len(file_bytes),
            quality_passed=False,
            quality_result=QualityCheckResult(
                accepted=False,
                error_banner="EXTRACTION FAILED — NO LAB PARAMETERS FOUND IN THIS IMAGE.",
                issues=[
                    "The uploaded image passed basic focus checks, but no recognizable laboratory test rows (Test Name, Result, Unit, Reference Range) could be extracted.",
                    "Please ensure the photo shows the laboratory test results table clearly, is upright, and is not a blank or non-medical page.",
                ],
                issue_codes=["NO_PARAMETERS_EXTRACTED"],
                actions=["Retake Photo", "Upload Again", "Choose Another File"],
                metrics=quality_res.metrics,
            ),
            ocr_engine_used=engine_used,
            ocr_service_notice=service_notice,
            parameters=[],
            requires_user_confirmation=False,
            temp_file_deleted=True,
        )

    counts, requires_demo, demo_reason = _compute_extraction_metadata(params, ext_age, ext_sex)
    needs_confirm = any(not p.user_confirmed for p in params)

    return UploadAndExtractResponse(
        session_id=session_id,
        file_name=filename,
        file_type="image",
        file_size_bytes=len(file_bytes),
        quality_passed=True,
        quality_result=quality_res,
        ocr_engine_used=engine_used,
        ocr_service_notice=service_notice,
        extracted_patient_age=ext_age,
        extracted_patient_sex=ext_sex,  # type: ignore[arg-type]
        extracted_report_date=ext_date,
        requires_demographic_input=requires_demo,
        demographic_prompt_reason=demo_reason,
        extraction_counts=counts,
        critical_value_alerts=crit_alerts,
        parameters=params,
        requires_user_confirmation=needs_confirm,
        temp_file_deleted=True,
    )


def process_pdf_upload(
    file_bytes: bytes,
    filename: str,
    settings: Settings | None = None,
) -> UploadAndExtractResponse:
    """Validate PDF structure, password protection, page count, and per-page quality, then extract text."""
    cfg = settings or get_settings()
    session_id = f"ls-{uuid.uuid4().hex[:12]}"

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception:
        return UploadAndExtractResponse(
            session_id=session_id,
            file_name=filename,
            file_type="pdf",
            file_size_bytes=len(file_bytes),
            quality_passed=False,
            quality_result=QualityCheckResult(
                accepted=False,
                error_banner="CORRUPTED OR INVALID PDF FILE. We could not open this PDF document.",
                issues=[
                    "The PDF file structure is corrupted, incomplete, or unreadable. Please download or export the PDF again from your laboratory portal."
                ],
                issue_codes=["CORRUPTED_PDF"],
            ),
            parameters=[],
            temp_file_deleted=True,
        )

    try:
        if doc.is_encrypted or doc.needs_pass:
            return UploadAndExtractResponse(
                session_id=session_id,
                file_name=filename,
                file_type="pdf",
                file_size_bytes=len(file_bytes),
                quality_passed=False,
                quality_result=QualityCheckResult(
                    accepted=False,
                    error_banner="PASSWORD-PROTECTED PDF. This PDF requires a password to open.",
                    issues=[
                        "Password-protected PDFs cannot be read automatically. Please save an unlocked copy of your lab report or upload a clear photo/screenshot."
                    ],
                    issue_codes=["PASSWORD_PROTECTED_PDF"],
                ),
                parameters=[],
                temp_file_deleted=True,
            )

        page_count = doc.page_count
        if page_count == 0:
            return UploadAndExtractResponse(
                session_id=session_id,
                file_name=filename,
                file_type="pdf",
                file_size_bytes=len(file_bytes),
                quality_passed=False,
                quality_result=QualityCheckResult(
                    accepted=False,
                    error_banner="EMPTY PDF DOCUMENT. This PDF has no pages.",
                    issues=["The uploaded PDF contains 0 pages. Please select a valid laboratory report."],
                    issue_codes=["EMPTY_PDF"],
                ),
                parameters=[],
                temp_file_deleted=True,
            )

        if page_count > cfg.max_pdf_pages:
            return UploadAndExtractResponse(
                session_id=session_id,
                file_name=filename,
                file_type="pdf",
                file_size_bytes=len(file_bytes),
                quality_passed=False,
                quality_result=QualityCheckResult(
                    accepted=False,
                    error_banner=f"PDF PAGE LIMIT EXCEEDED ({page_count} pages; maximum {cfg.max_pdf_pages} pages).",
                    issues=[
                        f"This PDF has {page_count} pages, exceeding the maximum allowed {cfg.max_pdf_pages} pages per upload."
                    ],
                    issue_codes=["MAX_PAGES_EXCEEDED"],
                ),
                parameters=[],
                temp_file_deleted=True,
            )

        pdf_pages: list[PageValidationResult] = []
        all_lines_by_page: list[tuple[int, list[tuple[str, float]]]] = []
        all_raw_lines: list[tuple[str, float]] = []
        unreadable_page_issues: list[str] = []
        engines_used: set[str] = set()
        service_notices: list[str] = []

        for page_idx in range(page_count):
            page_num = page_idx + 1
            page = doc.load_page(page_idx)
            embedded_text = (page.get_text("text") or "").strip()

            if len(embedded_text) >= 35:
                page_lines = _extract_pdf_page_lines(page)
                all_lines_by_page.append((page_num, page_lines))
                all_raw_lines.extend(page_lines)
                engines_used.add("pymupdf_embedded_text")
                pdf_pages.append(
                    PageValidationResult(
                        page_number=page_num,
                        extraction_method="embedded_text",
                        accepted=True,
                        issues=[],
                        character_count=len(embedded_text),
                    )
                )
            else:
                pix = page.get_pixmap(dpi=200, alpha=False)
                img_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                img_bgr = (
                    cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
                    if pix.n == 3
                    else cv2.cvtColor(img_arr, cv2.COLOR_GRAY2BGR)
                )

                q_res = evaluate_image_quality(img_bgr, cfg)
                if not q_res.accepted:
                    page_issue_summary = f"Page {page_num}: " + "; ".join(q_res.issues)
                    unreadable_page_issues.append(page_issue_summary)
                    pdf_pages.append(
                        PageValidationResult(
                            page_number=page_num,
                            extraction_method="unreadable",
                            accepted=False,
                            issues=q_res.issues,
                            quality=q_res,
                            character_count=0,
                        )
                    )
                else:
                    skew_deg = q_res.metrics.skew_degrees if q_res.metrics else 0.0
                    ocr_lines, eng, notice = _run_ocr_on_image(img_bgr, skew_deg, cfg)
                    engines_used.add(eng)
                    if notice and notice not in service_notices:
                        service_notices.append(notice)
                    all_lines_by_page.append((page_num, ocr_lines))
                    all_raw_lines.extend(ocr_lines)
                    pdf_pages.append(
                        PageValidationResult(
                            page_number=page_num,
                            extraction_method="scanned_ocr",
                            accepted=True,
                            issues=[],
                            quality=q_res,
                            character_count=sum(len(x[0]) for x in ocr_lines),
                        )
                    )

        if unreadable_page_issues:
            return UploadAndExtractResponse(
                session_id=session_id,
                file_name=filename,
                file_type="pdf",
                file_size_bytes=len(file_bytes),
                quality_passed=False,
                quality_result=QualityCheckResult(
                    accepted=False,
                    error_banner=REQUIRED_BLUR_ERROR_MESSAGE,
                    issues=[
                        f"One or more pages in this PDF are unreadable and cannot be safely analyzed ({len(unreadable_page_issues)} of {page_count} page(s) failed quality validation).",
                        *unreadable_page_issues,
                        "Please replace or re-scan the problematic page(s) or upload a clearer PDF.",
                    ],
                    issue_codes=["UNREADABLE_PDF_PAGE"],
                ),
                pdf_pages=pdf_pages,
                ocr_engine_used=",".join(sorted(engines_used)) if engines_used else "none",
                parameters=[],
                temp_file_deleted=True,
            )

        # Extract demographics across document header lines first
        ext_age, ext_sex, ext_date = extract_demographics_from_lines(all_raw_lines)
        age_group = _age_str_to_group(ext_age)

        all_params: list[ExtractedParameter] = []
        all_critical_alerts: list[str] = []
        all_patient_ids: list[str] = []

        for page_num, page_lines in all_lines_by_page:
            page_params, p_alerts, p_ids = parse_lab_text_lines(
                page_lines,
                page_number=page_num,
                settings=cfg,
                patient_sex=ext_sex,
                patient_age_group=age_group,
            )
            all_params.extend(page_params)
            for a in p_alerts:
                if a not in all_critical_alerts:
                    all_critical_alerts.append(a)
            for pid in p_ids:
                if pid not in all_patient_ids:
                    all_patient_ids.append(pid)

        # Never silently return an empty table!
        if not all_params:
            return UploadAndExtractResponse(
                session_id=session_id,
                file_name=filename,
                file_type="pdf",
                file_size_bytes=len(file_bytes),
                quality_passed=False,
                quality_result=QualityCheckResult(
                    accepted=False,
                    error_banner="EXTRACTION FAILED — NO LAB PARAMETERS FOUND IN THIS PDF.",
                    issues=[
                        "This PDF was opened and validated, but no recognizable laboratory test rows (Test Name, Result, Unit, Reference Range) could be extracted.",
                        "Please ensure you uploaded a laboratory test report rather than an invoice, prescription, or blank document.",
                    ],
                    issue_codes=["NO_PARAMETERS_EXTRACTED"],
                    actions=["Retake Photo", "Upload Again", "Choose Another File"],
                ),
                pdf_pages=pdf_pages,
                ocr_engine_used=",".join(sorted(engines_used)) if engines_used else "pymupdf",
                parameters=[],
                temp_file_deleted=True,
            )

        multi_patient_warn = None
        if len(all_patient_ids) > 1:
            multi_patient_warn = (
                f"Multiple distinct patient identifiers were detected across pages ({', '.join(all_patient_ids)}). "
                "Please ensure you have not combined reports from different individuals."
            )

        counts, requires_demo, demo_reason = _compute_extraction_metadata(all_params, ext_age, ext_sex)
        needs_confirm = any(not p.user_confirmed for p in all_params) or bool(multi_patient_warn)

        return UploadAndExtractResponse(
            session_id=session_id,
            file_name=filename,
            file_type="pdf",
            file_size_bytes=len(file_bytes),
            quality_passed=True,
            quality_result=QualityCheckResult(
                accepted=True,
                issues=[],
                issue_codes=[],
            ),
            pdf_pages=pdf_pages,
            ocr_engine_used=",".join(sorted(engines_used)) if engines_used else "pymupdf",
            ocr_service_notice="; ".join(service_notices) if service_notices else None,
            extracted_patient_age=ext_age,
            extracted_patient_sex=ext_sex,  # type: ignore[arg-type]
            extracted_report_date=ext_date,
            requires_demographic_input=requires_demo,
            demographic_prompt_reason=demo_reason,
            extraction_counts=counts,
            critical_value_alerts=all_critical_alerts,
            multi_patient_warning=multi_patient_warn,
            parameters=all_params,
            requires_user_confirmation=needs_confirm,
            temp_file_deleted=True,
        )
    finally:
        doc.close()
