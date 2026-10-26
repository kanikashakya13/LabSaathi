# LabSaathi — Confused by Reports? Decode Them!

**LabSaathi** is a responsive, safety-first medical laboratory report explanation web application that helps patients and families understand blood test and pathology reports in **Plain English** and **Easy Hinglish** (Hindi in Roman script).

> **Medical Disclaimer:** LabSaathi provides educational explanations and is not a substitute for professional medical advice, diagnosis, or treatment. It never diagnoses diseases, never invents missing reference ranges, and never recommends starting, stopping, or changing medications.

---

## Key Architecture & Features

1. **Mandatory OpenCV Image Quality & Blur Detection (`backend/quality_validator.py`)**
   - Validates magic-byte file signatures (`JPEG`, `PNG`, `PDF`) and upload size limits before decoding.
   - Uses multi-signal computer vision (**Laplacian variance** across global and local text tiles, **Tenengrad Sobel gradient energy**, **brightness/exposure**, **contrast**, **specular glare blobs**, **border crop/cut-off detection**, and **Hough text-line skew angle estimation**).
   - Rejects blurry, dark, cropped, or heavily skewed images **before** report interpretation with the mandatory red error banner and retry actions (`Retake Photo`, `Upload Again`, `Choose Another File`).

2. **PDF Structure & Per-Page Scanned Quality Validation (`backend/ocr_pipeline.py`)**
   - Uses **PyMuPDF (`fitz`)** to detect corrupted PDFs, empty PDFs, and password-protected PDFs.
   - Extracts embedded digital text when present, and renders scanned pages at 200 DPI to run per-page OpenCV quality checks.
   - Identifies specific unreadable pages (e.g., *"Page 2: Text is too blurry"*) and prevents unverified pages from being analyzed.
   - Detects multi-patient identifier mismatches across pages and preserves explicit **Laboratory Critical-Value Alerts**.

3. **OCR Extraction & Interactive Verification Screen (`frontend/src/components/ReviewTableView.tsx`)**
   - Detects OCR digit/letter confusions (such as `1O.5` or `l3.2`), suspected missing decimal points (e.g., `58` vs reference range `4.0 - 5.6`), low OCR confidence, and missing reference ranges.
   - Presents an editable review table (`Test Name | Original Result | Unit | Lab Reference Range | Verification Status`) preserving original extracted values for traceability and requiring user confirmation of uncertain rows before proceeding.

4. **Deterministic Rule-Based Result Classification (`backend/classifier.py`)**
   - Strictly deterministic Python logic (never AI-decided) classifies each verified parameter into:
     - `Within Reference Range` (Green + Checkmark icon + text label)
     - `Below Reference Range` (Amber + Down-arrow icon + text label)
     - `Above Reference Range` (Amber + Up-arrow icon + text label)
     - `Unable to Classify` (Neutral Slate + Help icon + text label)
   - Handles closed intervals (`12.0 - 15.5`), strict vs. inclusive inequalities (`< 200` vs. `<= 200`), inequality results (`< 0.01`), qualitative strings (`Negative` / `Non-Reactive`), sex/age-stratified subranges, missing ranges, and unit mismatches (`mg/dL` vs. `mmol/L`).

5. **Bilingual AI Explanation Engine + Curated Medical Reference Fallback (`backend/ai_engine.py` & `backend/medical_kb.py`)**
   - Uses the official `google-genai` SDK (`client.interactions.create` with `model="gemini-3.8-flash"` and `store=False` for zero server-side retention).
   - Sanitizes untrusted report text against prompt injection and validates output against unsafe diagnostic or prescription claims.
   - When `GEMINI_API_KEY` is not configured in `.env`, LabSaathi **honestly notifies the user** and serves complete **Plain English** and **Easy Hinglish** explanations, affecting factors, source attributions (MedlinePlus/NLM, AACC LabTestsOnline, NIDDK, ATA), and doctor questions from its built-in **Vetted Curated Medical Reference Library**.

---

## External Service Credentials & Honest Fallback Behavior

| Feature / Component | External Credential / Binary | Behavior When Not Configured |
| :--- | :--- | :--- |
| **OpenCV Quality & Blur Detection** | None (Runs 100% locally via `opencv-python-headless`) | Always active. |
| **Digital PDF Text Extraction** | None (Runs 100% locally via `PyMuPDF`) | Always active. |
| **Camera Photo OCR** | Optional `TESSERACT_CMD` binary path in `.env` (or `rapidocr-onnxruntime`) | Displays an honest OCR service notice; supports embedded digital PDFs, synthetic sample images (`samples/sample_clear_report.png`), and the interactive Sample Report demo. |
| **AI Explanation Engine** | Optional `GEMINI_API_KEY` in `.env` (`google-genai` SDK, `gemini-3.8-flash`) | Displays a clear setup banner and uses the local **Vetted Curated Medical Reference Library** (`backend/medical_kb.py`) in English & Hinglish without fabricating live AI calls. |

---

## Project Structure

```text
labproject/
├── backend/
│   ├── __init__.py
│   ├── config.py              # Environment settings & configurable CV/OCR thresholds
│   ├── schemas.py             # Pydantic API request/response schemas
│   ├── quality_validator.py   # OpenCV blur, brightness, contrast, glare, crop & skew checks
│   ├── ocr_pipeline.py        # PyMuPDF validation, OCR preprocessing & line parser
│   ├── classifier.py          # Deterministic rule-based reference-range classifier
│   ├── medical_kb.py          # Vetted bilingual (English/Hinglish) medical reference library
│   ├── ai_engine.py           # Gemini Interactions API integration + safety filters
│   ├── sample_data.py         # Synthetic sample report & test asset generator
│   └── main.py                # FastAPI application and endpoints
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── types.ts
│       ├── App.tsx
│       └── components/
│           ├── Navbar.tsx
│           ├── HomeView.tsx
│           ├── UploadView.tsx
│           ├── ReviewTableView.tsx
│           └── ExplanationView.tsx
├── samples/                   # Auto-generated synthetic test images & PDFs
├── tests/
│   └── test_labsaathi.py      # 19 pytest acceptance & integration tests
├── .env.example               # Example environment configuration (no secrets)
├── requirements.txt           # Locked Python dependencies
├── API_DOCS.md                # Endpoint reference documentation
└── README.md                  # Setup and usage guide
```

---

## Quickstart Instructions

### 1. Backend Setup (Python + FastAPI)
```powershell
# Activate the virtual environment and install dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# (Optional) Copy .env.example to .env and add GEMINI_API_KEY if desired
Copy-Item .env.example .env

# Start the FastAPI backend server on http://127.0.0.1:8000
.\.venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup (React + Vite + Tailwind CSS)
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open **`http://localhost:5173`** in your browser.

### 3. Running Automated Tests
```powershell
.\.venv\Scripts\python.exe -m pytest -v
```
