import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, TabType } from './components/Sidebar';
import { MapView } from './components/MapView';
import { SatelliteAnalysisPanel } from './components/SatelliteAnalysisPanel';
import { DriftAnalysisPanel } from './components/DriftAnalysisPanel';
import { AISAnalysisPanel } from './components/AISAnalysisPanel';
import { VesselRankingPanel } from './components/VesselRankingPanel';
import { UploadSection } from './components/UploadSection';
import { fetchFullAnalysis } from './services/api';
import { FullAnalysisResponse, EnvironmentalParameters, RankingWeights } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('map');
  const [analysisData, setAnalysisData] = useState<FullAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedMMSI, setSelectedMMSI] = useState<number | null>(null);

  const [environmental, setEnvironmental] = useState<EnvironmentalParameters>({
    wind_speed_knots: 14.5,
    wind_direction_deg: 225.0,
    current_speed_knots: 1.2,
    current_direction_deg: 45.0,
  });

  const [weights, setWeights] = useState<RankingWeights>({
    distance_weight: 0.30,
    time_weight: 0.25,
    trajectory_weight: 0.25,
    course_weight: 0.10,
    anomaly_weight: 0.10,
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchFullAnalysis(environmental, weights);
      setAnalysisData(res);
      if (res.ranked_vessels.length > 0 && !selectedMMSI) {
        setSelectedMMSI(res.ranked_vessels[0].mmsi);
      }
    } catch (err) {
      console.error("Failed to load analysis data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [weights]);

  return (
    <div className="flex flex-col h-screen w-screen bg-navy-950 text-slate-100 overflow-hidden">
      <Header data={analysisData} loading={loading} onRefresh={loadData} />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          weights={weights}
          setWeights={setWeights}
        />

        <main className="flex-1 relative overflow-hidden bg-navy-950">
          {activeTab === 'map' && (
            <MapView
              data={analysisData}
              selectedVesselMMSI={selectedMMSI}
              onSelectVessel={(mmsi) => setSelectedMMSI(mmsi)}
            />
          )}

          {activeTab === 'satellite' && (
            <SatelliteAnalysisPanel data={analysisData} />
          )}

          {activeTab === 'drift' && (
            <DriftAnalysisPanel data={analysisData} />
          )}

          {activeTab === 'ais' && (
            <AISAnalysisPanel
              data={analysisData}
              selectedMMSI={selectedMMSI}
              onSelectVessel={(mmsi) => {
                setSelectedMMSI(mmsi);
                setActiveTab('map');
              }}
            />
          )}

          {activeTab === 'ranking' && (
            <VesselRankingPanel
              data={analysisData}
              selectedMMSI={selectedMMSI}
              onSelectVessel={(mmsi) => {
                setSelectedMMSI(mmsi);
                setActiveTab('map');
              }}
            />
          )}

          {activeTab === 'upload' && (
            <UploadSection
              environmental={environmental}
              setEnvironmental={setEnvironmental}
              onUploadSuccess={loadData}
            />
          )}
        </main>
      </div>
    </div>
  );
};
