import React from 'react';
import { Waves, Cpu, Play, ShieldAlert, FileSpreadsheet } from 'lucide-react';

export const Navbar = ({ onSeedDemo, isDemoLoading }) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-cyan-500/20 px-6 py-3 mb-6 flex flex-wrap items-center justify-between shadow-lg">
      {/* Brand */}
      <div className="flex items-center space-x-3">
        <div className="p-2.5 bg-gradient-to-tr from-cyan-600 to-blue-700 rounded-xl shadow-lg shadow-cyan-500/20">
          <Waves className="w-6 h-6 text-white animate-pulse" />
        </div>
        <div>
          <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-blue-300 to-emerald-400 bg-clip-text text-transparent">
            AquaGuard AI
          </h1>
          <p className="text-xs text-slate-400 font-mono">Autonomous Side Scan Sonar Debris & GIS System</p>
        </div>
      </div>

      {/* Badges & Demo Action */}
      <div className="flex items-center space-x-4 mt-2 sm:mt-0">
        <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-emerald-500/30 text-xs font-mono text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>YOLOv11 Preprocessed Pipeline Ready</span>
        </div>

        <button
          onClick={onSeedDemo}
          disabled={isDemoLoading}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-sm transition-all duration-200 shadow-md shadow-cyan-500/25 active:scale-95 disabled:opacity-50"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>{isDemoLoading ? 'Loading Demo Datasets...' : 'Run Demo Mode'}</span>
        </button>
      </div>
    </header>
  );
};
