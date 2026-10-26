# LabSaathi API Documentation

Base URL (Local Development): `http://127.0.0.1:8000`  
Interactive Swagger UI: `http://127.0.0.1:8000/docs`  
OpenAPI Schema: `http://127.0.0.1:8000/openapi.json`

---

## 1. `GET /api/health`
Returns service readiness, external credential configuration status (`GEMINI_API_KEY`, `TESSERACT_CMD`), OpenCV quality thresholds, upload limits, and privacy policy metadata.

### Response `200 OK`
```json
{
  "status": "ok",
  "app_name": "LabSaathi",
  "tagline": "Confused by Reports? Decode Them!",
  "version": "1.0.0",
  "services": {
    "ai_explanation_service": {
      "configured": false,
      "provider": "Google Gemini Interactions API",
      "model": "gemini-3.8-flash",
      "credential_env_var": "GEMINI_API_KEY",
      "fallback_mode": "Vetted Curated Medical Reference Library (English & Hinglish)",
      "setup_message": "GEMINI_API_KEY is not set in .env. Using built-in Curated Medical Reference Library (no fabricated AI responses)."
    },
    "ocr_service": {
      "tesseract_detected": false,
      "pdf_embedded_text_engine": "PyMuPDF (fitz)",
      "credential_or_binary_env_var": "TESSERACT_CMD",
      "setup_message": "..."
    }
  }
}
```

---

## 2. `GET /api/sample-report`
Returns the synthetic sample report dataset explicitly labelled `"Sample Data — Not a Real Patient"`, including realistic verified parameters, a low-confidence OCR review parameter, a sex-specific reference range parameter, and a missing-range parameter.

---

## 3. `GET /api/sample-test-files` & `POST /api/test-sample-scenario/{scenario_id}`
Lists and executes the 9 synthetic test files generated in `samples/` against the real OpenCV + PyMuPDF backend validation pipeline:
- `clear_image` (`sample_clear_report.png`) — Accepted
- `blurry_image` (`sample_blurry_report.jpg`) — Rejected (`BLURRY_IMAGE`)
- `dark_image` (`sample_dark_report.jpg`) — Rejected (`TOO_DARK`)
- `cropped_image` (`sample_cropped_report.jpg`) — Rejected (`CROPPED_PAGE`)
- `skewed_image` (`sample_skewed_report.jpg`) — Rejected (`EXCESSIVE_SKEW`)
- `digital_pdf` (`sample_digital_report.pdf`) — Accepted (`embedded_text`)
- `multipage_blurry_pdf` (`sample_multipage_with_blurry_page.pdf`) — Rejected (`UNREADABLE_PDF_PAGE` on Page 2)
- `password_pdf` (`sample_password_protected.pdf`) — Rejected (`PASSWORD_PROTECTED_PDF`)
- `corrupted_pdf` (`sample_corrupted.pdf`) — Rejected (`CORRUPTED_PDF`)

---

## 4. `POST /api/upload-and-extract`
Accepts a `multipart/form-data` `file` upload (`.jpg`, `.jpeg`, `.png`, `.pdf`).
1. Enforces `MAX_FILE_SIZE_MB` and verifies magic-byte file signatures.
2. Runs OpenCV computer-vision image quality & blur detection (`evaluate_image_quality`) or PyMuPDF per-page validation (`process_pdf_upload`).
3. If quality is insufficient, rejects the file **before** report interpretation and returns:
   - `quality_passed: false`
   - `error_banner: "IMAGE IS BLURRY OR UNREADABLE. We couldn't clearly read your lab report. Please retake the photo in good lighting, keep your phone steady, and click again clearly."`
   - `issues`: Specific diagnostic reasons
   - `actions`: `["Retake Photo", "Upload Again", "Choose Another File"]`
4. If accepted, extracts laboratory parameters, flags any low-confidence or digit/decimal-confused rows as `"Needs Review"`, and deletes the temporary upload stream in a `finally` block.

---

## 5. `POST /api/classify`
Runs the deterministic rule-based classification engine (`backend/classifier.py`) on a list of verified parameters without invoking any LLM.
Possible statuses:
- `"Within Reference Range"`
- `"Below Reference Range"`
- `"Above Reference Range"`
- `"Unable to Classify"`

---

## 6. `POST /api/verify-and-explain`
Accepts user-verified parameters (`VerifyAndExplainRequest`).
1. **Verification Gate**: Rejects with `400 Bad Request` if any parameter is unconfirmed (`user_confirmed == false`) or still contains unresolved OCR digit/letter confusions (such as `1O.5`).
2. **Deterministic Classification**: Computes `rule_based_status` and `summary_counts` deterministically via `classifier.py`.
3. **Educational Explanation Generation**:
   - When `GEMINI_API_KEY` is configured and `user_consented_ai_processing == true`, calls the Google Gemini Interactions API (`gemini-3.8-flash`, `store=False`) with sanitized untrusted data tags and validates output against unsafe diagnostic/prescription patterns.
   - When `GEMINI_API_KEY` is not set or opted out, transparently uses `backend/medical_kb.py` (Vetted Curated Medical Reference Library in Plain English & Easy Hinglish).

---

## 7. `POST /api/cleanup`
Confirms zero-retention cleanup of temporary upload streams and derived session state.
