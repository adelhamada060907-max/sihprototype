import React from 'react';
import { Download, FileJson, FileSpreadsheet, ShieldCheck } from 'lucide-react';
import { getJsonReportUrl, getCsvReportUrl } from '../services/api';

export const ReportExporter = () => {
  return (
    <div className="glass-panel p-6 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-cyan-300 flex items-center gap-2">
            <Download className="w-5 h-5" />
            Geospatial Report Export System
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            Generate standardized marine debris survey reports with WGS84 coordinates & anomaly scores.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <a
            href={getJsonReportUrl()}
            download
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm transition-all duration-150 shadow-md shadow-emerald-600/30"
          >
            <FileJson className="w-4 h-4" />
            <span>Download JSON Report</span>
          </a>

          <a
            href={getCsvReportUrl()}
            download
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-all duration-150 shadow-md shadow-blue-600/30"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Download CSV Report</span>
          </a>
        </div>
      </div>
    </div>
  );
};
