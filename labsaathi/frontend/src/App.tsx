import React, { useEffect, useState } from 'react';
import { CheckCircle2, FileCheck2, Stethoscope } from 'lucide-react';
import { Navbar } from './components/Navbar';
import { HomeView } from './components/HomeView';
import { UploadView } from './components/UploadView';
import { ReviewTableView } from './components/ReviewTableView';
import { ExplanationView } from './components/ExplanationView';
import {
  CLIENT_SYNTHETIC_SAMPLE_REPORT,
  getClientSyntheticExplanationResponse,
} from './sampleData';
import {
  ExtractedParameter,
  HealthResponse,
  ReportExplanationResponse,
  SampleScenario,
  UploadAndExtractResponse,
} from './types';

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

const DEFAULT_SAMPLE_SCENARIOS: SampleScenario[] = [
  {
    id: 'clear_image',
    title: 'Clear Report Image (Accepted)',
    filename: 'sample_clear_report.png',
    description: 'Sharp, well-lit synthetic lab report image extracted via OCR.',
    expected_outcome: 'Accepted -> Automatically extracts 11 parameters',
  },
  {
    id: 'digital_pdf',
    title: 'Readable Digital PDF (Accepted)',
    filename: 'sample_digital_report.pdf',
    description: 'Clean digital PDF extracted via PyMuPDF coordinate parser.',
    expected_outcome: 'Accepted -> Automatically extracts 11 parameters',
  },
  {
    id: 'scanned_multipage_pdf',
    title: '2-Page Scanned PDF (Accepted via OCR)',
    filename: 'sample_scanned_multipage.pdf',
    description: '2-page scanned image PDF processed page-by-page with OCR.',
    expected_outcome: 'Accepted -> Extracts parameters across 2 scanned pages',
  },
  {
    id: 'blurry_image',
    title: 'Blurry Photo (Rejected)',
    filename: 'sample_blurry_report.jpg',
    description: 'Out-of-focus camera photo simulated with Gaussian blur.',
    expected_outcome: 'Rejected with mandatory red blur warning',
  },
  {
    id: 'dark_image',
    title: 'Dark / Underexposed Photo (Rejected)',
    filename: 'sample_dark_report.jpg',
    description: 'Photo taken in very poor lighting.',
    expected_outcome: "Rejected -> 'The page is too dark'",
  },
  {
    id: 'cropped_image',
    title: 'Cropped / Cut-Off Report (Rejected)',
    filename: 'sample_cropped_report.jpg',
    description: 'Incomplete photo where reference range columns are cut off.',
    expected_outcome: "Rejected -> 'Some values or columns appear cut off'",
  },
];

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'home' | 'upload' | 'review' | 'results'>('home');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [scenarios, setScenarios] = useState<SampleScenario[]>(DEFAULT_SAMPLE_SCENARIOS);

  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const [extractionData, setExtractionData] = useState<UploadAndExtractResponse | null>(null);
  const [reportData, setReportData] = useState<ReportExplanationResponse | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data && data.services) {
          setHealth(data);
        } else {
          // Default health presentation for Netlify static demo
          setHealth({
            status: 'ok',
            app_name: 'LabSaathi',
            tagline: 'Confused by Reports? Decode Them!',
            version: '1.0.0',
            services: {
              ai_explanation_service: {
                configured: false,
                provider: 'Google Gemini Interactions API',
                model: 'gemini-3.8-flash',
                credential_env_var: 'GEMINI_API_KEY',
                fallback_mode: 'Vetted Curated Medical Reference Library (English & Hinglish)',
                setup_message:
                  'Netlify Preview Mode: Using Curated Medical Reference Library. For live Gemini AI, set GEMINI_API_KEY on the backend server.',
              },
              ocr_service: {
                tesseract_detected: false,
                windows_native_ocr: true,
                pdf_embedded_text_engine: 'PyMuPDF (fitz) + Coordinate Row Reconstruction',
                credential_or_binary_env_var: 'TESSERACT_CMD',
                setup_message:
                  'Windows Native WinRT OCR + PyMuPDF active on local backend. Netlify frontend connected.',
              },
              image_quality_cv: {
                engine: 'OpenCV (Laplacian Variance + Tenengrad + Brightness/Contrast/Glare/Skew/Crop)',
                thresholds: {},
              },
            },
            upload_limits: {
              max_file_size_mb: 15,
              max_pdf_pages: 10,
              supported_formats: ['JPG', 'JPEG', 'PNG', 'PDF'],
              required_upload_warning:
                'IMPORTANT: Please upload a clear and readable lab report. Ensure all test names, values, units, and reference ranges are visible. Blurry or unreadable images will not be accepted. Please click the photo again clearly.',
            },
            privacy_policy: {
              default_retention_seconds: 0,
              stores_reports_on_disk: false,
              logs_medical_values: false,
              llm_zero_retention_store_false: true,
            },
            disclaimer:
              'LabSaathi provides educational explanations and is not a substitute for professional medical advice, diagnosis, or treatment.',
          });
        }
      })
      .catch(() => {});

    fetch(`${API_BASE}/api/sample-test-files`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.scenarios && Array.isArray(data.scenarios)) {
          setScenarios(data.scenarios);
        }
      })
      .catch(() => {});
  }, []);

  const handleNavigateHome = (sectionId?: string) => {
    setActiveTab('home');
    setTimeout(() => {
      if (sectionId && sectionId !== 'top') {
        const el = document.getElementById(sectionId);
        el?.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 50);
  };

  const handleStartUpload = () => {
    setActiveTab('upload');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleTrySampleReport = async () => {
    setUploading(true);
    setReviewError(null);
    try {
      const res = await fetch(`${API_BASE}/api/sample-report`);
      if (!res.ok) throw new Error('API not reached, using client-side fallback');
      const data: UploadAndExtractResponse = await res.json();
      setExtractionData(data);
      setActiveTab('review');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch {
      // Seamless static preview fallback on Netlify without backend
      setExtractionData(CLIENT_SYNTHETIC_SAMPLE_REPORT);
      setActiveTab('review');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setUploading(false);
    }
  };

  const handleUploadFile = async (file: File) => {
    setUploading(true);
    setReviewError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE}/api/upload-and-extract`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail || `Upload failed with status ${res.status}`);
      }
      const data: UploadAndExtractResponse = await res.json();
      setExtractionData(data);
      if (data.quality_passed && data.parameters.length > 0) {
        setActiveTab('review');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error && !err.message.includes('Failed to fetch')
          ? err.message
          : 'Netlify Static Preview: Live camera OCR and OpenCV blur checks require the Python backend server. To test the full extraction, table verification, and medical explanations, click "Try Sample Report" or deploy the backend to Render/Railway and set VITE_API_URL in Netlify settings.';

      setExtractionData({
        session_id: 'err',
        file_name: file.name,
        file_type: 'error',
        file_size_bytes: file.size,
        is_sample: false,
        sample_label: null,
        quality_passed: false,
        quality_result: {
          accepted: false,
          error_banner: message,
          issues: [message],
          issue_codes: ['BACKEND_CONNECTION_NOTICE'],
          actions: ['Try Sample Report', 'Upload Again', 'Choose Another File'],
          metrics: null,
        },
        pdf_pages: [],
        ocr_engine_used: 'none',
        ocr_service_notice: null,
        extracted_patient_age: null,
        extracted_patient_sex: null,
        extracted_report_date: null,
        requires_demographic_input: false,
        demographic_prompt_reason: null,
        extraction_counts: {
          extracted: 0,
          total_extracted: 0,
          verified: 0,
          verified_count: 0,
          flagged: 0,
          flagged_count: 0,
          unprocessed: 0,
          unprocessed_count: 0,
        },
        critical_value_alerts: [],
        multi_patient_warning: null,
        unsupported_format_notice: null,
        parameters: [],
        requires_user_confirmation: false,
        temp_file_deleted: true,
        disclaimer:
          'LabSaathi provides educational explanations and is not a substitute for professional medical advice, diagnosis, or treatment.',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleRunTestScenario = async (scenarioId: string) => {
    setUploading(true);
    setReviewError(null);
    try {
      const res = await fetch(`${API_BASE}/api/test-sample-scenario/${scenarioId}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Scenario test failed');
      const data: UploadAndExtractResponse = await res.json();
      setExtractionData(data);
      if (data.quality_passed && data.parameters.length > 0) {
        setActiveTab('review');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch {
      // If scenario requires backend OpenCV binary on Netlify, load sample report or stay on upload
      if (scenarioId === 'clear_image' || scenarioId === 'digital_pdf') {
        setExtractionData(CLIENT_SYNTHETIC_SAMPLE_REPORT);
        setActiveTab('review');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateExplanations = async (payload: {
    parameters: ExtractedParameter[];
    patientSex: 'unspecified' | 'female' | 'male';
    patientAgeGroup: 'unspecified' | 'adult' | 'child' | 'senior';
    patientAge: string | null;
    reportDate: string | null;
    userConsentedAi: boolean;
    urgentSymptomsReported: boolean;
  }) => {
    if (!extractionData) return;
    setGenerating(true);
    setReviewError(null);

    try {
      const res = await fetch(`${API_BASE}/api/verify-and-explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: extractionData.session_id,
          is_sample: extractionData.is_sample,
          sample_label: extractionData.sample_label,
          patient_sex: payload.patientSex,
          patient_age_group: payload.patientAgeGroup,
          patient_age: payload.patientAge,
          report_date: payload.reportDate,
          critical_value_alerts: extractionData.critical_value_alerts,
          user_consented_ai_processing: payload.userConsentedAi,
          urgent_symptoms_reported: payload.urgentSymptomsReported,
          parameters: payload.parameters,
        }),
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        setReviewError(
          errBody.detail ||
            'Please confirm all flagged rows and resolve any OCR warnings before proceeding.'
        );
        return;
      }

      const data: ReportExplanationResponse = await res.json();
      setExtractionData({
        ...extractionData,
        parameters: payload.parameters,
      });
      setReportData(data);
      setActiveTab('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch {
      // Fallback on Netlify static preview
      const fallbackReport = getClientSyntheticExplanationResponse(payload.parameters);
      setExtractionData({
        ...extractionData,
        parameters: payload.parameters,
      });
      setReportData(fallbackReport);
      setActiveTab('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <Navbar
        activeTab={activeTab}
        onNavigateHome={handleNavigateHome}
        onStartUpload={handleStartUpload}
        onTrySample={handleTrySampleReport}
        health={health}
      />

      {/* Workflow Step Progress Indicator when inside Upload -> Review -> Results */}
      {activeTab !== 'home' && (
        <div
          aria-label="Report Processing Progress"
          className="bg-white border-b border-slate-200 py-3 px-4 no-print"
        >
          <div className="max-w-5xl mx-auto flex items-center justify-between text-xs sm:text-sm">
            {[
              { id: 'upload', step: 1, label: '1. Upload & Blur Check' },
              { id: 'review', step: 2, label: '2. Verify Extracted Data' },
              { id: 'results', step: 3, label: '3. Explanations & Doctor Questions' },
            ].map((item) => {
              const isCurrent = activeTab === item.id;
              const isCompleted =
                (item.id === 'upload' && (activeTab === 'review' || activeTab === 'results')) ||
                (item.id === 'review' && activeTab === 'results');

              return (
                <div
                  key={item.id}
                  className={`flex items-center gap-2 font-semibold ${
                    isCurrent
                      ? 'text-teal-800'
                      : isCompleted
                      ? 'text-emerald-700'
                      : 'text-slate-400'
                  }`}
                >
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      isCurrent
                        ? 'bg-teal-700 text-white'
                        : isCompleted
                        ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                        : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : item.step}
                  </span>
                  <span>{item.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Landmark */}
      <main id="main-content" tabIndex={-1} className="flex-1 outline-none">
        {activeTab === 'home' && (
          <HomeView
            onStartUpload={handleStartUpload}
            onTrySample={handleTrySampleReport}
            loadingSample={uploading}
            health={health}
          />
        )}

        {activeTab === 'upload' && (
          <UploadView
            onUploadFile={handleUploadFile}
            onTrySampleReport={handleTrySampleReport}
            onRunTestScenario={handleRunTestScenario}
            uploading={uploading}
            lastUploadResult={extractionData}
            onClearError={() => setExtractionData(null)}
            scenarios={scenarios}
            maxFileSizeMb={health?.upload_limits.max_file_size_mb || 15}
          />
        )}

        {activeTab === 'review' && extractionData && (
          <ReviewTableView
            extractionData={extractionData}
            onBackToUpload={() => setActiveTab('upload')}
            onGenerateExplanations={handleGenerateExplanations}
            generating={generating}
            errorMessage={reviewError}
          />
        )}

        {activeTab === 'results' && reportData && (
          <ExplanationView
            report={reportData}
            onBackToReview={() => setActiveTab('review')}
            onStartNewUpload={() => {
              setExtractionData(null);
              setReportData(null);
              setActiveTab('upload');
            }}
          />
        )}
      </main>

      {/* Accessible Footer with Persistent Disclaimer */}
      <footer className="bg-white border-t border-slate-200 mt-16 py-10 text-xs sm:text-sm text-slate-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3">
            <Stethoscope className="w-5 h-5 text-teal-700 shrink-0 mt-0.5" aria-hidden="true" />
            <p className="text-slate-800 font-medium">
              <strong>Medical Safety Disclaimer:</strong> LabSaathi provides educational
              explanations and is not a substitute for professional medical advice, diagnosis, or
              treatment. Never start, stop, or alter any medication based on this application. If
              you are experiencing a medical emergency, call your local emergency number or visit
              the nearest hospital immediately.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-2 border-t border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-teal-700 text-white flex items-center justify-center">
                <FileCheck2 className="w-4 h-4" aria-hidden="true" />
              </div>
              <div>
                <span className="font-bold text-slate-900">LabSaathi</span> —{' '}
                <span>Confused by Reports? Decode Them!</span>
              </div>
            </div>

            <div className="text-xs text-slate-500">
              Zero Default File Retention • Rule-Based Classification • English & Hinglish Support
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
