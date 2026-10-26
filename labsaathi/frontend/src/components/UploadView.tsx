import React, { useRef, useState } from 'react';
import {
  AlertTriangle,
  Camera,
  CheckCircle2,
  FileText,
  FlaskConical,
  Image as ImageIcon,
  RefreshCw,
  Sun,
  Trash2,
  Upload,
  XCircle,
} from 'lucide-react';
import { SampleScenario, UploadAndExtractResponse } from '../types';

interface UploadViewProps {
  onUploadFile: (file: File) => Promise<void>;
  onTrySampleReport: () => Promise<void>;
  onRunTestScenario: (scenarioId: string) => Promise<void>;
  uploading: boolean;
  lastUploadResult: UploadAndExtractResponse | null;
  onClearError: () => void;
  scenarios: SampleScenario[];
  maxFileSizeMb: number;
}

const REQUIRED_UPLOAD_WARNING =
  'IMPORTANT: Please upload a clear and readable lab report. Ensure all test names, values, units, and reference ranges are visible. Blurry or unreadable images will not be accepted. Please click the photo again clearly.';

export const UploadView: React.FC<UploadViewProps> = ({
  onUploadFile,
  onTrySampleReport,
  onRunTestScenario,
  uploading,
  lastUploadResult,
  onClearError,
  scenarios,
  maxFileSizeMb,
}) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const cameraInputRef = useRef<HTMLInputElement | null>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [clientError, setClientError] = useState<string | null>(null);

  const handleFileChosen = (file: File | undefined | null) => {
    if (!file) return;
    setClientError(null);
    onClearError();

    const ext = file.name.split('.').pop()?.toLowerCase() || '';
    if (!['jpg', 'jpeg', 'png', 'pdf'].includes(ext)) {
      setClientError(
        'Unsupported file type. Please choose a JPG, JPEG, PNG, or PDF laboratory report.'
      );
      return;
    }

    if (file.size > maxFileSizeMb * 1024 * 1024) {
      setClientError(
        `File size (${(file.size / (1024 * 1024)).toFixed(2)} MB) exceeds the ${maxFileSizeMb} MB limit.`
      );
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(file);
    if (file.type.startsWith('image/')) {
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      setPreviewUrl(null);
    }

    // Automatically start OCR & quality validation as soon as the user selects or drops a valid file
    void onUploadFile(file);
  };

  const handleRemoveFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setClientError(null);
    onClearError();
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChosen(e.dataTransfer.files[0]);
    }
  };

  const handleRetryFile = async () => {
    if (!selectedFile) {
      fileInputRef.current?.click();
      return;
    }
    await onUploadFile(selectedFile);
  };

  const rejectedResult =
    lastUploadResult && (!lastUploadResult.quality_passed || lastUploadResult.parameters.length === 0)
      ? lastUploadResult
      : null;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700">
            Step 1 of 3 • Automatic Upload, Quality Validation & OCR Extraction
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
            Upload Your Laboratory Report
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Supported formats: <strong>JPG, JPEG, PNG, PDF</strong> • Max size:{' '}
            <strong>{maxFileSizeMb} MB</strong> (up to 10 pages per PDF). Processing starts
            automatically on upload.
          </p>
        </div>

        <button
          type="button"
          onClick={onTrySampleReport}
          disabled={uploading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-teal-50 text-teal-900 hover:bg-teal-100 border border-teal-200 transition-colors self-start"
        >
          <FileText className="w-4 h-4 text-teal-700" aria-hidden="true" />
          <span>Try Sample Report (Synthetic Data)</span>
        </button>
      </div>

      {/* Upload Dropzone Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setDragActive(true);
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setDragActive(false);
          }}
          onDrop={handleDrop}
          className={`rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
            dragActive
              ? 'border-teal-600 bg-teal-50/70'
              : 'border-slate-300 hover:border-teal-600 bg-slate-50/60'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            id="report-file-input"
            accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf"
            onChange={(e) => handleFileChosen(e.target.files?.[0])}
            className="sr-only"
          />
          <input
            ref={cameraInputRef}
            type="file"
            id="report-camera-input"
            accept="image/jpeg,image/png"
            capture="environment"
            onChange={(e) => handleFileChosen(e.target.files?.[0])}
            className="sr-only"
          />

          <div className="w-14 h-14 rounded-2xl bg-teal-100 text-teal-800 flex items-center justify-center mx-auto mb-4">
            {uploading ? (
              <RefreshCw className="w-7 h-7 animate-spin" aria-hidden="true" />
            ) : (
              <Upload className="w-7 h-7" aria-hidden="true" />
            )}
          </div>

          <h2 className="text-lg font-bold text-slate-900">
            {uploading
              ? 'Validating Image Quality, Running OCR & Extracting Parameters...'
              : 'Drag and drop your lab report here, or choose a file'}
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-xl mx-auto">
            Supports clear photos (JPG, JPEG, PNG) or digital/scanned PDF reports. Extraction and
            rule-based classification begin automatically.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 mt-5">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-teal-700 text-white hover:bg-teal-800 shadow-sm transition-colors disabled:opacity-60"
            >
              <Upload className="w-4 h-4" aria-hidden="true" />
              <span>Select Report File</span>
            </button>

            <button
              type="button"
              onClick={() => cameraInputRef.current?.click()}
              disabled={uploading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-white text-slate-800 hover:bg-slate-100 border border-slate-300 transition-colors disabled:opacity-60"
            >
              <Camera className="w-4 h-4 text-teal-700" aria-hidden="true" />
              <span>Capture with Camera</span>
            </button>
          </div>
        </div>

        {/* MANDATORY RED UPLOAD WARNING DIRECTLY BELOW UPLOAD AREA */}
        <div
          role="note"
          aria-label="Important Upload Readability Warning"
          className="p-4 rounded-xl bg-red-50 border-2 border-red-600 text-red-900 flex items-start gap-3 shadow-sm"
        >
          <AlertTriangle className="w-6 h-6 text-red-700 shrink-0 mt-0.5" aria-hidden="true" />
          <p className="text-xs sm:text-sm font-bold leading-relaxed text-red-800">
            {REQUIRED_UPLOAD_WARNING}
          </p>
        </div>

        {/* Brief Readability Checklist */}
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-1.5">
            <Sun className="w-4 h-4 text-teal-700" aria-hidden="true" />
            Quick Checklist Before Uploading
          </h3>
          <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5 text-xs text-slate-700 font-medium">
            {[
              'Good lighting (natural or bright room light)',
              'Hold the camera steady with both hands',
              'Capture the entire report page & margins',
              'Avoid shadows and camera flash glare',
              'Keep all numbers & decimal points in focus',
            ].map((item, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 bg-white p-2.5 rounded-lg border border-slate-200/80"
              >
                <CheckCircle2
                  className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5"
                  aria-hidden="true"
                />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Selected File Preview & Controls */}
        {selectedFile && (
          <div className="p-4 rounded-xl bg-teal-50/60 border border-teal-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt={`Preview of ${selectedFile.name}`}
                  className="w-16 h-20 object-cover rounded-lg border border-slate-300 bg-white"
                />
              ) : (
                <div className="w-14 h-16 rounded-lg bg-white border border-slate-300 flex items-center justify-center text-teal-700">
                  {selectedFile.name.toLowerCase().endsWith('.pdf') ? (
                    <FileText className="w-7 h-7" aria-hidden="true" />
                  ) : (
                    <ImageIcon className="w-7 h-7" aria-hidden="true" />
                  )}
                </div>
              )}

              <div>
                <div className="text-sm font-bold text-slate-900 break-all">
                  {selectedFile.name}
                </div>
                <div className="text-xs text-slate-600 mt-0.5">
                  Size: {(selectedFile.size / 1024).toFixed(1)} KB • Type:{' '}
                  {selectedFile.type || 'Document'}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto justify-end">
              <button
                type="button"
                onClick={handleRemoveFile}
                disabled={uploading}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-300"
              >
                <Trash2 className="w-3.5 h-3.5 text-slate-600" aria-hidden="true" />
                <span>Remove</span>
              </button>

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-300"
              >
                <Upload className="w-3.5 h-3.5 text-slate-600" aria-hidden="true" />
                <span>Upload Another Report</span>
              </button>

              <button
                type="button"
                onClick={handleRetryFile}
                disabled={uploading}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-teal-700 text-white hover:bg-teal-800 shadow-sm disabled:opacity-60"
              >
                {uploading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" aria-hidden="true" />
                    <span>Extracting Report Parameters...</span>
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4" aria-hidden="true" />
                    <span>Retry Extraction</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Client-side format/size validation error */}
        {clientError && (
          <div
            role="alert"
            className="p-4 rounded-xl bg-red-50 border border-red-300 text-red-900 flex items-start gap-3 text-sm"
          >
            <XCircle className="w-5 h-5 text-red-700 shrink-0 mt-0.5" aria-hidden="true" />
            <div>{clientError}</div>
          </div>
        )}

        {/* MANDATORY RED ERROR BANNER WHEN OPENCV / PDF QUALITY OR EXTRACTION FAILS */}
        {rejectedResult && (
          <div
            role="alert"
            aria-live="assertive"
            className="p-6 rounded-2xl bg-red-50 border-2 border-red-600 text-red-950 space-y-4 shadow-md"
          >
            <div className="flex items-start gap-3">
              <XCircle className="w-7 h-7 text-red-700 shrink-0 mt-0.5" aria-hidden="true" />
              <div className="space-y-1">
                <h3 className="text-base sm:text-lg font-extrabold text-red-900">
                  {rejectedResult.quality_result.error_banner ||
                    "IMAGE IS BLURRY OR UNREADABLE. We couldn't clearly read your lab report. Please retake the photo in good lighting, keep your phone steady, and click again clearly."}
                </h3>
                <p className="text-xs sm:text-sm text-red-800 font-medium">
                  File: <strong>{rejectedResult.file_name}</strong> — Analysis was stopped so
                  unreadable or missing values are never guessed or silently ignored.
                </p>
              </div>
            </div>

            {/* Specific Detected Issues */}
            {rejectedResult.quality_result.issues.length > 0 && (
              <div className="bg-white/90 rounded-xl p-4 border border-red-200 space-y-2">
                <div className="text-xs font-bold uppercase tracking-wider text-red-900">
                  Reason Extraction Stopped:
                </div>
                <ul className="list-disc list-inside space-y-1 text-xs sm:text-sm text-red-900 font-medium">
                  {rejectedResult.quality_result.issues.map((issue, idx) => (
                    <li key={idx}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* OpenCV Telemetry Metrics if available */}
            {rejectedResult.quality_result.metrics && (
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs bg-white/80 p-3 rounded-xl border border-red-200">
                <div>
                  <span className="text-slate-500 block">Sharpness (Laplacian)</span>
                  <strong className="text-slate-900">
                    {rejectedResult.quality_result.metrics.laplacian_variance}
                  </strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Edge Energy</span>
                  <strong className="text-slate-900">
                    {rejectedResult.quality_result.metrics.tenengrad_score}
                  </strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Brightness (0–255)</span>
                  <strong className="text-slate-900">
                    {rejectedResult.quality_result.metrics.brightness_mean}
                  </strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Resolution</span>
                  <strong className="text-slate-900">
                    {rejectedResult.quality_result.metrics.width}×
                    {rejectedResult.quality_result.metrics.height}px
                  </strong>
                </div>
                <div>
                  <span className="text-slate-500 block">Skew Angle</span>
                  <strong className="text-slate-900">
                    {rejectedResult.quality_result.metrics.skew_degrees}°
                  </strong>
                </div>
              </div>
            )}

            {/* Required Retry & Upload Another Action Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <button
                type="button"
                onClick={handleRetryFile}
                disabled={uploading}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-red-700 text-white hover:bg-red-800 shadow-sm transition-colors"
              >
                <RefreshCw className="w-4 h-4" aria-hidden="true" />
                <span>Retry</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  handleRemoveFile();
                  fileInputRef.current?.click();
                }}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-white text-red-900 hover:bg-red-100 border border-red-400 transition-colors"
              >
                <Upload className="w-4 h-4" aria-hidden="true" />
                <span>Upload Another Report</span>
              </button>

              <button
                type="button"
                onClick={() => cameraInputRef.current?.click()}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-white text-slate-800 hover:bg-slate-100 border border-slate-300 transition-colors"
              >
                <Camera className="w-4 h-4" aria-hidden="true" />
                <span>Retake Photo</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  handleRemoveFile();
                  fileInputRef.current?.click();
                }}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-white text-slate-800 hover:bg-slate-100 border border-slate-300 transition-colors"
              >
                <FileText className="w-4 h-4" aria-hidden="true" />
                <span>Choose Another File</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Quality & Edge-Case Verification Sandbox */}
      {scenarios.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-start gap-3">
            <FlaskConical className="w-6 h-6 text-teal-700 shrink-0 mt-0.5" aria-hidden="true" />
            <div>
              <h2 className="text-base sm:text-lg font-bold text-slate-900">
                Test Live Image Quality, Blur Rejection & PDF Validation Scenarios
              </h2>
              <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
                Click any synthetic sample file below to run it through the actual backend OpenCV
                blur/darkness/crop/skew detector, OCR engine, and PyMuPDF validator (Labelled:{' '}
                <strong>Sample Data — Not a Real Patient</strong>):
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {scenarios.map((sc) => {
              const isAccept = sc.expected_outcome.toLowerCase().startsWith('accepted');
              return (
                <button
                  key={sc.id}
                  type="button"
                  disabled={uploading}
                  onClick={() => onRunTestScenario(sc.id)}
                  className="text-left p-3.5 rounded-xl border border-slate-200 hover:border-teal-600 hover:bg-teal-50/40 transition-all flex flex-col justify-between gap-2 disabled:opacity-60"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-slate-900">{sc.title}</span>
                      <span
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                          isAccept
                            ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                            : 'bg-amber-50 text-amber-800 border border-amber-200'
                        }`}
                      >
                        {isAccept ? 'Passes CV' : 'Rejects'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">{sc.description}</p>
                  </div>
                  <div className="text-[11px] font-mono text-teal-800 truncate">
                    File: {sc.filename}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
