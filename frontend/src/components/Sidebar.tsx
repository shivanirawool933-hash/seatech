import React from 'react';
import { 
  Map, Satellite, Compass, Ship, Trophy, Upload, Sliders, Info 
} from 'lucide-react';
import { RankingWeights } from '../types';

export type TabType = 'map' | 'satellite' | 'drift' | 'ais' | 'ranking' | 'upload';

interface SidebarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  weights: RankingWeights;
  setWeights: React.Dispatch<React.SetStateAction<RankingWeights>>;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  weights,
  setWeights
}) => {
  const tabs = [
    { id: 'map', label: 'GIS Map Workspace', icon: Map },
    { id: 'satellite', label: 'Satellite Analysis', icon: Satellite },
    { id: 'drift', label: 'Drift & Hindcasting', icon: Compass },
    { id: 'ais', label: 'AIS Vessel Trajectories', icon: Ship },
    { id: 'ranking', label: 'Vessel Ranking Engine', icon: Trophy },
    { id: 'upload', label: 'Data Sources & Upload', icon: Upload },
  ];

  const handleWeightChange = (key: keyof RankingWeights, value: number) => {
    setWeights(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <aside className="w-64 bg-navy-900 border-r border-navy-800 flex flex-col justify-between z-10 shrink-0">
      <div className="p-4 space-y-6 overflow-y-auto">
        <div>
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-2">Navigation</h2>
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive 
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-glow-cyan' 
                      : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="pt-4 border-t border-navy-800 space-y-4">
          <div className="flex items-center justify-between px-2">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-cyan-400" />
              Scoring Weights
            </h2>
            <span className="text-[10px] text-cyan-400 font-mono">Configurable</span>
          </div>

          <div className="space-y-3 px-2 text-xs">
            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Distance:</span>
                <span className="font-mono text-cyan-400">{(weights.distance_weight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.distance_weight}
                onChange={(e) => handleWeightChange('distance_weight', parseFloat(e.target.value))}
                className="w-full accent-cyan-500 h-1 bg-navy-800 rounded cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Time Delta:</span>
                <span className="font-mono text-cyan-400">{(weights.time_weight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.time_weight}
                onChange={(e) => handleWeightChange('time_weight', parseFloat(e.target.value))}
                className="w-full accent-cyan-500 h-1 bg-navy-800 rounded cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Trajectory Proximity:</span>
                <span className="font-mono text-cyan-400">{(weights.trajectory_weight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.trajectory_weight}
                onChange={(e) => handleWeightChange('trajectory_weight', parseFloat(e.target.value))}
                className="w-full accent-cyan-500 h-1 bg-navy-800 rounded cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Course/Speed:</span>
                <span className="font-mono text-cyan-400">{(weights.course_weight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.course_weight}
                onChange={(e) => handleWeightChange('course_weight', parseFloat(e.target.value))}
                className="w-full accent-cyan-500 h-1 bg-navy-800 rounded cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Anomaly Flag:</span>
                <span className="font-mono text-cyan-400">{(weights.anomaly_weight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.anomaly_weight}
                onChange={(e) => handleWeightChange('anomaly_weight', parseFloat(e.target.value))}
                className="w-full accent-cyan-500 h-1 bg-navy-800 rounded cursor-pointer"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-navy-800">
        <div className="p-3 rounded-lg bg-navy-850 border border-navy-800 flex items-start space-x-2 text-[11px] text-slate-400">
          <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <p>Analytical scoring model. Results do not constitute legal proof of liability.</p>
        </div>
      </div>
    </aside>
  );
};
