import React from 'react';
import { Satellite, ShieldCheck, MapPin, Maximize2, Layers, Cpu, Clock } from 'lucide-react';
import { FullAnalysisResponse } from '../types';

interface SatelliteAnalysisPanelProps {
  data: FullAnalysisResponse | null;
}

export const SatelliteAnalysisPanel: React.FC<SatelliteAnalysisPanelProps> = ({ data }) => {
  if (!data) return null;

  const sat = data.satellite;
  const det = data.detection;

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full text-slate-100 max-w-5xl mx-auto">
      <div className="border-b border-navy-800 pb-4">
        <h2 className="text-xl font-bold text-slate-100 tracking-wide flex items-center gap-2">
          <Satellite className="w-5 h-5 text-cyan-400" />
          Satellite Imagery & U-Net Oil Spill Segmentation Analysis
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Georeferenced SAR metadata, PyTorch segmentation mask metrics, and spatial polygon attributes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Scene Metadata Card */}
        <div className="glass-card p-5 rounded-xl space-y-4 border border-navy-800">
          <div className="flex items-center space-x-2 text-cyan-400 font-semibold text-sm">
            <Layers className="w-4 h-4" />
            <span>1. Georeferenced Scene Metadata</span>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between p-2 rounded bg-navy-950/70 border border-navy-800">
              <span className="text-slate-400">Scene Identifier:</span>
              <span className="text-cyan-300 font-bold">{sat.scene_id}</span>
            </div>

            <div className="flex justify-between p-2 rounded bg-navy-950/70 border border-navy-800">
              <span className="text-slate-400">File Name:</span>
              <span className="text-slate-200 truncate max-w-[220px]">{sat.filename}</span>
            </div>

            <div className="flex justify-between p-2 rounded bg-navy-950/70 border border-navy-800">
              <span className="text-slate-400">Dimensions:</span>
              <span className="text-slate-200">{sat.width} × {sat.height} px</span>
            </div>

            <div className="flex justify-between p-2 rounded bg-navy-950/70 border border-navy-800">
              <span className="text-slate-400">CRS (Coordinate Reference):</span>
              <span className="text-cyan-300 font-semibold">{sat.crs}</span>
            </div>

            <div className="flex justify-between p-2 rounded bg-navy-950/70 border border-navy-800">
              <span className="text-slate-400">Spatial Resolution:</span>
              <span className="text-slate-200">{sat.resolution_meters} meters / pixel</span>
            </div>

            <div className="flex justify-between p-2 rounded bg-navy-950/70 border border-navy-800">
              <span className="text-slate-400">Bands / Polarization:</span>
              <span className="text-slate-200">{sat.num_bands} bands ({sat.sensor_type})</span>
            </div>

            <div className="flex justify-between p-2 rounded bg-navy-950/70 border border-navy-800">
              <span className="text-slate-400">Acquisition Time:</span>
              <span className="text-amber-400">{sat.acquisition_time ? new Date(sat.acquisition_time).toUTCString() : 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Oil Spill Detection Results Card */}
        <div className="glass-card p-5 rounded-xl space-y-4 border border-navy-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-red-400 font-semibold text-sm">
              <Cpu className="w-4 h-4" />
              <span>2. Segmentation & Polygon Properties</span>
            </div>
            <span className="px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800 text-[10px] font-mono uppercase font-bold">
              SPILL DETECTED ({det.confidence * 100}%)
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div className="p-3 rounded bg-navy-950 border border-navy-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase">Estimated Area</span>
              <div className="text-lg font-bold text-red-400">{det.area_sq_km} km²</div>
              <span className="text-[10px] text-slate-500">{det.area_sq_m.toLocaleString()} m²</span>
            </div>

            <div className="p-3 rounded bg-navy-950 border border-navy-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase">Polygon Perimeter</span>
              <div className="text-lg font-bold text-cyan-400">{det.perimeter_km} km</div>
              <span className="text-[10px] text-slate-500">{(det.perimeter_km * 1000).toLocaleString()} m</span>
            </div>

            <div className="p-3 rounded bg-navy-950 border border-navy-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase">Major Axis Length</span>
              <div className="text-base font-bold text-slate-200">{det.estimated_length_m} m</div>
            </div>

            <div className="p-3 rounded bg-navy-950 border border-navy-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase">Minor Axis Width</span>
              <div className="text-base font-bold text-slate-200">{det.estimated_width_m} m</div>
            </div>
          </div>

          <div className="p-3 rounded bg-navy-950/80 border border-navy-800 space-y-1 text-xs font-mono">
            <div className="text-slate-400 text-[11px] font-sans font-semibold mb-1">Geographic Centroid (WGS 84):</div>
            <div className="text-cyan-300">
              Latitude: <span className="font-bold">{det.centroid_lat.toFixed(6)}°N</span>
            </div>
            <div className="text-cyan-300">
              Longitude: <span className="font-bold">{det.centroid_lon.toFixed(6)}°E</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
