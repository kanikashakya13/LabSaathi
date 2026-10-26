import React from 'react';
import {
  BookOpen,
  Camera,
  CheckCircle2,
  ClipboardCheck,
  Eye,
  FileSearch,
  FileText,
  HelpCircle,
  Languages,
  Lock,
  MessageSquarePlus,
  Scale,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  Trash2,
  Upload,
} from 'lucide-react';
import { HealthResponse } from '../types';

interface HomeViewProps {
  onStartUpload: () => void;
  onTrySample: () => void;
  loadingSample: boolean;
  health: HealthResponse | null;
}

export const HomeView: React.FC<HomeViewProps> = ({
  onStartUpload,
  onTrySample,
  loadingSample,
  health,
}) => {
  return (
    <div id="top" className="space-y-16 pb-16">
      {/* HERO SECTION */}
      <section className="relative bg-gradient-to-b from-teal-50/70 via-white to-white pt-10 pb-12 border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-teal-100/80 text-teal-900 text-xs sm:text-sm font-semibold border border-teal-200">
                <Languages className="w-4 h-4 text-teal-700" aria-hidden="true" />
                <span>Confused by Reports? Decode Them!</span>
              </div>

              <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
                Medical Reports Made{' '}
                <span className="text-teal-700 underline decoration-teal-300/70 decoration-wavy underline-offset-8">
                  Easy to Understand.
                </span>
              </h1>

              <p className="text-base sm:text-lg text-slate-700 leading-relaxed max-w-2xl">
                Upload a clear, readable blood test or laboratory report (JPG, PNG, or PDF) and
                receive calm, patient-friendly explanations of what each parameter measures in{' '}
                <strong>Plain English</strong> or <strong>Easy Hinglish</strong> — along with
                practical questions to discuss with your doctor.
              </p>

              {/* Primary and Secondary CTAs */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <button
                  type="button"
                  onClick={onStartUpload}
                  className="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl text-base font-semibold bg-teal-700 text-white hover:bg-teal-800 shadow-md hover:shadow-lg transition-all"
                >
                  <Upload className="w-5 h-5" aria-hidden="true" />
                  <span>Understand My Report</span>
                </button>

                <button
                  type="button"
                  onClick={onTrySample}
                  disabled={loadingSample}
                  className="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl text-base font-semibold bg-white text-slate-800 hover:bg-teal-50 hover:text-teal-900 border-2 border-slate-300 hover:border-teal-600 transition-all disabled:opacity-60"
                >
                  <FileText className="w-5 h-5 text-teal-700" aria-hidden="true" />
                  <span>{loadingSample ? 'Loading Sample...' : 'Try Sample Report'}</span>
                </button>
              </div>

              {/* Visible Disclaimer Box */}
              <div
                role="note"
                aria-label="Medical Disclaimer"
                className="p-4 rounded-xl bg-sky-50/90 border border-sky-200 text-slate-800 text-xs sm:text-sm leading-relaxed flex items-start gap-3"
              >
                <Stethoscope
                  className="w-5 h-5 text-sky-700 shrink-0 mt-0.5"
                  aria-hidden="true"
                />
                <div>
                  <strong className="font-semibold text-slate-900">
                    Educational Purpose Disclaimer:
                  </strong>{' '}
                  LabSaathi provides educational explanations and is not a substitute for
                  professional medical advice, diagnosis, or treatment. It never diagnoses
                  conditions or prescribes medicines.
                </div>
              </div>
            </div>

            {/* Right Interactive Preview Card */}
            <div className="lg:col-span-5">
              <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-teal-700">
                      Example Explanation Card
                    </span>
                    <h2 className="text-lg font-bold text-slate-900">Hemoglobin (Hb)</h2>
                  </div>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" aria-hidden="true" />
                    Within Reference Range
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200/70 text-center">
                  <div>
                    <div className="text-xs text-slate-500">Reported Value</div>
                    <div className="text-base font-bold text-slate-900">13.8</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Unit</div>
                    <div className="text-base font-semibold text-slate-800">g/dL</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Lab Reference</div>
                    <div className="text-sm font-semibold text-slate-800">12.0 – 15.5</div>
                  </div>
                </div>

                <div className="space-y-2.5 text-sm">
                  <div className="p-3 rounded-lg bg-teal-50/60 border border-teal-100">
                    <div className="text-xs font-semibold text-teal-900 uppercase tracking-wide mb-1">
                      Plain English
                    </div>
                    <p className="text-slate-700 text-xs sm:text-sm leading-relaxed">
                      Hemoglobin is an iron-rich protein inside red blood cells that carries oxygen
                      from your lungs to tissues throughout your body.
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-sky-50/60 border border-sky-100">
                    <div className="text-xs font-semibold text-sky-900 uppercase tracking-wide mb-1">
                      Easy Hinglish
                    </div>
                    <p className="text-slate-700 text-xs sm:text-sm leading-relaxed">
                      Hemoglobin aapke red blood cells mein paaya jaane wala protein hai jo lungs se
                      poore sharir mein oxygen pahunchata hai.
                    </p>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <span>Rule-Based Status (Not AI-Guessed)</span>
                  <span>Source: MedlinePlus (NLM)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* THREE-STEP OVERVIEW: HOW IT WORKS */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-mt-24">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-10">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700">
            3-Step Guided Workflow
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
            How LabSaathi Helps You Understand Your Report
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">
            Every step is designed to prevent misread numbers, keep reference-range calculations
            deterministic, and explain terms clearly without causing alarm.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center font-bold text-lg">
              1
            </div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Camera className="w-5 h-5 text-teal-700" aria-hidden="true" />
              Upload Your Report
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Upload a JPG, PNG, or PDF report. Before running OCR, our OpenCV computer-vision
              check verifies sharpness, lighting, contrast, page margins, and skew — rejecting
              blurry or unreadable photos so bad data is never guessed.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-xl bg-sky-50 border border-sky-200 text-sky-700 flex items-center justify-center font-bold text-lg">
              2
            </div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <ClipboardCheck className="w-5 h-5 text-sky-700" aria-hidden="true" />
              Understand Each Result
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Review and confirm the extracted test names, values, units, and laboratory reference
              ranges. Deterministic backend logic classifies each value against your lab’s printed
              range, and generates clear English & Hinglish cards.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center font-bold text-lg">
              3
            </div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <MessageSquarePlus className="w-5 h-5 text-teal-700" aria-hidden="true" />
              Prepare Questions for Your Doctor
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Get neutral, relevant questions tailored to your verified report parameters so you can
              have an informed, productive conversation with your physician at your next visit.
            </p>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-mt-24">
        <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-10 shadow-sm space-y-8">
          <div className="max-w-3xl space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-700">
              Safety-First Engineering
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Built for Accuracy, Transparency, and Patient Safety
            </h2>
            <p className="text-slate-600 text-sm sm:text-base">
              Unlike generic chat tools that guess unreadable text or hallucinate normal ranges,
              LabSaathi separates computer-vision validation, human verification, rule-based
              classification, and educational language.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <Eye className="w-6 h-6 text-teal-700" aria-hidden="true" />
              <h3 className="font-bold text-slate-900">Mandatory Blur & Quality Guard</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Uses OpenCV Laplacian variance, Sobel gradient energy, brightness/glare analysis,
                and border-crop detection to block blurry or cut-off photos before OCR.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <FileSearch className="w-6 h-6 text-sky-700" aria-hidden="true" />
              <h3 className="font-bold text-slate-900">Editable OCR Verification Table</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Flags low-confidence fields, digit/letter confusions (like <code>1O.5</code>), or
                missing decimal points so you can verify every number against your paper report.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <Scale className="w-6 h-6 text-teal-700" aria-hidden="true" />
              <h3 className="font-bold text-slate-900">Deterministic Range Status</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Whether a value is Within, Below, or Above Reference Range is calculated by
                deterministic Python rules using your lab’s printed range — never decided by AI.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <Languages className="w-6 h-6 text-sky-700" aria-hidden="true" />
              <h3 className="font-bold text-slate-900">Plain English & Easy Hinglish</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Switch effortlessly between Plain English, Easy Hinglish, or Side-by-Side view so
                patients and family members can read together comfortably.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <BookOpen className="w-6 h-6 text-teal-700" aria-hidden="true" />
              <h3 className="font-bold text-slate-900">Vetted Medical Attribution</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Explanations are grounded in educational material from MedlinePlus (NLM), Testing.com
                (AACC), NIDDK, and ATA, showing clear source attribution on every card.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <ShieldAlert className="w-6 h-6 text-sky-700" aria-hidden="true" />
              <h3 className="font-bold text-slate-900">No Disease Scores or Prescriptions</h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                We never invent missing reference ranges, never output a fake "health score", and
                never advise starting, stopping, or changing medications.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ABOUT & EXTERNAL SERVICE TRANSPARENCY SECTION */}
      <section id="about" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-mt-24">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-700">
              About LabSaathi
            </span>
            <h2 className="text-2xl font-bold text-slate-900">
              Bridging the Gap Between Lab Numbers and Doctor Visits
            </h2>
            <p className="text-sm text-slate-700 leading-relaxed">
              When patients receive a laboratory report before their doctor appointment, unfamiliar
              abbreviations like <em>HbA1c, SGPT (ALT), MCV, eGFR, or TSH</em> often cause confusion
              or unnecessary anxiety.
            </p>
            <p className="text-sm text-slate-700 leading-relaxed">
              LabSaathi was built with a single mission: to translate complex pathology terminology
              into calm, everyday language while respecting clinical boundaries. An out-of-range
              result does not automatically mean disease, and an in-range result does not guarantee
              complete health — LabSaathi helps you understand what was measured so you can speak
              confidently with your doctor.
            </p>
          </div>

          <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-teal-700" aria-hidden="true" />
              <h2 className="text-xl font-bold text-slate-900">
                Live Service & Credential Transparency
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-600">
              LabSaathi never displays fake AI success messages. Below is the real-time status of
              backend services on this server:
            </p>

            <div className="space-y-3 text-xs sm:text-sm">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <div className="flex items-center justify-between font-semibold text-slate-900">
                  <span>1. Image Quality & Blur CV Engine (OpenCV)</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs">
                    Active (Local)
                  </span>
                </div>
                <p className="text-slate-600 text-xs">
                  Requires no external credentials. Evaluates Laplacian sharpness, Tenengrad edges,
                  brightness, contrast, glare, cropping, and skew angle locally.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <div className="flex items-center justify-between font-semibold text-slate-900">
                  <span>2. PDF & OCR Extraction Pipeline</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs">
                    PyMuPDF Active
                  </span>
                </div>
                <p className="text-slate-600 text-xs">
                  {health?.services.ocr_service.setup_message ||
                    'Digital PDF text extraction via PyMuPDF is active. Set TESSERACT_CMD in .env for external Tesseract OCR.'}
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <div className="flex items-center justify-between font-semibold text-slate-900">
                  <span>3. AI Explanation Engine (`GEMINI_API_KEY`)</span>
                  <span
                    className={`px-2 py-0.5 rounded text-xs ${
                      health?.services.ai_explanation_service.configured
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-sky-100 text-sky-900'
                    }`}
                  >
                    {health?.services.ai_explanation_service.configured
                      ? 'Live Gemini API Configured'
                      : 'Curated Medical KB Mode'}
                  </span>
                </div>
                <p className="text-slate-600 text-xs">
                  {health?.services.ai_explanation_service.setup_message ||
                    'Set GEMINI_API_KEY in .env to enable live Gemini explanations. When unconfigured, LabSaathi transparently uses its built-in Curated Medical Reference Library.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PRIVACY & SECURITY SECTION */}
      <section id="privacy" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-mt-24">
        <div className="bg-gradient-to-br from-slate-900 to-teal-950 text-white rounded-3xl p-6 sm:p-10 shadow-md space-y-6">
          <div className="max-w-3xl space-y-2">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-teal-300">
              <Lock className="w-4 h-4" aria-hidden="true" />
              Privacy & Data Protection
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold">
              Your Lab Report Is Treated as Sensitive Personal Information
            </h2>
            <p className="text-slate-300 text-sm sm:text-base">
              We minimize collection and retention at every step of the workflow.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            <div className="p-5 rounded-2xl bg-white/10 border border-white/15 space-y-2">
              <Trash2 className="w-6 h-6 text-teal-300" aria-hidden="true" />
              <h3 className="font-bold text-white text-base">Zero Default File Retention</h3>
              <p className="text-slate-200 text-xs sm:text-sm leading-relaxed">
                Uploaded images and PDFs are validated and processed transiently, then immediately
                deleted in a server-side <code>finally</code> block. No reports are stored in public
                folders or databases by default.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-white/10 border border-white/15 space-y-2">
              <Lock className="w-6 h-6 text-teal-300" aria-hidden="true" />
              <h3 className="font-bold text-white text-base">Data Minimization for AI</h3>
              <p className="text-slate-200 text-xs sm:text-sm leading-relaxed">
                Patient names, phone numbers, doctor names, and hospital addresses are never sent to
                the AI model. Only verified parameter names, values, units, and ranges are passed
                with <code>store=False</code>, and you can opt out to use local curated explanations.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-white/10 border border-white/15 space-y-2">
              <ShieldCheck className="w-6 h-6 text-teal-300" aria-hidden="true" />
              <h3 className="font-bold text-white text-base">Server-Side Security Controls</h3>
              <p className="text-slate-200 text-xs sm:text-sm leading-relaxed">
                Every upload undergoes server-side magic-byte signature verification, file-size and
                page-count limits, prompt-injection sanitization, and output safety validation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQS SECTION */}
      <section aria-labelledby="faq-heading" className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-2 mb-8">
          <h2 id="faq-heading" className="text-2xl sm:text-3xl font-bold text-slate-900">
            Frequently Asked Questions
          </h2>
          <p className="text-sm text-slate-600">
            Common questions about how LabSaathi works and what it can and cannot do.
          </p>
        </div>

        <div className="space-y-4">
          {[
            {
              q: 'Why was my uploaded lab report photo rejected as blurry or unreadable?',
              a: 'Misreading a single decimal point (for example, reading 13.8 as 138 or 0.5 as 5) can completely change a lab number. LabSaathi uses OpenCV computer vision to check sharpness, brightness, contrast, cropping, and tilt before OCR. If a photo is unclear, we ask you to retake it in good light rather than guessing.',
            },
            {
              q: 'Does the AI decide whether my test value is normal, low, or high?',
              a: 'No. Your status (Within Reference Range, Below Reference Range, Above Reference Range, or Unable to Classify) is calculated deterministically by our rule-based backend using the exact reference range printed on your report. The AI is never allowed to compute or override that status.',
            },
            {
              q: 'What if a test on my report does not have a reference range printed?',
              a: 'Different laboratories use different machines and chemical reagents, so reference ranges vary between labs. If a reference range is missing on your report, LabSaathi will never invent one — it marks the parameter as "Unable to Classify" and still explains what the test generally measures.',
            },
            {
              q: 'Can LabSaathi tell me if I have a disease or what medicine to take?',
              a: 'No. LabSaathi is strictly an educational tool. An out-of-range lab result does not automatically mean you have a disease, and an in-range result does not guarantee complete health. Always consult a qualified doctor before making any health or medication decisions.',
            },
          ].map((faq, idx) => (
            <div
              key={idx}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-2"
            >
              <h3 className="text-base font-bold text-slate-900 flex items-start gap-2.5">
                <HelpCircle
                  className="w-5 h-5 text-teal-700 shrink-0 mt-0.5"
                  aria-hidden="true"
                />
                <span>{faq.q}</span>
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed pl-7">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
