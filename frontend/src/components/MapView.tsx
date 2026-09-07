import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polygon, Marker, Popup, Polyline, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { FullAnalysisResponse, VesselTrajectory, VesselCandidateScore } from '../types';
import { Ship, Waves, AlertTriangle, Compass, Layers } from 'lucide-react';

interface MapViewProps {
  data: FullAnalysisResponse | null;
  selectedVesselMMSI?: number | null;
  onSelectVessel?: (mmsi: number) => void;
}

// Auto-center map helper component
const MapRecenter: React.FC<{ center: [number, number] }> = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, 11);
  }, [center, map]);
  return null;
};

// Custom Boat/Vessel Icon builder
const createVesselIcon = (vesselType: string, isSelected: boolean) => {
  const color = isSelected ? '#ef4444' : '#06b6d4';
  const size = isSelected ? 32 : 26;
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1 .6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>
      <path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.94 5.34 2.81 7.76"/>
      <path d="M19 13V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6"/>
      <path d="M12 10V4"/>
      <path d="M12 2v2"/>
    </svg>
  `;
  return L.divIcon({
    html: `<div class="transition-transform duration-300 hover:scale-125 drop-shadow-md">${svg}</div>`,
    className: 'vessel-marker-icon',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
};

const createCentroidIcon = () => {
  return L.divIcon({
    html: `
      <div class="relative flex items-center justify-center">
        <span class="animate-ping absolute inline-flex h-6 w-6 rounded-full bg-red-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-4 w-4 bg-red-600 border-2 border-white shadow-glow-red"></span>
      </div>
    `,
    className: 'centroid-icon',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

const createOriginIcon = () => {
  return L.divIcon({
    html: `
      <div class="flex items-center justify-center w-6 h-6 rounded-full bg-amber-500 text-black border-2 border-white shadow-lg font-bold text-[10px]">
        O
      </div>
    `,
    className: 'origin-icon',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

export const MapView: React.FC<MapViewProps> = ({ data, selectedVesselMMSI, onSelectVessel }) => {
  const [showSpill, setShowSpill] = useState(true);
  const [showDrift, setShowDrift] = useState(true);
  const [showVessels, setShowVessels] = useState(true);

  if (!data) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-navy-950 text-slate-400">
        <div className="text-center space-y-3">
          <Waves className="w-12 h-12 text-cyan-500 animate-pulse mx-auto" />
          <p className="text-sm font-medium">Initializing Maritime Intelligence Map...</p>
        </div>
      </div>
    );
  }

  const center: [number, number] = [data.detection.centroid_lat, data.detection.centroid_lon];

  // Polygon coordinates: GeoJSON lon/lat -> Leaflet lat/lon
  const spillPolygonCoords: [number, number][] = data.detection.polygon.coordinates[0].map(
    ([lon, lat]) => [lat, lon]
  );

  // Drift path coords
  const hindcastCoords: [number, number][] = data.drift.hindcast_path.map(p => [p.latitude, p.longitude]);
  const forecastCoords: [number, number][] = data.drift.forecast_path.map(p => [p.latitude, p.longitude]);

  const originLatLon: [number, number] = [data.drift.probable_origin_lat, data.drift.probable_origin_lon];

  const getVesselScore = (mmsi: number): VesselCandidateScore | undefined => {
    return data.ranked_vessels.find(v => v.mmsi === mmsi);
  };

  return (
    <div className="relative w-full h-full">
      {/* Map Control Toggle Overlay */}
      <div className="absolute top-4 right-4 z-[1000] glass-panel p-3 rounded-lg shadow-xl space-y-2 text-xs">
        <div className="flex items-center space-x-2 font-semibold text-slate-200 border-b border-slate-700 pb-1.5 mb-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>GIS Layers</span>
        </div>

        <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            checked={showSpill}
            onChange={(e) => setShowSpill(e.target.checked)}
            className="rounded text-red-500 focus:ring-red-400 bg-navy-800"
          />
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
            Oil Spill Slick & Centroid
          </span>
        </label>

        <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            checked={showDrift}
            onChange={(e) => setShowDrift(e.target.checked)}
            className="rounded text-amber-500 focus:ring-amber-400 bg-navy-800"
          />
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            Drift & Hindcast Vectors
          </span>
        </label>

        <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            checked={showVessels}
            onChange={(e) => setShowVessels(e.target.checked)}
            className="rounded text-cyan-500 focus:ring-cyan-400 bg-navy-800"
          />
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            AIS Vessels & Trajectories
          </span>
        </label>
      </div>

      <MapContainer
        center={center}
        zoom={11}
        className="w-full h-full"
        zoomControl={false}
      >
        <MapRecenter center={center} />
        
        {/* Dark CartoDB Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />

        {/* Oil Spill Layer */}
        {showSpill && (
          <>
            <Polygon
              positions={spillPolygonCoords}
              pathOptions={{
                color: '#ef4444',
                fillColor: '#f87171',
                fillOpacity: 0.45,
                weight: 2,
                dashArray: '4, 4'
              }}
            >
              <Popup>
                <div className="p-1 space-y-1.5 text-xs">
                  <div className="font-bold text-red-400 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    Detected Oil Slick
                  </div>
                  <div>Area: <span className="font-mono text-cyan-300 font-semibold">{data.detection.area_sq_km} km²</span></div>
                  <div>Perimeter: <span className="font-mono text-cyan-300">{data.detection.perimeter_km} km</span></div>
                  <div>Confidence: <span className="font-mono text-green-400">{data.detection.confidence * 100}%</span></div>
                </div>
              </Popup>
            </Polygon>

            <Marker position={center} icon={createCentroidIcon()}>
              <Popup>
                <div className="p-1 text-xs">
                  <div className="font-semibold text-slate-200">Spill Centroid</div>
                  <div className="font-mono text-slate-400 text-[11px]">{center[0].toFixed(5)}°N, {center[1].toFixed(5)}°E</div>
                </div>
              </Popup>
            </Marker>
          </>
        )}

        {/* Drift & Hindcast Layers */}
        {showDrift && (
          <>
            {/* Backward Hindcast Path */}
            <Polyline
              positions={hindcastCoords}
              pathOptions={{ color: '#f59e0b', weight: 3, dashArray: '6, 6' }}
            />
            {/* Forward Forecast Path */}
            <Polyline
              positions={forecastCoords}
              pathOptions={{ color: '#06b6d4', weight: 2.5, dashArray: '4, 4' }}
            />

            {/* Estimated Origin Point */}
            <Marker position={originLatLon} icon={createOriginIcon()}>
              <Popup>
                <div className="p-1 space-y-1 text-xs">
                  <div className="font-bold text-amber-400 flex items-center gap-1.5">
                    <Compass className="w-4 h-4" />
                    Probable Spill Origin
                  </div>
                  <div>Estimated Time: <span className="font-mono text-slate-300">{new Date(data.drift.estimated_origin_time).toUTCString()}</span></div>
                  <div>Location: <span className="font-mono text-slate-400">{originLatLon[0].toFixed(4)}°N, {originLatLon[1].toFixed(4)}°E</span></div>
                </div>
              </Popup>
            </Marker>
          </>
        )}

        {/* AIS Vessel Trajectories & Points */}
        {showVessels && data.trajectories.map((traj) => {
          const isSelected = selectedVesselMMSI === traj.mmsi;
          const vesselScore = getVesselScore(traj.mmsi);
          const trajPoints: [number, number][] = traj.positions.map(p => [p.latitude, p.longitude]);
          const lastPosition = traj.positions[traj.positions.length - 1];

          if (!lastPosition) return null;

          return (
            <React.Fragment key={traj.mmsi}>
              {/* Trajectory Polyline */}
              <Polyline
                positions={trajPoints}
                pathOptions={{
                  color: isSelected ? '#ef4444' : '#06b6d4',
                  weight: isSelected ? 4 : 2,
                  opacity: isSelected ? 1 : 0.65
                }}
              />

              {/* Individual Waypoints */}
              {traj.positions.map((pos, idx) => (
                <CircleMarker
                  key={`${traj.mmsi}-${idx}`}
                  center={[pos.latitude, pos.longitude]}
                  radius={isSelected ? 4 : 3}
                  pathOptions={{
                    fillColor: isSelected ? '#ef4444' : '#0891b2',
                    color: '#ffffff',
                    weight: 1,
                    fillOpacity: 0.9
                  }}
                />
              ))}

              {/* Vessel Icon Marker at Latest Position */}
              <Marker
                position={[lastPosition.latitude, lastPosition.longitude]}
                icon={createVesselIcon(traj.vessel_type, isSelected)}
                eventHandlers={{
                  click: () => onSelectVessel && onSelectVessel(traj.mmsi)
                }}
              >
                <Popup>
                  <div className="p-2 space-y-2 text-xs w-60">
                    <div className="flex items-center justify-between border-b border-slate-700 pb-1">
                      <span className="font-bold text-slate-100">{traj.vessel_name}</span>
                      <span className="px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 font-mono text-[10px]">
                        {traj.vessel_type}
                      </span>
                    </div>

                    <div className="space-y-1 font-mono text-slate-300 text-[11px]">
                      <div>MMSI: <span className="text-slate-400">{traj.mmsi}</span></div>
                      <div>IMO: <span className="text-slate-400">{traj.imo || 'N/A'}</span></div>
                      <div>SOG: <span className="text-cyan-400">{lastPosition.sog || 0} knots</span></div>
                      <div>COG: <span className="text-cyan-400">{lastPosition.cog || 0}°</span></div>
                    </div>

                    {vesselScore && (
                      <div className="pt-1.5 border-t border-slate-700 space-y-1">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-400 font-medium">Candidate Score:</span>
                          <span className={`font-mono font-bold text-sm ${vesselScore.composite_score >= 75 ? 'text-red-400' : 'text-amber-400'}`}>
                            {vesselScore.composite_score}%
                          </span>
                        </div>
                        <div className="text-[10px] text-amber-300/90 font-medium">
                          Status: {vesselScore.candidate_status}
                        </div>
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
};
