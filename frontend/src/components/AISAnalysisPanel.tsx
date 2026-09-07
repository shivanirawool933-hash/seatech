import React from 'react';
import { Ship, Navigation, Anchor, Activity } from 'lucide-react';
import { FullAnalysisResponse } from '../types';

interface AISAnalysisPanelProps {
  data: FullAnalysisResponse | null;
  selectedMMSI: number | null;
  onSelectVessel: (mmsi: number) => void;
}

export const AISAnalysisPanel: React.FC<AISAnalysisPanelProps> = ({
  data,
  selectedMMSI,
  onSelectVessel
}) => {
  if (!data) return null;

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full text-slate-100 max-w-5xl mx-auto">
      <div className="border-b border-navy-800 pb-4">
        <h2 className="text-xl font-bold text-slate-100 tracking-wide flex items-center gap-2">
          <Ship className="w-5 h-5 text-cyan-400" />
          AIS Vessel Trajectories & Position History
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Historical AIS tracking data, reconstructed vessel trajectories, speed, and course parameters within search radius.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {data.trajectories.map((traj) => {
          const isSelected = selectedMMSI === traj.mmsi;
          const score = data.ranked_vessels.find(v => v.mmsi === traj.mmsi);

          return (
            <div
              key={traj.mmsi}
              onClick={() => onSelectVessel(traj.mmsi)}
              className={`glass-card p-4 rounded-xl space-y-3 cursor-pointer transition-all border ${
                isSelected 
                  ? 'border-cyan-500 bg-navy-850 shadow-glow-cyan' 
                  : 'border-navy-800 hover:border-navy-700'
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-sm text-slate-100">{traj.vessel_name}</h3>
                  <span className="text-[11px] text-slate-400 font-mono">MMSI: {traj.mmsi}</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 text-[10px] font-mono border border-cyan-800">
                  {traj.vessel_type}
                </span>
              </div>

              <div className="space-y-1 text-xs font-mono text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-400">Total Tracked Points:</span>
                  <span>{traj.positions.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Track Length:</span>
                  <span>{traj.total_distance_km} km</span>
                </div>
                {score && (
                  <div className="flex justify-between font-bold pt-1 border-t border-navy-800">
                    <span className="text-slate-400 font-sans">Attribution Score:</span>
                    <span className={score.composite_score >= 75 ? 'text-red-400' : 'text-amber-400'}>
                      {score.composite_score}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Vessel Position Log Table */}
      {selectedMMSI && (
        <div className="glass-card p-5 rounded-xl space-y-4 border border-navy-800">
          <h3 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            Detailed Waypoint Log for MMSI {selectedMMSI}
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-navy-950 text-slate-400 border-b border-navy-800">
                <tr>
                  <th className="p-2.5">Timestamp (UTC)</th>
                  <th className="p-2.5">Latitude</th>
                  <th className="p-2.5">Longitude</th>
                  <th className="p-2.5">Speed (SOG)</th>
                  <th className="p-2.5">Course (COG)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-850">
                {data.trajectories
                  .find(t => t.mmsi === selectedMMSI)
                  ?.positions.map((pos, idx) => (
                    <tr key={idx} className="hover:bg-navy-800/50 text-slate-300">
                      <td className="p-2.5 text-cyan-300">{new Date(pos.timestamp).toUTCString()}</td>
                      <td className="p-2.5">{pos.latitude.toFixed(5)}°N</td>
                      <td className="p-2.5">{pos.longitude.toFixed(5)}°E</td>
                      <td className="p-2.5 font-bold text-amber-400">{pos.sog || 0} knots</td>
                      <td className="p-2.5">{pos.cog || 0}°</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
