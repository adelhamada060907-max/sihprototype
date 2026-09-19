import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { BarChart2, Shield, Activity, Anchor } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

export const AnalyticsPanel = ({ analyticsData }) => {
  const { total_detections = 0, category_counts = {}, confidence_distribution = {} } = analyticsData || {};

  const categoryLabels = Object.keys(category_counts);
  const categoryValues = Object.values(category_counts);

  const doughnutData = {
    labels: categoryLabels.map(l => l.replace('_', ' ')),
    datasets: [
      {
        data: categoryValues.length > 0 ? categoryValues : [1],
        backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981'],
        borderColor: '#0f172a',
        borderWidth: 2,
      },
    ],
  };

  const barData = {
    labels: ['High (>80%)', 'Medium (55-80%)', 'Low (<55%)'],
    datasets: [
      {
        label: 'Detection Confidence',
        data: [
          confidence_distribution.high || 0,
          confidence_distribution.medium || 0,
          confidence_distribution.low || 0
        ],
        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b'],
        borderRadius: 6
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } }
      }
    }
  };

  return (
    <div className="glass-panel p-6 mb-6">
      <h2 className="text-lg font-semibold text-cyan-300 flex items-center gap-2 mb-4">
        <BarChart2 className="w-5 h-5" />
        Acoustic Analytics & Metrics Dashboard
      </h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-cyan-500/20">
          <span className="text-xs font-mono text-slate-400 block">Total Target Alerts</span>
          <span className="text-2xl font-extrabold text-cyan-400 font-mono">{total_detections}</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-red-500/20">
          <span className="text-xs font-mono text-slate-400 block">Ghost Nets Detected</span>
          <span className="text-2xl font-extrabold text-red-400 font-mono">
            {category_counts.ghost_net || 0}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-amber-500/20">
          <span className="text-xs font-mono text-slate-400 block">Sunken Wrecks / Obstacles</span>
          <span className="text-2xl font-extrabold text-amber-400 font-mono">
            {category_counts.shipwreck || 0}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-emerald-500/20">
          <span className="text-xs font-mono text-slate-400 block">Avg Anomaly Verification</span>
          <span className="text-2xl font-extrabold text-emerald-400 font-mono">88.4%</span>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800 h-[240px] flex flex-col items-center">
          <h4 className="text-xs font-mono text-slate-300 mb-2">Debris Object Categories</h4>
          <div className="w-full h-[180px]">
            <Doughnut data={doughnutData} options={chartOptions} />
          </div>
        </div>

        <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800 h-[240px] flex flex-col items-center">
          <h4 className="text-xs font-mono text-slate-300 mb-2">AI Confidence Distribution</h4>
          <div className="w-full h-[180px]">
            <Bar data={barData} options={chartOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};
