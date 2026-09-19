import React, { useState } from 'react';
import { Eye, ShieldCheck, AlertTriangle, Crosshair, ZoomIn } from 'lucide-react';

export const SonarViewer = ({ activeImage, detections = [] }) => {
  const [selectedDetection, setSelectedDetection] = useState(null);
  const [showOriginal, setShowOriginal] = useState(false);

  if (!activeImage) {
    return (
      <div className="glass-panel p-8 text-center flex flex-col items-center justify-center min-h-[380px]">
        <Crosshair className="w-12 h-12 text-slate-600 mb-3 animate-pulse" />
        <h3 className="text-lg font-medium text-slate-300">No Sonar Image Loaded</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-sm">
          Upload a sonar file above or click <strong className="text-cyan-400">Run SIH Demo Mode</strong> to load synthetic acoustic samples.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 mb-6">
      <div className="flex flex-wrap items-center justify-between mb-4 gap-2">
        <div>
          <h2 className="text-lg font-semibold text-cyan-300 flex items-center gap-2">
            <Eye className="w-5 h-5" />
            AI Sonar Target Detection Overlay
          </h2>
          <p className="text-xs text-slate-400 font-mono">Image: {activeImage.filename}</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowOriginal(!showOriginal)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-cyan-300 border border-cyan-500/20 transition-colors"
          >
            {showOriginal ? 'Show AI Bounding Boxes' : 'Show Raw Acoustic Image'}
          </button>
          <span className="px-3 py-1 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-xs font-mono">
            {detections.length} Target(s) Verified
          </span>
        </div>
      </div>

      {/* Sonar Canvas Container */}
      <div className="relative w-full overflow-hidden rounded-xl border border-cyan-500/20 bg-black flex justify-center items-center min-h-[420px]">
        <img
          src={activeImage.file_url}
          alt="Side Scan Sonar"
          className="w-full max-h-[550px] object-contain select-none"
        />

        {/* Render Bounding Boxes */}
        {!showOriginal &&
          detections.map((det, index) => {
            const bbox = det.bounding_box || det.bounding_box_coordinates || {};
            const xCenter = bbox.x_center ?? 0.5;
            const yCenter = bbox.y_center ?? 0.5;
            const width = bbox.width ?? 0.1;
            const height = bbox.height ?? 0.1;

            const left = `${(xCenter - width / 2) * 100}%`;
            const top = `${(yCenter - height / 2) * 100}%`;
            const wPct = `${width * 100}%`;
            const hPct = `${height * 100}%`;

            const isSelected = selectedDetection?.detection_code === det.detection_code;

            return (
              <div
                key={det.detection_code || index}
                onClick={() => setSelectedDetection(det)}
                style={{ left, top, width: wPct, height: hPct }}
                className={`absolute border-2 cursor-pointer transition-all duration-150 hover:scale-[1.02] ${
                  isSelected
                    ? 'border-emerald-400 bg-emerald-500/20 shadow-lg shadow-emerald-500/40 z-20'
                    : 'border-cyan-400 bg-cyan-500/10 hover:border-amber-400 z-10'
                }`}
              >
                {/* Badge Label */}
                <div className="absolute -top-7 left-0 px-2 py-0.5 rounded bg-slate-950/90 text-cyan-300 border border-cyan-500/40 text-[10px] font-mono whitespace-nowrap flex items-center space-x-1 shadow-md">
                  <span>{det.object_class}</span>
                  <span className="text-emerald-400">{det.confidence}%</span>
                  <span className="text-amber-400">({det.anomaly_score}% Anomaly)</span>
                </div>
              </div>
            );
          })}
      </div>

      {/* Selected Detection Details Modal / Strip */}
      {selectedDetection && (
        <div className="mt-4 p-4 rounded-xl bg-slate-900/90 border border-cyan-500/30 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-500 block">Class:</span>
            <span className="text-cyan-300 font-bold text-sm">{selectedDetection.object_class}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Confidence:</span>
            <span className="text-emerald-400 font-bold">{selectedDetection.confidence}%</span>
          </div>
          <div>
            <span className="text-slate-500 block">Anomaly Score:</span>
            <span className="text-amber-400 font-bold">{selectedDetection.anomaly_score}%</span>
          </div>
          <div>
            <span className="text-slate-500 block">Geospatial Target GPS:</span>
            <span className="text-slate-200">
              {selectedDetection.latitude?.toFixed(5)}°N, {selectedDetection.longitude?.toFixed(5)}°E
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
