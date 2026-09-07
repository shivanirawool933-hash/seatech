import React from 'react';
import { Compass, Wind, Waves, Navigation, Clock, MapPin } from 'lucide-react';
import { FullAnalysisResponse } from '../types';

interface DriftAnalysisPanelProps {
  data: FullAnalysisResponse | null;
}

export const DriftAnalysisPanel: React.FC<DriftAnalysisPanelProps> = ({ data }) => {
  if (!data) return null;

  const drift = data.drift;

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full text-slate-100 max-w-5xl mx-auto">
      <div className="border-b border-navy-800 pb-4">
        <h2 className="text-xl font-bold text-slate-100 tracking-wide flex items-center gap-2">
          <Compass className="w-5 h-5 text-amber-400" />
          Oceanographic Drift & Backward Hindcasting Model
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Vector advection model calculating reverse oil slick transport to estimate origin time & coordinates.
        </p>
      </div>

      {/* Probable Origin Banner */}
      <div className="glass-card p-5 rounded-xl border border-amber-500/30 bg-amber-950/20 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="space-y-1">
          <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
            <MapPin className="w-4 h-4" /> Estimated Spill Origin Location
          </span>
          <div className="text-xl font-mono font-bold text-slate-100">
            {drift.probable_origin_lat.toFixed(5)}°N, {drift.probable_origin_lon.toFixed(5)}°E
          </div>
          <p className="text-xs text-slate-400">
            Estimated Creation Time: <span className="font-mono text-amber-300 font-semibold">{new Date(drift.estimated_origin_time).toUTCString()}</span>
          </p>
        </div>

        <div className="px-4 py-2 rounded-lg bg-navy-950 border border-navy-800 text-xs font-mono text-cyan-400">
          {drift.status_message}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backward Hindcast Path Timeline */}
        <div className="glass-card p-5 rounded-xl space-y-4 border border-navy-800">
          <h3 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-400" />
            Backward Hindcast Steps (t = 0 to Origin)
          </h3>

          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {drift.hindcast_path.map((point, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-navy-950/80 border border-navy-800 flex justify-between items-center text-xs font-mono">
                <div>
                  <span className="text-amber-400 font-bold">{point.hours_offset} hours</span>
                  <div className="text-[10px] text-slate-500">{new Date(point.timestamp).toLocaleTimeString()}</div>
                </div>
                <div className="text-right text-slate-300">
                  <div>{point.latitude.toFixed(4)}°N, {point.longitude.toFixed(4)}°E</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Forward Prediction Path Timeline */}
        <div className="glass-card p-5 rounded-xl space-y-4 border border-navy-800">
          <h3 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
            <Navigation className="w-4 h-4 text-cyan-400" />
            Forward Forecast Predictions (Future Transport)
          </h3>

          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {drift.forecast_path.map((point, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-navy-950/80 border border-navy-800 flex justify-between items-center text-xs font-mono">
                <div>
                  <span className="text-cyan-400 font-bold">+{point.hours_offset} hours</span>
                  <div className="text-[10px] text-slate-500">{new Date(point.timestamp).toLocaleTimeString()}</div>
                </div>
                <div className="text-right text-slate-300">
                  <div>{point.latitude.toFixed(4)}°N, {point.longitude.toFixed(4)}°E</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
