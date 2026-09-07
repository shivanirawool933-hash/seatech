from fastapi import APIRouter, Body
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.schemas.dto import (
    SatelliteSceneInfo, OilSpillDetectionResult, EnvironmentalParameters, 
    DriftAnalysisResult, VesselTrajectory, VesselCandidateScore, RankingWeights, GeoBounds
)
from app.services.satellite.metadata import SatelliteMetadataExtractor
from app.services.oil_detection.segmentation import OilSpillDetectorModule
from app.services.drift.hindcast import DriftHindcastEngine
from app.services.correlation.spatial_temporal import SpatialTemporalCorrelator
from app.services.ranking.scoring import TransparentVesselScoringEngine
from app.services.ais.trajectory import AISTrajectoryProcessor
import pandas as pd

router = APIRouter()

class AnalysisRunRequest(BaseModel_Request := type("AnalysisRunRequest", (), {})):
    pass

@router.post("/run-full-analysis")
async def run_full_analysis(payload: Dict[str, Any] = Body(...)):
    """
    Unified OilSpill Intelligence Pipeline Run:
    Satellite Scene -> Detection -> Drift Engine -> AIS Correlation -> Vessel Ranking
    """
    env_data = payload.get("environmental", {
        "wind_speed_knots": 14.5,
        "wind_direction_deg": 225.0,
        "current_speed_knots": 1.2,
        "current_direction_deg": 45.0
    })
    env_params = EnvironmentalParameters(**env_data)

    weights_data = payload.get("weights", {
        "distance_weight": 0.30,
        "time_weight": 0.25,
        "trajectory_weight": 0.25,
        "course_weight": 0.10,
        "anomaly_weight": 0.10
    })
    weights = RankingWeights(**weights_data)

    # 1. Satellite Metadata & Detection
    scene_bounds = GeoBounds(min_lat=24.85, max_lat=25.25, min_lon=54.90, max_lon=55.40)
    detector = OilSpillDetectorModule()
    spill = detector.detect_spill("SCENE-001", scene_bounds)

    # 2. Ocean Drift & Backward Hindcasting
    drift = DriftHindcastEngine.calculate_drift(spill, env_params)

    # 3. Generate or Correlate AIS Trajectories (Sample Maritime Dataset for UI initialization)
    origin_lat = drift.probable_origin_lat
    origin_lon = drift.probable_origin_lon
    base_ts = datetime.utcnow()

    # Synthetic realistic AIS vessels in Arabian Gulf / Strait area
    sample_df = pd.DataFrame([
        # Vessel 1: Crude Oil Tanker "PACIFIC TRADER" - Passes right by origin 1.2 km away
        {"mmsi": 477123400, "imo": 9812345, "vessel_name": "PACIFIC TRADER", "vessel_type": "Oil Tanker", "timestamp": (base_ts - timedelta(hours=3)).isoformat(), "latitude": origin_lat + 0.01, "longitude": origin_lon - 0.02, "sog": 11.2, "cog": 48.0},
        {"mmsi": 477123400, "imo": 9812345, "vessel_name": "PACIFIC TRADER", "vessel_type": "Oil Tanker", "timestamp": (base_ts - timedelta(hours=1.5)).isoformat(), "latitude": origin_lat + 0.005, "longitude": origin_lon + 0.005, "sog": 3.1, "cog": 45.0}, # Slow speed near origin
        {"mmsi": 477123400, "imo": 9812345, "vessel_name": "PACIFIC TRADER", "vessel_type": "Oil Tanker", "timestamp": base_ts.isoformat(), "latitude": origin_lat + 0.03, "longitude": origin_lon + 0.04, "sog": 12.5, "cog": 42.0},

        # Vessel 2: Container Ship "MSC OCEANUS" - Passes 8.5 km away
        {"mmsi": 311890123, "imo": 9745678, "vessel_name": "MSC OCEANUS", "vessel_type": "Container Ship", "timestamp": (base_ts - timedelta(hours=4)).isoformat(), "latitude": origin_lat + 0.07, "longitude": origin_lon - 0.05, "sog": 18.5, "cog": 120.0},
        {"mmsi": 311890123, "imo": 9745678, "vessel_name": "MSC OCEANUS", "vessel_type": "Container Ship", "timestamp": (base_ts - timedelta(hours=1)).isoformat(), "latitude": origin_lat + 0.06, "longitude": origin_lon + 0.03, "sog": 19.0, "cog": 118.0},

        # Vessel 3: Chemical Tanker "GULF VOYAGER" - Passes 18.2 km away
        {"mmsi": 636098765, "imo": 9654321, "vessel_name": "GULF VOYAGER", "vessel_type": "Chemical Tanker", "timestamp": (base_ts - timedelta(hours=5)).isoformat(), "latitude": origin_lat - 0.15, "longitude": origin_lon - 0.12, "sog": 10.8, "cog": 210.0},
        {"mmsi": 636098765, "imo": 9654321, "vessel_name": "GULF VOYAGER", "vessel_type": "Chemical Tanker", "timestamp": (base_ts - timedelta(hours=2)).isoformat(), "latitude": origin_lat - 0.12, "longitude": origin_lon - 0.18, "sog": 11.5, "cog": 208.0},
    ])

    trajectories = AISTrajectoryProcessor.process_csv(sample_df)

    # 4. Feature Extraction & Ranking
    feature_list = []
    for traj in trajectories:
        feats = SpatialTemporalCorrelator.extract_vessel_features(traj, spill, drift)
        if feats:
            feature_list.append(feats)

    ranked_vessels = TransparentVesselScoringEngine.rank_vessels(feature_list, weights)

    return {
        "satellite": {
            "scene_id": "SCENE-2026-S1A",
            "filename": "S1A_IW_GRDH_1SDV_20260907.tif",
            "bounds": scene_bounds,
            "crs": "EPSG:4326",
            "sensor": "Sentinel-1 SAR C-Band"
        },
        "detection": spill,
        "drift": drift,
        "trajectories": trajectories,
        "ranked_vessels": ranked_vessels,
        "disclaimer": "Scores and status designations are calculated analytical approximations for decision support and do not constitute legal proof of liability."
    }
