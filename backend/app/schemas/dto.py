from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class GeoBounds(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float

class SatelliteSceneInfo(BaseModel):
    scene_id: str
    filename: str
    width: int
    height: int
    crs: str
    bounds: GeoBounds
    acquisition_time: Optional[datetime] = None
    resolution_meters: float
    num_bands: int
    sensor_type: str = "Sentinel-1 SAR"
    metadata_json: Dict[str, Any] = {}

class GeoJSONPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]] # [[[lon, lat], ...]]

class OilSpillDetectionResult(BaseModel):
    detected: bool
    confidence: float
    centroid_lat: float
    centroid_lon: float
    bounding_box: GeoBounds
    area_sq_km: float
    area_sq_m: float
    perimeter_km: float
    estimated_length_m: Optional[float] = None
    estimated_width_m: Optional[float] = None
    polygon: GeoJSONPolygon
    mask_available: bool = True

class AISColumnMapping(BaseModel):
    mmsi_col: str = "mmsi"
    imo_col: Optional[str] = "imo"
    name_col: Optional[str] = "vessel_name"
    timestamp_col: str = "timestamp"
    lat_col: str = "latitude"
    lon_col: str = "longitude"
    sog_col: Optional[str] = "sog"
    cog_col: Optional[str] = "cog"
    heading_col: Optional[str] = "heading"
    vessel_type_col: Optional[str] = "vessel_type"

class AISPositionPoint(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    sog: Optional[float] = None # Speed over ground
    cog: Optional[float] = None # Course over ground
    heading: Optional[float] = None

class VesselTrajectory(BaseModel):
    mmsi: int
    imo: Optional[int] = None
    vessel_name: str
    vessel_type: str = "Unknown"
    positions: List[AISPositionPoint]
    total_distance_km: float = 0.0

class EnvironmentalParameters(BaseModel):
    wind_speed_knots: float
    wind_direction_deg: float
    current_speed_knots: float
    current_direction_deg: float
    observation_time: Optional[datetime] = None

class DriftPathPoint(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    hours_offset: float

class DriftAnalysisResult(BaseModel):
    probable_origin_lat: float
    probable_origin_lon: float
    estimated_origin_time: datetime
    hindcast_path: List[DriftPathPoint]
    forecast_path: List[DriftPathPoint]
    environmental_data_used: bool = True
    status_message: str = "Baseline ocean current & wind vector drift model applied."

class RankingWeights(BaseModel):
    distance_weight: float = Field(0.30, ge=0, le=1)
    time_weight: float = Field(0.25, ge=0, le=1)
    trajectory_weight: float = Field(0.25, ge=0, le=1)
    course_weight: float = Field(0.10, ge=0, le=1)
    anomaly_weight: float = Field(0.10, ge=0, le=1)

class FeatureScoreBreakdown(BaseModel):
    distance_score: float # 0 to 100
    time_score: float # 0 to 100
    trajectory_score: float # 0 to 100
    course_score: float # 0 to 100
    anomaly_score: float # 0 to 100

class VesselCandidateScore(BaseModel):
    vessel_name: str
    mmsi: int
    imo: Optional[int] = None
    vessel_type: str
    composite_score: float # 0 to 100 %
    feature_scores: FeatureScoreBreakdown
    min_distance_to_spill_km: float
    min_distance_to_origin_km: float
    time_delta_hours: float
    evidence_reasons: List[str]
    candidate_status: str = "Potential source vessel" # Legal disclaimers applied
    confidence_level: str = "Medium" # High, Medium, Low
