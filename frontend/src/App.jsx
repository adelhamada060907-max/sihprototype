import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { UploadSection } from './components/UploadSection';
import { SonarViewer } from './components/SonarViewer';
import { MapViewer } from './components/MapViewer';
import { AnalyticsPanel } from './components/AnalyticsPanel';
import { ReportExporter } from './components/ReportExporter';
import {
  uploadSonarImage,
  runDetection,
  fetchAllDetections,
  fetchAnalytics,
  seedDemoData
} from './services/api';

export function App() {
  const [activeImage, setActiveImage] = useState(null);
  const [detections, setDetections] = useState([]);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);

  const loadData = async () => {
    try {
      const dets = await fetchAllDetections();
      setDetections(dets);
      const analytics = await fetchAnalytics();
      setAnalyticsData(analytics);
    } catch (err) {
      console.warn('Backend server not connected yet or empty state:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpload = async (formData) => {
    setIsUploading(true);
    try {
      const uploadRes = await uploadSonarImage(formData);
      setActiveImage(uploadRes);

      // Trigger AI Detection
      const detResult = await runDetection(uploadRes.id);
      setActiveImage({
        ...uploadRes,
        file_url: detResult.file_url || uploadRes.file_url
      });

      await loadData();
    } catch (err) {
      alert('Failed executing sonar detection: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsUploading(false);
    }
  };

  const handleSeedDemo = async () => {
    setIsDemoLoading(true);
    try {
      const seedRes = await seedDemoData();
      if (seedRes.samples && seedRes.samples.length > 0) {
        const firstSample = seedRes.samples[0];
        setActiveImage({
          id: firstSample.image_id,
          filename: firstSample.filename,
          file_url: firstSample.file_url
        });
      }
      await loadData();
    } catch (err) {
      alert('Failed seeding SIH demo data: ' + err.message);
    } finally {
      setIsDemoLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans pb-12">
      <Navbar onSeedDemo={handleSeedDemo} isDemoLoading={isDemoLoading} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex-grow">
        {/* Banner */}
        <div className="glass-panel p-6 mb-6 bg-gradient-to-r from-slate-900 via-cyan-950/40 to-slate-900 border-cyan-500/30">
          <h2 className="text-2xl font-extrabold text-cyan-300 tracking-tight">
            Autonomous Underwater Debris & Ghost Net Detection
          </h2>
          <p className="text-sm text-slate-300 mt-1 max-w-3xl">
            AquaGuard AI applies multi-stage acoustic pre-filtering (CLAHE + Bilateral speckle suppression),
            YOLOv11 neural inference, trailing acoustic shadow anomaly verification, and geospatial telemetry mapping.
          </p>
        </div>

        {/* Upload Interface */}
        <UploadSection onUpload={handleUpload} isUploading={isUploading} />

        {/* Dual Grid: Sonar Viewer & Geospatial Map */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-6">
            <SonarViewer activeImage={activeImage} detections={detections} />
          </div>
          <div className="lg:col-span-6">
            <MapViewer detections={detections} />
          </div>
        </div>

        {/* Analytics Panel */}
        <AnalyticsPanel analyticsData={analyticsData} />

        {/* Report Exporter */}
        <ReportExporter />
      </main>

      <footer className="text-center py-6 text-xs text-slate-500 font-mono border-t border-slate-900 mt-12">
        AquaGuard AI — SIH Prototype Prototype • Powered by PyTorch, YOLOv11 & FastAPI
      </footer>
    </div>
  );
}

export default App;
