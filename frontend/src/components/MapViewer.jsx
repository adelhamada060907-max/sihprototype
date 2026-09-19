import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { MapPin, Navigation } from 'lucide-react';
import L from 'leaflet';

// Create custom marker icons
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-map-marker',
    html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #ffffff; box-shadow: 0 0 10px ${color};"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7]
  });
};

const CLASS_COLORS = {
  ghost_net: '#ef4444',       // Red
  shipwreck: '#f59e0b',       // Amber
  pipe: '#3b82f6',            // Blue
  cylinder: '#8b5cf6',        // Purple
  underwater_debris: '#10b981' // Green
};

export const MapViewer = ({ detections = [] }) => {
  const defaultCenter = [15.4989, 73.8278]; // Default Goa/India Coast center
  const mapCenter = detections.length > 0 && detections[0].latitude
    ? [detections[0].latitude, detections[0].longitude]
    : defaultCenter;

  return (
    <div className="glass-panel p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-cyan-300 flex items-center gap-2">
          <MapPin className="w-5 h-5" />
          Real-World Geospatial GIS Map
        </h2>
        <span className="text-xs font-mono text-slate-400">
          WGS84 Coordinates Georeferenced ({detections.length} Target Pins)
        </span>
      </div>

      <div className="h-[400px] w-full rounded-xl overflow-hidden border border-cyan-500/20 shadow-inner">
        <MapContainer
          center={mapCenter}
          zoom={9}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
        >
          {/* Dark Esri Basemap */}
          <TileLayer
            attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />

          {detections.map((d, i) => {
            if (!d.latitude || !d.longitude) return null;
            const markerColor = CLASS_COLORS[d.object_class] || '#06b6d4';
            const icon = createCustomIcon(markerColor);

            return (
              <Marker key={d.id || i} position={[d.latitude, d.longitude]} icon={icon}>
                <Popup>
                  <div className="p-1 space-y-1 font-mono text-xs">
                    <div className="text-cyan-400 font-bold text-sm border-b border-slate-700 pb-1">
                      {d.object_class?.toUpperCase()}
                    </div>
                    <div><strong className="text-slate-400">Confidence:</strong> {d.confidence}%</div>
                    <div><strong className="text-slate-400">Anomaly Score:</strong> {d.anomaly_score}%</div>
                    <div><strong className="text-slate-400">Lat:</strong> {d.latitude?.toFixed(5)}°N</div>
                    <div><strong className="text-slate-400">Lon:</strong> {d.longitude?.toFixed(5)}°E</div>
                    <div><strong className="text-slate-400">Target Depth:</strong> {d.depth_meters}m</div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400">
        {Object.entries(CLASS_COLORS).map(([cls, color]) => (
          <div key={cls} className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full inline-block" style={{ backgroundColor: color }} />
            <span className="capitalize">{cls.replace('_', ' ')}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
