"""Configuration and adjustable thresholds for LabSaathi backend."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_float(key: str, default: float) -> float:
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    try:
        return float(val)
    except ValueError:
        return default


def _get_int(key: str, default: int) -> int:
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    try:
        return int(val)
    except ValueError:
        return default


def _detect_tesseract() -> str | None:
    env_cmd = os.getenv("TESSERACT_CMD", "").strip()
    if env_cmd and Path(env_cmd).exists():
        return env_cmd
    which_cmd = shutil.which("tesseract")
    if which_cmd:
        return which_cmd
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        str(Path.home() / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe"),
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]
    for path in common_paths:
        if Path(path).exists():
            return path
    return None


@dataclass
class Settings:
    """Application settings and CV/OCR thresholds."""

    app_name: str = "LabSaathi"
    tagline: str = "Confused by Reports? Decode Them!"
    version: str = "1.0.0"

    # External AI credentials
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip())
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip() or "gemini-3.8-flash")

    # OCR executable detection
    tesseract_cmd: str | None = field(default_factory=_detect_tesseract)

    # Upload & Security limits
    max_file_size_mb: int = field(default_factory=lambda: _get_int("MAX_FILE_SIZE_MB", 10))
    max_pdf_pages: int = field(default_factory=lambda: _get_int("MAX_PDF_PAGES", 10))
    temp_file_retention_seconds: int = field(default_factory=lambda: _get_int("TEMP_FILE_RETENTION_SECONDS", 0))

    # Image Quality & Blur Detection Thresholds
    quality_min_laplacian_var: float = field(default_factory=lambda: _get_float("QUALITY_MIN_LAPLACIAN_VAR", 65.0))
    quality_min_tenengrad: float = field(default_factory=lambda: _get_float("QUALITY_MIN_TENENGRAD", 320.0))
    quality_min_width_px: int = field(default_factory=lambda: _get_int("QUALITY_MIN_WIDTH_PX", 480))
    quality_min_height_px: int = field(default_factory=lambda: _get_int("QUALITY_MIN_HEIGHT_PX", 480))
    quality_min_brightness: float = field(default_factory=lambda: _get_float("QUALITY_MIN_BRIGHTNESS", 55.0))
    quality_max_brightness: float = field(default_factory=lambda: _get_float("QUALITY_MAX_BRIGHTNESS", 242.0))
    quality_min_contrast_std: float = field(default_factory=lambda: _get_float("QUALITY_MIN_CONTRAST_STD", 22.0))
    quality_max_glare_ratio: float = field(default_factory=lambda: _get_float("QUALITY_MAX_GLARE_RATIO", 0.38))
    quality_max_skew_degrees: float = field(default_factory=lambda: _get_float("QUALITY_MAX_SKEW_DEGREES", 14.0))

    # OCR Confidence
    ocr_low_confidence_threshold: float = field(default_factory=lambda: _get_float("OCR_LOW_CONFIDENCE_THRESHOLD", 0.78))

    # CORS
    allowed_origins: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "ALLOWED_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
            ).split(",")
            if origin.strip()
        ]
    )

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def is_ai_configured(self) -> bool:
        return bool(self.gemini_api_key and len(self.gemini_api_key) > 10 and not self.gemini_api_key.startswith("your_"))


def get_settings() -> Settings:
    return Settings()
