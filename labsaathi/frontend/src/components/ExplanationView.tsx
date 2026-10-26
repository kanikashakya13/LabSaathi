import React, { useState } from 'react';
import {
  AlertTriangle,
  ArrowDownCircle,
  ArrowLeft,
  ArrowUpCircle,
  BookOpen,
  CheckCircle2,
  HelpCircle,
  Info,
  Languages,
  MessageSquare,
  Printer,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  Stethoscope,
} from 'lucide-react';
import {
  ClassificationStatus,
  ParameterExplanationCard,
  ReportExplanationResponse,
} from '../types';

interface ExplanationViewProps {
  report: ReportExplanationResponse;
  onBackToReview: () => void;
  onStartNewUpload: () => void;
}

type LanguageMode = 'en' | 'hi' | 'both';
type FilterMode = 'all' | 'out_of_range' | 'within' | 'unclassified';

function renderStatusBadge(status: ClassificationStatus) {
  switch (status) {
    case 'Within Reference Range':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-300">
          <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" aria-hidden="true" />
          <span>Within Reference Range</span>
        </span>
      );
    case 'Below Reference Range':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-900 border border-amber-300">
          <ArrowDownCircle className="w-4 h-4 text-amber-700 shrink-0" aria-hidden="true" />
          <span>Below Reference Range</span>
        </span>
      );
    case 'Above Reference Range':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-900 border border-amber-300">
          <ArrowUpCircle className="w-4 h-4 text-amber-700 shrink-0" aria-hidden="true" />
          <span>Above Reference Range</span>
        </span>
      );
    case 'Unable to Classify':
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-800 border border-slate-300">
          <HelpCircle className="w-4 h-4 text-slate-600 shrink-0" aria-hidden="true" />
          <span>Unable to Classify</span>
        </span>
      );
  }
}

export const ExplanationView: React.FC<ExplanationViewProps> = ({
  report,
  onBackToReview,
  onStartNewUpload,
}) => {
  const [lang, setLang] = useState<LanguageMode>('both');
  const [filter, setFilter] = useState<FilterMode>('all');

  const filteredCards: ParameterExplanationCard[] = report.cards.filter((c) => {
    if (filter === 'within') return c.rule_based_status === 'Within Reference Range';
    if (filter === 'out_of_range')
      return (
        c.rule_based_status === 'Below Reference Range' ||
        c.rule_based_status === 'Above Reference Range'
      );
    if (filter === 'unclassified') return c.rule_based_status === 'Unable to Classify';
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Action & Language Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-700">
              Step 3 of 3 • Educational Report Summary (Not a Clinical Diagnosis)
            </span>
            {report.is_sample && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300">
                {report.sample_label || 'Sample Data — Not a Real Patient'}
              </span>
            )}
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
            Your Lab Report, Explained in Simple Words
          </h1>
          <p className="text-xs sm:text-sm text-slate-600">
            {report.disclaimer}
          </p>
        </div>

        {/* Language Toggle & Print Controls */}
        <div className="flex flex-wrap items-center gap-2.5 no-print">
          <div
            role="group"
            aria-label="Explanation Language Switcher"
            className="inline-flex items-center rounded-xl bg-slate-100 p-1 border border-slate-200"
          >
            <Languages className="w-4 h-4 text-teal-700 ml-2 mr-1" aria-hidden="true" />
            <button
              type="button"
              onClick={() => setLang('en')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                lang === 'en'
                  ? 'bg-white text-teal-900 shadow-sm'
                  : 'text-slate-700 hover:text-slate-900'
              }`}
            >
              Plain English
            </button>
            <button
              type="button"
              onClick={() => setLang('hi')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                lang === 'hi'
                  ? 'bg-white text-teal-900 shadow-sm'
                  : 'text-slate-700 hover:text-slate-900'
              }`}
            >
              Easy Hinglish
            </button>
            <button
              type="button"
              onClick={() => setLang('both')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                lang === 'both'
                  ? 'bg-white text-teal-900 shadow-sm'
                  : 'text-slate-700 hover:text-slate-900'
              }`}
            >
              Both (Bilingual)
            </button>
          </div>

          <button
            type="button"
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white text-slate-800 hover:bg-slate-100 border border-slate-300"
          >
            <Printer className="w-4 h-4 text-teal-700" aria-hidden="true" />
            <span>Print / Save PDF</span>
          </button>

          <button
            type="button"
            onClick={onBackToReview}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white text-slate-800 hover:bg-slate-100 border border-slate-300"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            <span>Edit Values</span>
          </button>

          <button
            type="button"
            onClick={onStartNewUpload}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-teal-700 text-white hover:bg-teal-800"
          >
            <RotateCcw className="w-4 h-4" aria-hidden="true" />
            <span>New Report</span>
          </button>
        </div>
      </div>

      {/* URGENT SYMPTOMS SAFETY ALERT (RED) */}
      {report.urgent_care_banner && (
        <div
          role="alert"
          className="p-5 rounded-2xl bg-red-50 border-2 border-red-600 text-red-950 flex items-start gap-3.5 shadow-sm"
        >
          <ShieldAlert className="w-7 h-7 text-red-700 shrink-0 mt-0.5" aria-hidden="true" />
          <div className="space-y-1">
            <h2 className="text-base font-extrabold text-red-900">
              Immediate Medical Attention Advised for Urgent Symptoms
            </h2>
            <p className="text-xs sm:text-sm text-red-900 font-medium leading-relaxed">
              {report.urgent_care_banner}
            </p>
          </div>
        </div>
      )}

      {/* CRITICAL VALUE ALERTS FROM REPORT (RED) */}
      {report.critical_value_alerts.length > 0 && (
        <div
          role="alert"
          className="p-5 rounded-2xl bg-red-50 border-2 border-red-600 text-red-950 space-y-2 shadow-sm"
        >
          <div className="flex items-center gap-2 font-extrabold text-red-900 text-base">
            <AlertTriangle className="w-6 h-6 text-red-700" aria-hidden="true" />
            <span>Laboratory Critical-Value Alert Preserved from Your Report</span>
          </div>
          <ul className="list-disc list-inside text-xs sm:text-sm text-red-900 font-medium space-y-1">
            {report.critical_value_alerts.map((alert, i) => (
              <li key={i}>{alert}</li>
            ))}
          </ul>
        </div>
      )}

      {/* AI / Curated Service Transparency Banner */}
      <div
        role="note"
        className="p-4 rounded-xl bg-teal-50/80 border border-teal-200 text-teal-950 text-xs sm:text-sm flex items-start gap-3"
      >
        <Sparkles className="w-5 h-5 text-teal-700 shrink-0 mt-0.5" aria-hidden="true" />
        <div className="space-y-0.5">
          <div className="font-bold">
            Explanation Engine Status:{' '}
            {report.ai_mode === 'live_gemini'
              ? 'Live Gemini AI + Curated Medical Reference'
              : 'Vetted Curated Medical Reference Library (Deterministic Local Fallback)'}
          </div>
          <div className="text-slate-700 text-xs">{report.ai_service_notice}</div>
        </div>
      </div>

      {/* FINAL REPORT SUMMARY COUNTS (No Disease Score or Verdict) */}
      <section aria-labelledby="summary-counts-heading" className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h2 id="summary-counts-heading" className="text-lg font-bold text-slate-900">
            Parameter Reference-Range Overview (Rule-Based Count)
          </h2>
          <span className="text-xs text-slate-500">
            Statuses are calculated deterministically from your lab’s printed reference ranges
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <button
            type="button"
            onClick={() => setFilter('all')}
            className={`p-4 rounded-2xl border text-left transition-all ${
              filter === 'all'
                ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                : 'bg-white text-slate-900 border-slate-200 hover:border-slate-400'
            }`}
          >
            <div className="text-xs font-semibold opacity-80">Total Verified</div>
            <div className="text-2xl sm:text-3xl font-extrabold mt-1">
              {report.summary_counts.total_verified}
            </div>
            <div className="text-[11px] mt-1 opacity-75">Click to view all</div>
          </button>

          <button
            type="button"
            onClick={() => setFilter('within')}
            className={`p-4 rounded-2xl border text-left transition-all ${
              filter === 'within'
                ? 'bg-emerald-700 text-white border-emerald-700 shadow-sm'
                : 'bg-emerald-50/70 text-emerald-950 border-emerald-200 hover:border-emerald-400'
            }`}
          >
            <div className="text-xs font-semibold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Within Range</span>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold mt-1">
              {report.summary_counts.within_range}
            </div>
            <div className="text-[11px] mt-1 opacity-80">Within lab limits</div>
          </button>

          <button
            type="button"
            onClick={() => setFilter('out_of_range')}
            className={`p-4 rounded-2xl border text-left transition-all ${
              filter === 'out_of_range'
                ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                : 'bg-amber-50/80 text-amber-950 border-amber-200 hover:border-amber-400'
            }`}
          >
            <div className="text-xs font-semibold flex items-center gap-1">
              <ArrowDownCircle className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Below Range</span>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold mt-1">
              {report.summary_counts.below_range}
            </div>
            <div className="text-[11px] mt-1 opacity-80">Below lower limit</div>
          </button>

          <button
            type="button"
            onClick={() => setFilter('out_of_range')}
            className={`p-4 rounded-2xl border text-left transition-all ${
              filter === 'out_of_range'
                ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                : 'bg-amber-50/80 text-amber-950 border-amber-200 hover:border-amber-400'
            }`}
          >
            <div className="text-xs font-semibold flex items-center gap-1">
              <ArrowUpCircle className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Above Range</span>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold mt-1">
              {report.summary_counts.above_range}
            </div>
            <div className="text-[11px] mt-1 opacity-80">Above upper limit</div>
          </button>

          <button
            type="button"
            onClick={() => setFilter('unclassified')}
            className={`p-4 rounded-2xl border text-left transition-all col-span-2 sm:col-span-1 ${
              filter === 'unclassified'
                ? 'bg-slate-700 text-white border-slate-700 shadow-sm'
                : 'bg-slate-100 text-slate-900 border-slate-300 hover:border-slate-400'
            }`}
          >
            <div className="text-xs font-semibold flex items-center gap-1">
              <HelpCircle className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Unable to Classify</span>
            </div>
            <div className="text-2xl sm:text-3xl font-extrabold mt-1">
              {report.summary_counts.unable_to_classify}
            </div>
            <div className="text-[11px] mt-1 opacity-80">Missing/ambiguous range</div>
          </button>
        </div>

        {/* Important Reference-Range Education Box */}
        <div className="p-4 rounded-xl bg-white border border-slate-200 text-xs sm:text-sm text-slate-700 space-y-1">
          {(lang === 'en' || lang === 'both') && (
            <p>
              <strong className="text-slate-900">How Reference Ranges Work:</strong>{' '}
              {report.range_education_note_en}
            </p>
          )}
          {(lang === 'hi' || lang === 'both') && (
            <p className="text-teal-900">
              <strong>Hinglish Note:</strong> {report.range_education_note_hi}
            </p>
          )}
        </div>
      </section>

      {/* INDIVIDUAL RESULT EXPLANATION CARDS */}
      <section aria-labelledby="cards-heading" className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 id="cards-heading" className="text-xl font-bold text-slate-900">
            Individual Parameter Explanations ({filteredCards.length})
          </h2>
          {filter !== 'all' && (
            <button
              type="button"
              onClick={() => setFilter('all')}
              className="text-xs font-semibold text-teal-700 hover:underline no-print"
            >
              Show All ({report.cards.length})
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 gap-6">
          {filteredCards.map((card) => (
            <article
              key={card.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5 print-break-inside-avoid"
            >
              {/* Card Top Row: Name, Status Badge, and Reported Values */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2.5">
                    <h3 className="text-lg sm:text-xl font-bold text-slate-900">
                      {card.test_name}
                    </h3>
                    {renderStatusBadge(card.rule_based_status)}
                    {card.user_edited && (
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-teal-50 text-teal-800 border border-teal-200">
                        User-Verified Edit
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{card.classification_reason}</p>
                </div>

                {/* Numerical Pill Box */}
                <div className="flex items-center gap-4 bg-slate-50 px-4 py-2.5 rounded-xl border border-slate-200/90 self-start md:self-auto">
                  <div>
                    <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold">
                      Your Result
                    </div>
                    <div className="text-lg font-extrabold text-slate-900 font-mono">
                      {card.original_result}{' '}
                      <span className="text-xs font-semibold text-slate-600">{card.unit}</span>
                    </div>
                    {card.user_edited &&
                      card.original_extracted_result &&
                      card.original_extracted_result !== card.original_result && (
                        <div className="text-[10px] text-slate-500">
                          OCR raw: {card.original_extracted_result}
                        </div>
                      )}
                  </div>

                  <div className="h-8 w-px bg-slate-200" aria-hidden="true" />

                  <div>
                    <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold">
                      Lab Reference Range
                    </div>
                    <div className="text-sm font-bold text-slate-800 font-mono">
                      {card.reference_range || 'Not provided'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Critical Alert Banner inside Card if applicable */}
              {card.is_critical_alert && (
                <div
                  role="alert"
                  className="p-3.5 rounded-xl bg-red-50 border border-red-500 text-red-900 text-xs sm:text-sm font-semibold flex items-start gap-2.5"
                >
                  <AlertTriangle className="w-5 h-5 text-red-700 shrink-0" aria-hidden="true" />
                  <span>
                    Critical Alert noted on report for {card.test_name}. Please contact your
                    ordering clinician or laboratory promptly.
                  </span>
                </div>
              )}

              {/* Bilingual Explanations Grid */}
              <div
                className={`grid grid-cols-1 ${
                  lang === 'both' ? 'lg:grid-cols-2' : ''
                } gap-4`}
              >
                {(lang === 'en' || lang === 'both') && (
                  <div className="p-4 rounded-xl bg-slate-50/90 border border-slate-200/80 space-y-3">
                    <div className="text-xs font-bold uppercase tracking-wider text-teal-800">
                      Plain English Explanation
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase">
                        What This Test Measures
                      </h4>
                      <p className="text-sm text-slate-700 mt-0.5 leading-relaxed">
                        {card.what_it_measures_en}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase">
                        What This Result Can & Cannot Tell You
                      </h4>
                      <p className="text-sm text-slate-700 mt-0.5 leading-relaxed">
                        {card.result_context_en}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase">
                        Factors That May Affect This Value
                      </h4>
                      <ul className="list-disc list-inside text-xs sm:text-sm text-slate-700 mt-1 space-y-1">
                        {card.factors_affecting_en.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {(lang === 'hi' || lang === 'both') && (
                  <div className="p-4 rounded-xl bg-teal-50/40 border border-teal-200/70 space-y-3">
                    <div className="text-xs font-bold uppercase tracking-wider text-teal-900">
                      Aasan Hinglish Samajh (Simple Hinglish)
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase">
                        Yeh Test Kya Maapta Hai
                      </h4>
                      <p className="text-sm text-slate-800 mt-0.5 leading-relaxed">
                        {card.what_it_measures_hi}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase">
                        Is Value Ka Kya Matlab Ho Sakta Hai
                      </h4>
                      <p className="text-sm text-slate-800 mt-0.5 leading-relaxed">
                        {card.result_context_hi}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 uppercase">
                        Kin Baaton Ka Is Value Par Asar Pad Sakta Hai
                      </h4>
                      <ul className="list-disc list-inside text-xs sm:text-sm text-slate-800 mt-1 space-y-1">
                        {card.factors_affecting_hi.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>

              {/* Suggested Question for Doctor & Source Attribution */}
              <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-start gap-2 text-slate-800 bg-sky-50/80 px-3.5 py-2.5 rounded-xl border border-sky-200/80">
                  <MessageSquare
                    className="w-4 h-4 text-sky-700 shrink-0 mt-0.5"
                    aria-hidden="true"
                  />
                  <div>
                    <strong className="text-sky-950">Suggested Question for Doctor: </strong>
                    {lang === 'hi' ? card.doctor_question_hi : card.doctor_question_en}
                    {lang === 'both' && (
                      <div className="text-slate-600 mt-0.5 italic">
                        Hinglish: “{card.doctor_question_hi}”
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-1.5 text-slate-500 shrink-0">
                  <BookOpen className="w-3.5 h-3.5 text-teal-700" aria-hidden="true" />
                  <span>{card.source_attribution}</span>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* QUESTIONS TO ASK YOUR DOCTOR SECTION */}
      <section
        aria-labelledby="doctor-questions-heading"
        className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-4 print-break-inside-avoid"
      >
        <div className="flex items-start gap-3">
          <Stethoscope className="w-6 h-6 text-teal-700 shrink-0 mt-0.5" aria-hidden="true" />
          <div>
            <h2 id="doctor-questions-heading" className="text-xl font-bold text-slate-900">
              Questions to Discuss with Your Doctor
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
              These neutral discussion prompts are designed to help you prepare for your medical
              consultation. They are educational prompts, not treatment recommendations.
            </p>
          </div>
        </div>

        <div
          className={`grid grid-cols-1 ${
            lang === 'both' ? 'md:grid-cols-2' : ''
          } gap-4 pt-2`}
        >
          {(lang === 'en' || lang === 'both') && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-teal-800">
                In English
              </h3>
              <ul className="space-y-2">
                {report.general_doctor_questions_en.map((q, idx) => (
                  <li
                    key={idx}
                    className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs sm:text-sm text-slate-800 font-medium"
                  >
                    “{q}”
                  </li>
                ))}
              </ul>
            </div>
          )}

          {(lang === 'hi' || lang === 'both') && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-teal-900">
                In Hinglish (Doctor Se Puchhne Ke Liye Sawaal)
              </h3>
              <ul className="space-y-2">
                {report.general_doctor_questions_hi.map((q, idx) => (
                  <li
                    key={idx}
                    className="p-3 rounded-xl bg-teal-50/50 border border-teal-200 text-xs sm:text-sm text-slate-800 font-medium"
                  >
                    “{q}”
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>

      {/* LIMITATIONS AND MEDICAL DISCLAIMER SECTION */}
      <section
        aria-labelledby="limitations-heading"
        className="bg-slate-100 rounded-2xl border border-slate-300 p-6 space-y-3 print-break-inside-avoid"
      >
        <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
          <Info className="w-5 h-5 text-teal-700" aria-hidden="true" />
          <h2 id="limitations-heading">Important Limitations & Medical Disclaimer</h2>
        </div>

        <p className="text-xs sm:text-sm font-bold text-slate-900">{report.disclaimer}</p>

        <ul className="list-disc list-inside space-y-1 text-xs sm:text-sm text-slate-700">
          {report.limitations.map((lim, idx) => (
            <li key={idx}>{lim}</li>
          ))}
        </ul>
      </section>
    </div>
  );
};
