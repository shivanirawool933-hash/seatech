import React from 'react';
import { Waves, Satellite, Ship, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';
import { FullAnalysisResponse } from '../types';

interface HeaderProps {
  data: FullAnalysisResponse | null;
  loading: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ data, loading, onRefresh }) => {
  return (
    <header className="h-16 bg-navy-900 border-b border-navy-800 flex items-center justify-between px-6 z-20 shadow-lg">
      <div className="flex items-center space-x-4">
        <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-glow-cyan">
          <Waves className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-100 tracking-wide flex items-center gap-2">
            OILSPILL INTELLIGENCE
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">v1.0 SAR</span>
          </h1>
          <p className="text-xs text-slate-400">Satellite Detection + AIS Vessel Attribution System</p>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        {data && (
          <div className="hidden md:flex items-center space-x-4 text-xs font-mono">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-navy-850 border border-navy-800">
              <Satellite className="w-4 h-4 text-cyan-400" />
              <span className="text-slate-400">SPILL AREA:</span>
              <span className="text-cyan-400 font-semibold">{data.detection.area_sq_km} km²</span>
            </div>

            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-navy-850 border border-navy-800">
              <Ship className="w-4 h-4 text-amber-400" />
              <span className="text-slate-400">VESSELS TRACKED:</span>
              <span className="text-amber-400 font-semibold">{data.trajectories.length}</span>
            </div>

            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-navy-850 border border-navy-800">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span className="text-slate-400">TOP CANDIDATE:</span>
              <span className="text-red-400 font-semibold">
                {data.ranked_vessels[0]?.vessel_name || 'N/A'} ({data.ranked_vessels[0]?.composite_score}%)
              </span>
            </div>
          </div>
        )}

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs shadow-glow-cyan transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Analyzing...' : 'Run Intelligence Scan'}</span>
        </button>
      </div>
    </header>
  );
};
