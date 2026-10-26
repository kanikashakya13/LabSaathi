"""OpenCV Computer-Vision Image Quality and Blur Detection Engine for LabSaathi."""

from __future__ import annotations

import cv2
import numpy as np
from backend.config import Settings, get_settings
from backend.schemas import (
    QualityCheckResult,
    QualityMetrics,
    REQUIRED_BLUR_ERROR_MESSAGE,
)

ALLOWED_IMAGE_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
}
PDF_SIGNATURE = b"%PDF-"


def verify_file_signature(file_bytes: bytes, filename: str) -> tuple[bool, str, str]:
    """Verify file magic bytes match supported formats (JPG, JPEG, PNG, PDF).

    Returns: (is_valid, detected_kind, error_message)
    where detected_kind is 'image', 'pdf', or 'invalid'.
    """
    if not file_bytes or len(file_bytes) < 8:
        return False, "invalid", "The uploaded file is empty or corrupted."

    ext = (filename or "").lower().rsplit(".", 1)[-1] if "." in (filename or "") else ""
    if file_bytes.startswith(PDF_SIGNATURE):
        if ext not in ("pdf", ""):
            return False, "invalid", f"File signature is PDF but extension is .{ext}."
        return True, "pdf", ""

    for mime, sigs in ALLOWED_IMAGE_SIGNATURES.items():
        for sig in sigs:
            if file_bytes.startswith(sig):
                if ext not in ("jpg", "jpeg", "png", ""):
                    return False, "invalid", f"File signature is {mime} but extension is .{ext}."
                return True, "image", ""

    return (
        False,
        "invalid",
        "Unsupported or corrupted file format. Please upload a valid JPG, JPEG, PNG, or PDF file.",
    )


def decode_image_bytes(image_bytes: bytes) -> np.ndarray | None:
    """Decode raw image bytes into a BGR OpenCV numpy array safely."""
    try:
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def _estimate_skew_degrees(gray: np.ndarray) -> float:
    """Estimate document skew angle in degrees using morphological text-line Hough transform."""
    h, w = gray.shape[:2]
    # Invert binary threshold so text is white on black
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Connect horizontal characters into text lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(15, w // 30), 3))
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    edges = cv2.Canny(dilated, 50, 150)

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180.0,
        threshold=max(40, w // 12),
        minLineLength=max(50, w // 6),
        maxLineGap=20,
    )
    if lines is None or len(lines) == 0:
        return 0.0

    angles: list[float] = []
    for line in lines:
        coords = line[0] if np.ndim(line) > 1 else line
        x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) < 5:
            # Nearly vertical line — check if whole page is rotated ~90 deg
            continue
        angle = float(np.degrees(np.arctan2(dy, dx)))
        if -45.0 <= angle <= 45.0:
            angles.append(angle)

    if len(angles) < 3:
        return 0.0
    return round(float(np.median(angles)), 2)


def _compute_local_sharpness(gray: np.ndarray) -> float:
    """Compute 75th-percentile Laplacian variance across a 4x4 grid of non-blank tiles.

    This prevents large white margins on clean lab reports from artificially lowering
    the sharpness score while still catching genuinely blurry text.
    """
    h, w = gray.shape[:2]
    rows, cols = 4, 4
    dh, dw = max(1, h // rows), max(1, w // cols)
    tile_vars: list[float] = []
    for r in range(rows):
        for c in range(cols):
            tile = gray[r * dh : (r + 1) * dh, c * dw : (c + 1) * dw]
            if tile.size == 0:
                continue
            # Only consider tiles that have some foreground ink variation
            if float(np.std(tile)) > 8.0:
                lap = cv2.Laplacian(tile, cv2.CV_64F)
                tile_vars.append(float(lap.var()))
    if not tile_vars:
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return float(np.percentile(tile_vars, 75))


def _compute_edge_cutoff_And_text_density(gray: np.ndarray) -> tuple[float, float]:
    """Detect whether text content is abruptly severed at the left/right edges (cropped report)
    and estimate overall text region density.
    """
    h, w = gray.shape[:2]
    # Adaptive threshold to isolate dark text strokes
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15
    )
    # Remove tiny single-pixel sensor noise
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    text_density = float(np.count_nonzero(cleaned)) / float(max(1, h * w))

    # Check outer 1.5% left and right borders where test names or reference ranges get cut off
    border_w = max(4, int(w * 0.015))
    left_strip = cleaned[int(h * 0.1) : int(h * 0.9), :border_w]
    right_strip = cleaned[int(h * 0.1) : int(h * 0.9), w - border_w :]

    left_density = float(np.count_nonzero(left_strip)) / float(max(1, left_strip.size))
    right_density = float(np.count_nonzero(right_strip)) / float(max(1, right_strip.size))
    edge_cut_ratio = round(max(left_density, right_density), 4)

    return edge_cut_ratio, round(text_density, 4)


def _compute_glare_spot_score(gray: np.ndarray) -> float:
    """Detect localized camera flash glare or specular reflection hotspots on a darker document."""
    h, w = gray.shape[:2]
    mean_val = float(np.mean(gray))
    # Glare is a bright saturated patch (>248) when the rest of the photo has gray background (<225)
    # Or overall washout when almost all pixels are >250 with tiny text density
    bright_mask = (gray > 248).astype(np.uint8)
    raw_bright_ratio = float(np.count_nonzero(bright_mask)) / float(max(1, h * w))
    if mean_val < 228.0:
        # Camera photo with paper gray background: check for large contiguous glare blobs
        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(bright_mask)
        max_blob_ratio = 0.0
        for idx in range(1, num_labels):
            area = stats[idx, cv2.CC_STAT_AREA]
            ratio = float(area) / float(max(1, h * w))
            if ratio > max_blob_ratio:
                max_blob_ratio = ratio
        return round(max_blob_ratio, 4)
    return round(raw_bright_ratio * 0.25, 4)


def evaluate_image_quality(
    img_bgr: np.ndarray,
    settings: Settings | None = None,
) -> QualityCheckResult:
    """Run multi-signal OpenCV quality and blur validation on an image.

    Checks:
    1. Resolution & minimum dimensions (low resolution / tiny unreadable text)
    2. Sharpness / Blur using BOTH Laplacian variance (global + local text tiles) AND Tenengrad Sobel gradient energy
    3. Brightness & exposure (excessive darkness or overexposure)
    4. Contrast (standard deviation + dynamic range)
    5. Glare / Flash reflection hotspots
    6. Cropped / incomplete page borders & aspect ratio
    7. Skew / rotation angle
    """
    cfg = settings or get_settings()

    if img_bgr is None or img_bgr.size == 0:
        return QualityCheckResult(
            accepted=False,
            error_banner=REQUIRED_BLUR_ERROR_MESSAGE,
            issues=["Could not decode image data. The file appears corrupted or unreadable."],
            issue_codes=["CORRUPTED_IMAGE"],
        )

    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) if len(img_bgr.shape) == 3 else img_bgr

    # 1. Sharpness metrics (Laplacian variance + local tile Laplacian + Tenengrad gradient)
    global_lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    local_lap_var = _compute_local_sharpness(gray)
    effective_lap_var = round(max(global_lap_var, local_lap_var * 0.85), 2)

    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    tenengrad = round(float(np.mean(gx**2 + gy**2)), 2)

    # 2. Brightness & Contrast
    brightness_mean = round(float(np.mean(gray)), 2)
    contrast_std = round(float(np.std(gray)), 2)

    # 3. Glare, Skew, Cropping, Text Density
    glare_ratio = _compute_glare_spot_score(gray)
    skew_degrees = _estimate_skew_degrees(gray)
    edge_cut_ratio, text_density = _compute_edge_cutoff_And_text_density(gray)

    metrics = QualityMetrics(
        laplacian_variance=effective_lap_var,
        tenengrad_score=tenengrad,
        brightness_mean=brightness_mean,
        contrast_std=contrast_std,
        glare_ratio=glare_ratio,
        skew_degrees=skew_degrees,
        width=w,
        height=h,
        edge_cut_ratio=edge_cut_ratio,
        text_density_score=text_density,
    )

    issues: list[str] = []
    issue_codes: list[str] = []

    # Check A: Resolution
    if w < cfg.quality_min_width_px or h < cfg.quality_min_height_px:
        issues.append(
            f"Image resolution is too low ({w}x{h} px; minimum {cfg.quality_min_width_px}x{cfg.quality_min_height_px} px required to read small lab numbers clearly)."
        )
        issue_codes.append("LOW_RESOLUTION")

    # Check B: Cropped / incomplete aspect ratio or severed border columns
    aspect_ratio = float(w) / float(max(1, h))
    if aspect_ratio < 0.32 or aspect_ratio > 2.6 or edge_cut_ratio > 0.22:
        issues.append(
            "Some values or columns appear cut off at the edge of the photo. Please capture the entire report page with all margins visible."
        )
        issue_codes.append("CROPPED_PAGE")

    # Check C: Darkness / Underexposure
    if brightness_mean < cfg.quality_min_brightness:
        issues.append(
            f"The page is too dark (brightness {brightness_mean}/255). Please retake the photo in good lighting."
        )
        issue_codes.append("TOO_DARK")

    # Check D: Overexposure / Blank washed-out page
    if brightness_mean > cfg.quality_max_brightness and contrast_std < cfg.quality_min_contrast_std:
        issues.append(
            "The page is overexposed or blank — text is washed out and unreadable."
        )
        issue_codes.append("OVEREXPOSED")

    # Check E: Poor contrast
    if contrast_std < cfg.quality_min_contrast_std and "OVEREXPOSED" not in issue_codes:
        issues.append(
            f"Contrast is too low (score {contrast_std}). Text cannot be reliably separated from the background."
        )
        issue_codes.append("LOW_CONTRAST")

    # Check F: Glare hotspot
    if glare_ratio > cfg.quality_max_glare_ratio:
        issues.append(
            "Strong glare or flash reflection detected on the page. Please avoid direct overhead glare or turn off camera flash."
        )
        issue_codes.append("EXCESSIVE_GLARE")

    # Check G: Blur / Sharpness (combining Laplacian variance and Tenengrad edge energy)
    is_laplacian_blurry = effective_lap_var < cfg.quality_min_laplacian_var
    is_tenengrad_blurry = tenengrad < cfg.quality_min_tenengrad
    if is_laplacian_blurry and is_tenengrad_blurry:
        issues.append(
            f"Text is too blurry (sharpness score {effective_lap_var:.1f}, gradient energy {tenengrad:.1f}). Hold the camera steady and tap to focus on the report text."
        )
        issue_codes.append("BLURRY_IMAGE")
    elif effective_lap_var < (cfg.quality_min_laplacian_var * 0.65):
        issues.append(
            f"Text is out of focus (sharpness score {effective_lap_var:.1f} is well below the readable threshold of {cfg.quality_min_laplacian_var:.1f})."
        )
        issue_codes.append("BLURRY_IMAGE")

    # Check H: Excessive Skew / Rotation
    if abs(skew_degrees) > cfg.quality_max_skew_degrees:
        issues.append(
            f"The report is tilted or rotated ({skew_degrees:+.1f}°). Please align the camera straight above the report."
        )
        issue_codes.append("EXCESSIVE_SKEW")

    # Check I: Almost no text-like content
    if text_density < 0.0025 and "OVEREXPOSED" not in issue_codes:
        issues.append(
            "No readable laboratory text structure was detected on the page."
        )
        issue_codes.append("NO_TEXT_DETECTED")

    accepted = len(issues) == 0
    return QualityCheckResult(
        accepted=accepted,
        error_banner=None if accepted else REQUIRED_BLUR_ERROR_MESSAGE,
        issues=issues,
        issue_codes=issue_codes,
        metrics=metrics,
    )


def preprocess_image_for_ocr(img_bgr: np.ndarray, skew_degrees: float = 0.0) -> np.ndarray:
    """Preprocess an accepted image to maximize OCR accuracy (deskew, CLAHE contrast, denoise)."""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) if len(img_bgr.shape) == 3 else img_bgr.copy()

    # 1. Mild deskew if between 0.8 and 14 degrees
    if 0.8 <= abs(skew_degrees) <= 14.0:
        h, w = gray.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, skew_degrees, 1.0)
        gray = cv2.warpAffine(
            gray,
            rot_mat,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

    # 2. Upscale slightly if width < 1100px so small decimal points are crisp for OCR
    h, w = gray.shape[:2]
    if w < 1100:
        scale = 1200.0 / float(max(1, w))
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 3. CLAHE local contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 4. Gentle bilateral filter preserving sharp text edges
    denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=30, sigmaSpace=30)
    return denoised
