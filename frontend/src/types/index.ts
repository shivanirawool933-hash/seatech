export interface GeoBounds {
  min_lat: number;
  max_lat: number;
  min_lon: number;
  max_lon: number;
}

export interface GeoJSONPolygon {
  type: string;
  coordinates: number[][][]; // [[[lon, lat], ...]]
}

export interface SatelliteSceneInfo {
  scene_id: string;
  filename: string;
  width: number;
  height: number;
  crs: string;
  bounds: GeoBounds;
  acquisition_time?: string;
  resolution_meters: number;
  num_bands: number;
  sensor_type: string;
  metadata_json: Record<string, any>;
}

export interface OilSpillDetectionResult {
  detected: boolean;
  confidence: number;
  centroid_lat: number;
  centroid_lon: number;
  bounding_box: GeoBounds;
  area_sq_km: number;
  area_sq_m: number;
  perimeter_km: number;
  estimated_length_m?: number;
  estimated_width_m?: number;
  polygon: GeoJSONPolygon;
  mask_available: boolean;
}

export interface EnvironmentalParameters {
  wind_speed_knots: number;
  wind_direction_deg: number;
  current_speed_knots: number;
  current_direction_deg: number;
  observation_time?: string;
}

export interface DriftPathPoint {
  timestamp: string;
  latitude: number;
  longitude: number;
  hours_offset: number;
}

export interface DriftAnalysisResult {
  probable_origin_lat: number;
  probable_origin_lon: number;
  estimated_origin_time: string;
  hindcast_path: DriftPathPoint[];
  forecast_path: DriftPathPoint[];
  environmental_data_used: boolean;
  status_message: string;
}

export interface AISPositionPoint {
  timestamp: string;
  latitude: number;
  longitude: number;
  sog?: number;
  cog?: number;
  heading?: number;
}

export interface VesselTrajectory {
  mmsi: number;
  imo?: number;
  vessel_name: string;
  vessel_type: string;
  positions: AISPositionPoint[];
  total_distance_km: number;
}

export interface FeatureScoreBreakdown {
  distance_score: number;
  time_score: number;
  trajectory_score: number;
  course_score: number;
  anomaly_score: number;
}

export interface VesselCandidateScore {
  vessel_name: string;
  mmsi: number;
  imo?: number;
  vessel_type: string;
  composite_score: number;
  feature_scores: FeatureScoreBreakdown;
  min_distance_to_spill_km: number;
  min_distance_to_origin_km: number;
  time_delta_hours: number;
  evidence_reasons: string[];
  candidate_status: string;
  confidence_level: string;
}

export interface RankingWeights {
  distance_weight: number;
  time_weight: number;
  trajectory_weight: number;
  course_weight: number;
  anomaly_weight: number;
}

export interface FullAnalysisResponse {
  satellite: SatelliteSceneInfo;
  detection: OilSpillDetectionResult;
  drift: DriftAnalysisResult;
  trajectories: VesselTrajectory[];
  ranked_vessels: VesselCandidateScore[];
  disclaimer: string;
}
