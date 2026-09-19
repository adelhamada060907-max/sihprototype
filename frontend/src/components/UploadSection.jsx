import React, { useState } from 'react';
import { Upload, Compass, Navigation, Layers, Zap } from 'lucide-react';

export const UploadSection = ({ onUpload, isUploading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [latitude, setLatitude] = useState(15.4989);
  const [longitude, setLongitude] = useState(73.8278);
  const [depth, setDepth] = useState(25.0);
  const [heading, setHeading] = useState(45.0);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('latitude', latitude);
    formData.append('longitude', longitude);
    formData.append('depth_meters', depth);
    formData.append('sonar_heading_deg', heading);

    onUpload(formData);
  };

  return (
    <div className="glass-panel p-6 mb-6">
      <h2 className="text-lg font-semibold text-cyan-300 mb-4 flex items-center gap-2">
        <Upload className="w-5 h-5" />
        Ingest Sonar Waterfall & Telemetry
      </h2>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Dropzone */}
        <div className="md:col-span-6 flex flex-col justify-center items-center border-2 border-dashed border-cyan-500/30 hover:border-cyan-400/70 rounded-xl p-6 bg-slate-900/40 transition-colors">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
            id="sonar-file-input"
          />
          <label htmlFor="sonar-file-input" className="cursor-pointer flex flex-col items-center text-center">
            <Layers className="w-10 h-10 text-cyan-400 mb-2 animate-bounce" />
            <span className="text-sm font-medium text-slate-200">
              {selectedFile ? selectedFile.name : 'Drop raw Side Scan Sonar image here or click to browse'}
            </span>
            <span className="text-xs text-slate-500 mt-1">Supports PNG, JPG, TIFF (Max 20MB)</span>
          </label>
        </div>

        {/* Telemetry Inputs */}
        <div className="md:col-span-6 grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-mono text-slate-400 block mb-1 flex items-center gap-1">
              <Navigation className="w-3 h-3 text-cyan-400" /> Vessel Latitude (°N)
            </label>
            <input
              type="number"
              step="0.0001"
              value={latitude}
              onChange={(e) => setLatitude(parseFloat(e.target.value))}
              className="w-full bg-slate-900/80 border border-slate-700 focus:border-cyan-500 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-mono text-slate-400 block mb-1 flex items-center gap-1">
              <Navigation className="w-3 h-3 text-cyan-400" /> Vessel Longitude (°E)
            </label>
            <input
              type="number"
              step="0.0001"
              value={longitude}
              onChange={(e) => setLongitude(parseFloat(e.target.value))}
              className="w-full bg-slate-900/80 border border-slate-700 focus:border-cyan-500 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-mono text-slate-400 block mb-1">Depth (Meters)</label>
            <input
              type="number"
              step="0.1"
              value={depth}
              onChange={(e) => setDepth(parseFloat(e.target.value))}
              className="w-full bg-slate-900/80 border border-slate-700 focus:border-cyan-500 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-mono text-slate-400 block mb-1 flex items-center gap-1">
              <Compass className="w-3 h-3 text-cyan-400" /> Sonar Heading (Deg)
            </label>
            <input
              type="number"
              step="1"
              value={heading}
              onChange={(e) => setHeading(parseFloat(e.target.value))}
              className="w-full bg-slate-900/80 border border-slate-700 focus:border-cyan-500 rounded-lg px-3 py-2 text-sm text-slate-100 font-mono"
            />
          </div>

          <div className="col-span-2 mt-2">
            <button
              type="submit"
              disabled={!selectedFile || isUploading}
              className="w-full py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm transition-all flex items-center justify-center space-x-2 shadow-lg shadow-cyan-600/30 disabled:opacity-40"
            >
              <Zap className="w-4 h-4 fill-current" />
              <span>{isUploading ? 'Executing AI Detection Pipeline...' : 'Run AI Sonar Detection'}</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
