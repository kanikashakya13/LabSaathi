import React from 'react';
import { FileCheck2, ShieldCheck, Upload } from 'lucide-react';
import { HealthResponse } from '../types';

interface NavbarProps {
  activeTab: 'home' | 'upload' | 'review' | 'results';
  onNavigateHome: (sectionId?: string) => void;
  onStartUpload: () => void;
  onTrySample: () => void;
  health: HealthResponse | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  onNavigateHome,
  onStartUpload,
  health,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200 no-print">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20 gap-3">
          {/* Logo and Tagline */}
          <button
            type="button"
            onClick={() => onNavigateHome('top')}
            className="flex items-center gap-3 text-left group rounded-lg p-1 -ml-1"
            aria-label="LabSaathi Home — Confused by Reports? Decode Them!"
          >
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-teal-600 to-sky-700 flex items-center justify-center text-white shadow-sm group-hover:from-teal-700 group-hover:to-sky-800 transition-colors">
              <FileCheck2 className="w-6 h-6" aria-hidden="true" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-slate-900">
                  Lab<span className="text-teal-700">Saathi</span>
                </span>
                <span className="hidden xl:inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-800 border border-teal-200">
                  <ShieldCheck className="w-3.5 h-3.5 text-teal-700" aria-hidden="true" />
                  Educational Health Guide
                </span>
              </div>
              <p className="text-xs text-slate-600 font-medium hidden sm:block">
                Confused by Reports? Decode Them!
              </p>
            </div>
          </button>

          {/* Primary Navigation Links */}
          <nav aria-label="Primary Navigation" className="hidden md:flex items-center gap-1 lg:gap-2">
            <button
              type="button"
              onClick={() => onNavigateHome('top')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'home'
                  ? 'bg-teal-50 text-teal-800 font-semibold'
                  : 'text-slate-700 hover:text-teal-700 hover:bg-slate-100'
              }`}
            >
              Home
            </button>
            <button
              type="button"
              onClick={() => onNavigateHome('how-it-works')}
              className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-teal-700 hover:bg-slate-100 transition-colors"
            >
              How It Works
            </button>
            <button
              type="button"
              onClick={() => onNavigateHome('features')}
              className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-teal-700 hover:bg-slate-100 transition-colors"
            >
              Features
            </button>
            <button
              type="button"
              onClick={() => onNavigateHome('about')}
              className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-teal-700 hover:bg-slate-100 transition-colors"
            >
              About
            </button>
            <button
              type="button"
              onClick={() => onNavigateHome('privacy')}
              className="px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:text-teal-700 hover:bg-slate-100 transition-colors"
            >
              Privacy
            </button>
          </nav>

          {/* Service Status & CTA */}
          <div className="flex items-center gap-2.5">
            {health && (
              <span
                className="hidden lg:inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200"
                title={health.services.ai_explanation_service.setup_message}
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    health.services.ai_explanation_service.configured
                      ? 'bg-emerald-600'
                      : 'bg-teal-600'
                  }`}
                  aria-hidden="true"
                />
                {health.services.ai_explanation_service.configured
                  ? 'Live Gemini AI + Medical KB'
                  : 'Curated Medical KB Active'}
              </span>
            )}

            <button
              type="button"
              onClick={onStartUpload}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-teal-700 text-white hover:bg-teal-800 shadow-sm transition-colors"
            >
              <Upload className="w-4 h-4" aria-hidden="true" />
              <span>Understand My Report</span>
            </button>
          </div>
        </div>

        {/* Mobile Secondary Nav Bar */}
        <nav
          aria-label="Mobile Navigation"
          className="flex md:hidden items-center justify-start gap-2 overflow-x-auto py-2 border-t border-slate-100 text-xs"
        >
          <button
            type="button"
            onClick={() => onNavigateHome('top')}
            className="px-2.5 py-1 rounded-md font-medium text-slate-700 hover:bg-slate-100 whitespace-nowrap"
          >
            Home
          </button>
          <button
            type="button"
            onClick={() => onNavigateHome('how-it-works')}
            className="px-2.5 py-1 rounded-md font-medium text-slate-700 hover:bg-slate-100 whitespace-nowrap"
          >
            How It Works
          </button>
          <button
            type="button"
            onClick={() => onNavigateHome('features')}
            className="px-2.5 py-1 rounded-md font-medium text-slate-700 hover:bg-slate-100 whitespace-nowrap"
          >
            Features
          </button>
          <button
            type="button"
            onClick={() => onNavigateHome('about')}
            className="px-2.5 py-1 rounded-md font-medium text-slate-700 hover:bg-slate-100 whitespace-nowrap"
          >
            About
          </button>
          <button
            type="button"
            onClick={() => onNavigateHome('privacy')}
            className="px-2.5 py-1 rounded-md font-medium text-slate-700 hover:bg-slate-100 whitespace-nowrap"
          >
            Privacy
          </button>
        </nav>
      </div>
    </header>
  );
};
