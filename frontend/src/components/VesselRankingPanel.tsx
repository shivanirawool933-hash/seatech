import React from 'react';
import { Trophy, AlertTriangle, ShieldAlert, CheckCircle2, ChevronRight } from 'lucide-react';
import { FullAnalysisResponse, VesselCandidateScore } from '../types';

interface VesselRankingPanelProps {
  data: FullAnalysisResponse | null;
  selectedMMSI: number | null;
  onSelectVessel: (mmsi: number) => void;
}

export const VesselRankingPanel: React.FC<VesselRankingPanelProps> = ({
  data,
  selectedMMSI,
  onSelectVessel
}) => {
  if (!data) return null;

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full text-slate-100 max-w-5xl mx-auto">
      <div className="border-b border-navy-800 pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-wide flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-400" />
            Transparent 5-Factor Vessel Candidate Ranking
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Multivariate attribution scoring correlating spill polygon, origin location, and temporal AIS proximity.
          </p>
        </div>
      </div>

      {/* Legal & Analytical Disclaimer Banner */}
      <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/30 flex items-start space-x-3 text-xs text-amber-300">
        <ShieldAlert className="w-5 h-5 shrink-0 text-amber-400 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="font-bold">ANALYTICAL DISCLAIMER:</strong> Scores represent probabilistic spatial-temporal correlation for maritime decision support. The system uses non-definitive terminology (e.g. <em>"Most likely candidate"</em>) and does not provide legal proof of vessel discharge liability.
        </p>
      </div>

      {/* Candidate Score Cards List */}
      <div className="space-y-4">
        {data.ranked_vessels.map((vessel, idx) => {
          const isSelected = selectedMMSI === vessel.mmsi;

          return (
            <div
              key={vessel.mmsi}
              onClick={() => onSelectVessel(vessel.mmsi)}
              className={`glass-card p-5 rounded-xl space-y-4 border transition-all cursor-pointer ${
                isSelected 
                  ? 'border-cyan-500 bg-navy-850 shadow-glow-cyan' 
                  : 'border-navy-800 hover:border-navy-700'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-navy-800 pb-3">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold font-mono text-sm ${
                    idx === 0 ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-navy-800 text-slate-300'
                  }`}>
                    #{idx + 1}
                  </div>
                  <div>
                    <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
                      {vessel.vessel_name}
                      <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 font-mono font-normal">
                        {vessel.vessel_type}
                      </span>
                    </h3>
                    <div className="text-xs text-slate-400 font-mono space-x-3 mt-0.5">
                      <span>MMSI: {vessel.mmsi}</span>
                      {vessel.imo && <span>IMO: {vessel.imo}</span>}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-[10px] text-slate-400 uppercase">Composite Score</div>
                    <div className={`text-2xl font-bold font-mono ${
                      vessel.composite_score >= 75 ? 'text-red-400' : 'text-amber-400'
                    }`}>
                      {vessel.composite_score}%
                    </div>
                  </div>
                  <span className={`px-2.5 py-1 rounded text-xs font-semibold ${
                    vessel.composite_score >= 75 
                      ? 'bg-red-950 text-red-400 border border-red-800' 
                      : 'bg-amber-950 text-amber-400 border border-amber-800'
                  }`}>
                    {vessel.candidate_status}
                  </span>
                </div>
              </div>

              {/* Feature Score Breakdown Bar Chart */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
                <div>
                  <div className="text-slate-400 text-[10px] mb-1">Distance (30%)</div>
                  <div className="h-2 bg-navy-950 rounded overflow-hidden">
                    <div className="h-full bg-cyan-500" style={{ width: `${vessel.feature_scores.distance_score}%` }}></div>
                  </div>
                  <span className="text-slate-300 text-[11px] font-bold">{vessel.feature_scores.distance_score}%</span>
                </div>

                <div>
                  <div className="text-slate-400 text-[10px] mb-1">Time Delta (25%)</div>
                  <div className="h-2 bg-navy-950 rounded overflow-hidden">
                    <div className="h-full bg-cyan-500" style={{ width: `${vessel.feature_scores.time_score}%` }}></div>
                  </div>
                  <span className="text-slate-300 text-[11px] font-bold">{vessel.feature_scores.time_score}%</span>
                </div>

                <div>
                  <div className="text-slate-400 text-[10px] mb-1">Trajectory (25%)</div>
                  <div className="h-2 bg-navy-950 rounded overflow-hidden">
                    <div className="h-full bg-cyan-500" style={{ width: `${vessel.feature_scores.trajectory_score}%` }}></div>
                  </div>
                  <span className="text-slate-300 text-[11px] font-bold">{vessel.feature_scores.trajectory_score}%</span>
                </div>

                <div>
                  <div className="text-slate-400 text-[10px] mb-1">Course/Speed (10%)</div>
                  <div className="h-2 bg-navy-950 rounded overflow-hidden">
                    <div className="h-full bg-cyan-500" style={{ width: `${vessel.feature_scores.course_score}%` }}></div>
                  </div>
                  <span className="text-slate-300 text-[11px] font-bold">{vessel.feature_scores.course_score}%</span>
                </div>

                <div>
                  <div className="text-slate-400 text-[10px] mb-1">Anomaly (10%)</div>
                  <div className="h-2 bg-navy-950 rounded overflow-hidden">
                    <div className="h-full bg-cyan-500" style={{ width: `${vessel.feature_scores.anomaly_score}%` }}></div>
                  </div>
                  <span className="text-slate-300 text-[11px] font-bold">{vessel.feature_scores.anomaly_score}%</span>
                </div>
              </div>

              {/* Evidence Reasons Log */}
              <div className="space-y-1.5 pt-2 border-t border-navy-800">
                <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Analytical Evidence Trail:</span>
                <ul className="space-y-1 text-xs text-slate-300">
                  {vessel.evidence_reasons.map((reason, rIdx) => (
                    <li key={rIdx} className="flex items-start space-x-2">
                      <ChevronRight className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
