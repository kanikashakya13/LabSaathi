import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  ArrowDown,
  ArrowLeft,
  ArrowUp,
  Check,
  CheckCircle2,
  Edit3,
  HelpCircle,
  RefreshCw,
  ShieldAlert,
  Trash2,
  User,
  Calendar,
  Layers,
} from 'lucide-react';
import {
  ClassificationStatus,
  ExtractedParameter,
  UploadAndExtractResponse,
} from '../types';

interface ReviewTableViewProps {
  extractionData: UploadAndExtractResponse;
  onBackToUpload: () => void;
  onGenerateExplanations: (payload: {
    parameters: ExtractedParameter[];
    patientSex: 'unspecified' | 'female' | 'male';
    patientAgeGroup: 'unspecified' | 'adult' | 'child' | 'senior';
    patientAge: string | null;
    reportDate: string | null;
    userConsentedAi: boolean;
    urgentSymptomsReported: boolean;
  }) => Promise<void>;
  generating: boolean;
  errorMessage: string | null;
}

export const ReviewTableView: React.FC<ReviewTableViewProps> = ({
  extractionData,
  onBackToUpload,
  onGenerateExplanations,
  generating,
  errorMessage,
}) => {
  const [params, setParams] = useState<ExtractedParameter[]>(extractionData.parameters);
  const [editingId, setEditingId] = useState<string | null>(null);

  // Initialize demographics from automatic report extraction
  const initialSex: 'unspecified' | 'female' | 'male' =
    extractionData.extracted_patient_sex === 'female'
      ? 'female'
      : extractionData.extracted_patient_sex === 'male'
      ? 'male'
      : 'unspecified';

  const [patientSex, setPatientSex] = useState<'unspecified' | 'female' | 'male'>(initialSex);
  const [patientAge, setPatientAge] = useState<string>(
    extractionData.extracted_patient_age || ''
  );
  const [patientAgeGroup, setPatientAgeGroup] = useState<
    'unspecified' | 'adult' | 'child' | 'senior'
  >('adult');
  const [reportDate, setReportDate] = useState<string>(
    extractionData.extracted_report_date || ''
  );

  const [userConsentedAi, setUserConsentedAi] = useState<boolean>(true);
  const [urgentSymptomsReported, setUrgentSymptomsReported] = useState<boolean>(false);

  // Synchronize state if a new extraction response is passed
  useEffect(() => {
    setParams(extractionData.parameters);
    if (extractionData.extracted_patient_sex) {
      setPatientSex(
        extractionData.extracted_patient_sex === 'female' ? 'female' : 'male'
      );
    }
    if (extractionData.extracted_patient_age) {
      setPatientAge(extractionData.extracted_patient_age);
    }
    if (extractionData.extracted_report_date) {
      setReportDate(extractionData.extracted_report_date);
    }
  }, [extractionData]);

  // Dynamically reclassify a parameter whenever user edits values or changes demographic context
  const reclassifyLocal = (
    p: ExtractedParameter,
    sex: 'unspecified' | 'female' | 'male',
    ageGrp: 'unspecified' | 'adult' | 'child' | 'senior'
  ): { status: ClassificationStatus; reason: string } => {
    const resStr = (p.original_result || '').trim();
    const rngStr = (p.reference_range || '').trim();

    if (!rngStr || rngStr.toLowerCase() === 'not provided') {
      return {
        status: 'Unable to Classify',
        reason: 'Laboratory reference range was not provided on the report.',
      };
    }

    const val = parseFloat(resStr.replace(/^[<>≤≥]=?\s*/, ''));
    if (isNaN(val)) {
      return {
        status: 'Unable to Classify',
        reason: 'Measured result is non-numeric or qualitative.',
      };
    }

    // Check sex-specific range e.g. "Male: 0.7 - 1.3 | Female: 0.6 - 1.1"
    const sexMatch = rngStr.match(/Male\s*:\s*([^|]+)\s*\|\s*Female\s*:\s*([^|]+)/i);
    let effectiveRng = rngStr;
    if (sexMatch) {
      if (sex === 'male') {
        effectiveRng = sexMatch[1].trim();
      } else if (sex === 'female') {
        effectiveRng = sexMatch[2].trim();
      } else {
        return {
          status: 'Unable to Classify',
          reason:
            'Reference range is sex-specific. Biological sex is unspecified, retaining printed ranges.',
        };
      }
    }

    // Interval: Low - High
    const intMatch = effectiveRng.match(/([+-]?\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*([+-]?\d+(?:\.\d+)?)/i);
    if (intMatch) {
      const low = parseFloat(intMatch[1]);
      const high = parseFloat(intMatch[2]);
      if (val < low) {
        return {
          status: 'Below Reference Range',
          reason: `Result (${val}) is below lower limit (${low}).`,
        };
      }
      if (val > high) {
        return {
          status: 'Above Reference Range',
          reason: `Result (${val}) is above upper limit (${high}).`,
        };
      }
      return {
        status: 'Within Reference Range',
        reason: `Result (${val}) is within laboratory reference range (${low} – ${high}).`,
      };
    }

    // Inequality < Bound
    const lessMatch = effectiveRng.match(/^[<≤]=?\s*([+-]?\d+(?:\.\d+)?)/i);
    if (lessMatch) {
      const bound = parseFloat(lessMatch[1]);
      if (val < bound) {
        return {
          status: 'Within Reference Range',
          reason: `Result (${val}) satisfies desired threshold (< ${bound}).`,
        };
      }
      return {
        status: 'Above Reference Range',
        reason: `Result (${val}) exceeds desired upper threshold (${bound}).`,
      };
    }

    // Inequality > Bound
    const greaterMatch = effectiveRng.match(/^[>≥]=?\s*([+-]?\d+(?:\.\d+)?)/i);
    if (greaterMatch) {
      const bound = parseFloat(greaterMatch[1]);
      if (val > bound) {
        return {
          status: 'Within Reference Range',
          reason: `Result (${val}) satisfies desired threshold (> ${bound}).`,
        };
      }
      return {
        status: 'Below Reference Range',
        reason: `Result (${val}) is below desired threshold (${bound}).`,
      };
    }

    return {
      status: p.rule_based_status || 'Unable to Classify',
      reason: p.classification_reason || 'Retained printed laboratory classification.',
    };
  };

  const handleFieldChange = (
    id: string,
    field: 'test_name' | 'original_result' | 'unit' | 'reference_range',
    value: string
  ) => {
    setParams((prev) =>
      prev.map((p) => {
        if (p.id !== id) return p;
        const updated = {
          ...p,
          [field]: value,
          user_edited: true,
          verification_status: 'User Corrected' as const,
          user_confirmed: true,
        };
        const recls = reclassifyLocal(updated, patientSex, patientAgeGroup);
        updated.rule_based_status = recls.status;
        updated.classification_reason = recls.reason;
        return updated;
      })
    );
  };

  const handleSexChange = (newSex: 'unspecified' | 'female' | 'male') => {
    setPatientSex(newSex);
    setParams((prev) =>
      prev.map((p) => {
        const recls = reclassifyLocal(p, newSex, patientAgeGroup);
        return {
          ...p,
          rule_based_status: recls.status,
          classification_reason: recls.reason,
        };
      })
    );
  };

  const handleConfirmRow = (id: string) => {
    setParams((prev) =>
      prev.map((p) =>
        p.id === id
          ? {
              ...p,
              user_confirmed: true,
              verification_status: p.user_edited ? 'User Corrected' : 'Verified',
            }
          : p
      )
    );
  };

  const handleConfirmAll = () => {
    setParams((prev) =>
      prev.map((p) => ({
        ...p,
        user_confirmed: true,
        verification_status: p.user_edited ? 'User Corrected' : 'Verified',
      }))
    );
  };

  const handleRemoveRow = (id: string) => {
    setParams((prev) => prev.filter((p) => p.id !== id));
  };

  // Four explicit summary counters per Requirement 7
  const totalExtracted = params.length;
  const verifiedCount = params.filter((p) => p.user_confirmed).length;
  const flaggedCount = params.filter((p) => !p.user_confirmed).length;
  const unprocessedCount = params.filter(
    (p) => p.rule_based_status === 'Unable to Classify'
  ).length;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onGenerateExplanations({
      parameters: params,
      patientSex,
      patientAgeGroup,
      patientAge: patientAge.trim() || null,
      reportDate: reportDate.trim() || null,
      userConsentedAi,
      urgentSymptomsReported,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6"
    >
      {/* Top Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-700">
              Step 2 of 3 • Review & Verify Extracted Values
            </span>
            {extractionData.is_sample && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300">
                {extractionData.sample_label || 'Sample Data — Not a Real Patient'}
              </span>
            )}
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
            Verify Your Extracted Report Values
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">
            Extracted from <strong>{extractionData.file_name}</strong> via{' '}
            <code className="text-teal-900 bg-teal-50 px-1 py-0.5 rounded">
              {extractionData.ocr_engine_used}
            </code>
            . Please verify any uncertain rows before generating educational explanations.
          </p>
        </div>

        <button
          type="button"
          onClick={onBackToUpload}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-300 self-start"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          <span>Upload Different File</span>
        </button>
      </div>

      {/* Four Summary Counters Bar per Requirement 7 */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-100 text-teal-800 flex items-center justify-center font-bold">
            <Layers className="w-5 h-5" aria-hidden="true" />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Extracted
            </div>
            <div className="text-xl sm:text-2xl font-extrabold text-slate-900 font-mono">
              {totalExtracted}
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
            <CheckCircle2 className="w-5 h-5" aria-hidden="true" />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Verified
            </div>
            <div className="text-xl sm:text-2xl font-extrabold text-emerald-800 font-mono">
              {verifiedCount}
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-900 flex items-center justify-center font-bold">
            <AlertTriangle className="w-5 h-5" aria-hidden="true" />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Flagged (Review)
            </div>
            <div className="text-xl sm:text-2xl font-extrabold text-amber-900 font-mono">
              {flaggedCount}
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold">
            <HelpCircle className="w-5 h-5" aria-hidden="true" />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Unprocessed
            </div>
            <div className="text-xl sm:text-2xl font-extrabold text-slate-700 font-mono">
              {unprocessedCount}
            </div>
          </div>
        </div>
      </div>

      {/* Extracted Patient Demographics & Report Date Bar per Requirement 4 */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <User className="w-4 h-4 text-teal-700" aria-hidden="true" />
              <span>Extracted Patient Demographics & Report Context</span>
            </h2>
            <p className="text-xs text-slate-600 mt-0.5">
              Automatically read from report headers. LabSaathi never guesses age or infers
              biological sex from patient names.
            </p>
          </div>

          {extractionData.requires_demographic_input && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300 self-start">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-800" aria-hidden="true" />
              <span>Demographic Input Needed for Sex/Age Range</span>
            </span>
          )}
        </div>

        {extractionData.requires_demographic_input && extractionData.demographic_prompt_reason && (
          <div
            role="note"
            className="p-3.5 rounded-xl bg-amber-50 border border-amber-300 text-amber-950 text-xs sm:text-sm flex items-start gap-2.5"
          >
            <AlertCircle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" aria-hidden="true" />
            <div>
              <strong>Demographic Guidance:</strong> {extractionData.demographic_prompt_reason}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label
              htmlFor="patient-age-input"
              className="block text-xs font-semibold text-slate-700 mb-1"
            >
              Patient Age (Extracted: {extractionData.extracted_patient_age || 'Not on Report'})
            </label>
            <input
              id="patient-age-input"
              type="text"
              value={patientAge}
              onChange={(e) => setPatientAge(e.target.value)}
              placeholder="e.g. 38 Years or leave blank"
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-teal-600 focus:outline-none"
            />
          </div>

          <div>
            <label
              htmlFor="patient-sex-select"
              className="block text-xs font-semibold text-slate-700 mb-1"
            >
              Biological Sex (For Sex-Specific Reference Ranges)
            </label>
            <select
              id="patient-sex-select"
              value={patientSex}
              onChange={(e) =>
                handleSexChange(e.target.value as 'unspecified' | 'female' | 'male')
              }
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-teal-600 focus:outline-none"
            >
              <option value="unspecified">Unspecified (Retain Combined Range)</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </div>

          <div>
            <label
              htmlFor="report-date-input"
              className="block text-xs font-semibold text-slate-700 mb-1"
            >
              Report Date (Extracted: {extractionData.extracted_report_date || 'Not on Report'})
            </label>
            <div className="relative">
              <input
                id="report-date-input"
                type="text"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
                placeholder="e.g. 12/10/2026"
                className="w-full rounded-xl border border-slate-300 bg-white pl-9 pr-3 py-2 text-sm text-slate-900 focus:border-teal-600 focus:outline-none"
              />
              <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-3" aria-hidden="true" />
            </div>
          </div>
        </div>
      </div>

      {/* Critical Value Alerts Banner */}
      {extractionData.critical_value_alerts.length > 0 && (
        <div
          role="alert"
          className="p-4 rounded-xl bg-red-50 border-2 border-red-600 text-red-950 text-xs sm:text-sm space-y-1"
        >
          <div className="font-bold flex items-center gap-2 text-red-900">
            <ShieldAlert className="w-5 h-5 text-red-700" aria-hidden="true" />
            <span>Laboratory Critical-Value Alert Detected on Report:</span>
          </div>
          <ul className="list-disc list-inside pl-6 text-red-900">
            {extractionData.critical_value_alerts.map((alert, i) => (
              <li key={i}>{alert}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Extracted Data Review Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 sm:px-6 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Extracted Parameters ({params.length})
            </h2>
            <p className="text-xs text-slate-600">
              Click <strong>Edit</strong> on any row to correct OCR errors. The rule-based result
              status is computed deterministically in Python against the laboratory reference range.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {flaggedCount > 0 && (
              <button
                type="button"
                onClick={handleConfirmAll}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-amber-100 text-amber-950 hover:bg-amber-200 border border-amber-300 transition-colors"
              >
                <Check className="w-4 h-4" aria-hidden="true" />
                <span>Confirm All Flagged Rows ({flaggedCount})</span>
              </button>
            )}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <caption className="sr-only">
              Extracted laboratory test parameters with original results, units, reference ranges,
              verification status, and rule-based classification status.
            </caption>
            <thead>
              <tr className="border-b border-slate-200 bg-slate-100/80 text-xs font-bold uppercase tracking-wider text-slate-700">
                <th scope="col" className="py-3.5 px-4">
                  Test Name
                </th>
                <th scope="col" className="py-3.5 px-4">
                  Original Result
                </th>
                <th scope="col" className="py-3.5 px-4">
                  Unit
                </th>
                <th scope="col" className="py-3.5 px-4">
                  Lab Reference Range
                </th>
                <th scope="col" className="py-3.5 px-4">
                  Verification Status
                </th>
                <th scope="col" className="py-3.5 px-4">
                  Rule-Based Status
                </th>
                <th scope="col" className="py-3.5 px-4 text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-sm">
              {params.map((row) => {
                const isEditing = editingId === row.id;
                const needsConfirm = !row.user_confirmed;

                return (
                  <tr
                    key={row.id}
                    className={
                      needsConfirm
                        ? 'bg-amber-50/60 hover:bg-amber-50'
                        : row.user_edited
                        ? 'bg-teal-50/30 hover:bg-teal-50/50'
                        : 'hover:bg-slate-50'
                    }
                  >
                    {/* Test Name */}
                    <td className="py-3.5 px-4 align-top">
                      {isEditing ? (
                        <input
                          type="text"
                          aria-label={`Test name for ${row.test_name}`}
                          value={row.test_name}
                          onChange={(e) =>
                            handleFieldChange(row.id, 'test_name', e.target.value)
                          }
                          className="w-full rounded-lg border border-teal-500 px-2.5 py-1.5 text-sm font-medium text-slate-900 bg-white"
                        />
                      ) : (
                        <div className="font-semibold text-slate-900">{row.test_name}</div>
                      )}
                      {row.ocr_warnings.length > 0 && (
                        <div className="mt-1.5 space-y-1">
                          {row.ocr_warnings.map((w, idx) => (
                            <div
                              key={idx}
                              className="text-xs text-amber-900 bg-amber-100/80 border border-amber-300 rounded-md px-2 py-1 flex items-start gap-1.5"
                            >
                              <AlertTriangle
                                className="w-3.5 h-3.5 text-amber-800 shrink-0 mt-0.5"
                                aria-hidden="true"
                              />
                              <span>{w}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </td>

                    {/* Original Result */}
                    <td className="py-3.5 px-4 align-top">
                      {isEditing ? (
                        <input
                          type="text"
                          aria-label={`Original result for ${row.test_name}`}
                          value={row.original_result}
                          onChange={(e) =>
                            handleFieldChange(row.id, 'original_result', e.target.value)
                          }
                          className="w-28 rounded-lg border border-teal-500 px-2.5 py-1.5 text-sm font-bold text-slate-900 bg-white"
                        />
                      ) : (
                        <span className="font-bold text-slate-900 font-mono text-base">
                          {row.original_result}
                        </span>
                      )}
                      {row.user_edited &&
                        row.original_extracted_result &&
                        row.original_extracted_result !== row.original_result && (
                          <div className="text-[11px] text-slate-500 mt-1">
                            Originally extracted:{' '}
                            <code className="bg-slate-100 px-1 rounded">
                              {row.original_extracted_result}
                            </code>
                          </div>
                        )}
                    </td>

                    {/* Unit */}
                    <td className="py-3.5 px-4 align-top">
                      {isEditing ? (
                        <input
                          type="text"
                          aria-label={`Unit for ${row.test_name}`}
                          value={row.unit}
                          onChange={(e) => handleFieldChange(row.id, 'unit', e.target.value)}
                          className="w-24 rounded-lg border border-teal-500 px-2.5 py-1.5 text-sm text-slate-900 bg-white"
                        />
                      ) : (
                        <span className="text-slate-700 font-medium">
                          {row.unit || <em className="text-slate-400">None</em>}
                        </span>
                      )}
                    </td>

                    {/* Lab Reference Range */}
                    <td className="py-3.5 px-4 align-top">
                      {isEditing ? (
                        <input
                          type="text"
                          aria-label={`Reference range for ${row.test_name}`}
                          value={row.reference_range}
                          placeholder="e.g. 12.0 - 15.5 or Leave blank"
                          onChange={(e) =>
                            handleFieldChange(row.id, 'reference_range', e.target.value)
                          }
                          className="w-full min-w-[140px] rounded-lg border border-teal-500 px-2.5 py-1.5 text-sm text-slate-900 bg-white"
                        />
                      ) : row.reference_range ? (
                        <span className="font-mono text-xs sm:text-sm text-slate-800 bg-slate-100 px-2 py-1 rounded">
                          {row.reference_range}
                        </span>
                      ) : (
                        <span className="text-xs italic text-slate-500">
                          Not provided on report (Unable to Classify)
                        </span>
                      )}
                    </td>

                    {/* Verification Status */}
                    <td className="py-3.5 px-4 align-top">
                      {row.user_edited ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-teal-100 text-teal-900 border border-teal-300">
                          <Edit3 className="w-3.5 h-3.5 text-teal-800" aria-hidden="true" />
                          User Corrected
                        </span>
                      ) : row.user_confirmed ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                          <CheckCircle2
                            className="w-3.5 h-3.5 text-emerald-700"
                            aria-hidden="true"
                          />
                          Verified ({Math.round(row.confidence * 100)}%)
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300">
                          <AlertTriangle
                            className="w-3.5 h-3.5 text-amber-800"
                            aria-hidden="true"
                          />
                          Needs Review ({Math.round(row.confidence * 100)}%)
                        </span>
                      )}
                    </td>

                    {/* Rule-Based Result Status Column per Requirement 7 */}
                    <td className="py-3.5 px-4 align-top">
                      {row.rule_based_status === 'Within Reference Range' && (
                        <div>
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-300">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" aria-hidden="true" />
                            Within Range
                          </span>
                        </div>
                      )}
                      {row.rule_based_status === 'Below Reference Range' && (
                        <div>
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-400">
                            <ArrowDown className="w-3.5 h-3.5 text-amber-800" aria-hidden="true" />
                            Below Range
                          </span>
                        </div>
                      )}
                      {row.rule_based_status === 'Above Reference Range' && (
                        <div>
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-400">
                            <ArrowUp className="w-3.5 h-3.5 text-amber-800" aria-hidden="true" />
                            Above Range
                          </span>
                        </div>
                      )}
                      {row.rule_based_status === 'Unable to Classify' && (
                        <div>
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-300">
                            <HelpCircle className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
                            Unable to Classify
                          </span>
                        </div>
                      )}
                      {row.classification_reason && (
                        <div className="text-[11px] text-slate-500 mt-1 max-w-[200px] leading-tight">
                          {row.classification_reason}
                        </div>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 align-top text-right whitespace-nowrap space-x-1.5">
                      {needsConfirm && (
                        <button
                          type="button"
                          onClick={() => handleConfirmRow(row.id)}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-bold bg-amber-600 text-white hover:bg-amber-700 shadow-sm"
                        >
                          <Check className="w-3.5 h-3.5" aria-hidden="true" />
                          <span>Confirm</span>
                        </button>
                      )}

                      <button
                        type="button"
                        onClick={() => setEditingId(isEditing ? null : row.id)}
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-300"
                      >
                        <Edit3 className="w-3.5 h-3.5" aria-hidden="true" />
                        <span>{isEditing ? 'Done' : 'Edit'}</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleRemoveRow(row.id)}
                        aria-label={`Remove ${row.test_name}`}
                        className="inline-flex items-center p-1.5 rounded-lg text-slate-500 hover:text-red-700 hover:bg-red-50 border border-transparent"
                      >
                        <Trash2 className="w-4 h-4" aria-hidden="true" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Consent & Urgent Symptom Check */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label className="flex items-start gap-3 p-4 rounded-xl bg-white border border-slate-200 cursor-pointer hover:border-teal-500">
          <input
            type="checkbox"
            checked={userConsentedAi}
            onChange={(e) => setUserConsentedAi(e.target.checked)}
            className="mt-1 h-4 w-4 rounded border-slate-300 text-teal-700"
          />
          <div className="text-xs sm:text-sm">
            <span className="font-semibold text-slate-900 block">
              Consent to AI Educational Simplification (Zero-Retention)
            </span>
            <span className="text-slate-600 text-xs">
              Allow verified test names, values, and ranges (without personal identifiers) to be
              simplified by Gemini AI with <code>store=False</code>. Uncheck to use only the local
              Curated Medical Reference Library.
            </span>
          </div>
        </label>

        <label className="flex items-start gap-3 p-4 rounded-xl bg-white border border-slate-200 cursor-pointer hover:border-red-400">
          <input
            type="checkbox"
            checked={urgentSymptomsReported}
            onChange={(e) => setUrgentSymptomsReported(e.target.checked)}
            className="mt-1 h-4 w-4 rounded border-slate-300 text-red-700"
          />
          <div className="text-xs sm:text-sm">
            <span className="font-semibold text-slate-900 block">
              Are you currently experiencing severe or urgent physical symptoms?
            </span>
            <span className="text-slate-600 text-xs">
              Check this if you have chest pain, difficulty breathing, fainting, severe bleeding, or
              high fever with confusion (displays urgent care guidance).
            </span>
          </div>
        </label>
      </div>

      {/* Error message if user tries to proceed with unconfirmed or garbled values */}
      {errorMessage && (
        <div
          role="alert"
          className="p-4 rounded-xl bg-red-50 border-2 border-red-600 text-red-900 text-sm font-medium flex items-start gap-3"
        >
          <AlertTriangle className="w-5 h-5 text-red-700 shrink-0 mt-0.5" aria-hidden="true" />
          <div>{errorMessage}</div>
        </div>
      )}

      {/* Submit Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
        <p className="text-xs text-slate-600 max-w-xl">
          By clicking <strong>Generate Simple Explanations</strong>, you confirm that you have
          checked the values above against your original laboratory report.
        </p>

        <button
          type="submit"
          disabled={generating || params.length === 0}
          className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl text-base font-bold bg-teal-700 text-white hover:bg-teal-800 shadow-md transition-all disabled:opacity-60"
        >
          {generating ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" aria-hidden="true" />
              <span>Generating Educational Explanations...</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-5 h-5" aria-hidden="true" />
              <span>
                {flaggedCount > 0
                  ? `Confirm ${flaggedCount} Flagged Row(s) First`
                  : 'Generate Simple Explanations'}
              </span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};
