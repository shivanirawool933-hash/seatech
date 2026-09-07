import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.dto import EnvironmentalParameters, GeoBounds, RankingWeights
from app.services.oil_detection.segmentation import OilSpillDetectorModule
from app.services.drift.hindcast import DriftHindcastEngine
from app.services.ais.trajectory import AISTrajectoryProcessor
from app.services.correlation.spatial_temporal import SpatialTemporalCorrelator
from app.services.ranking.scoring import TransparentVesselScoringEngine

def test_ais_correlation_pipeline():
    # 1. Spill & Drift Setup
    detector = OilSpillDetectorModule()
    scene_bounds = GeoBounds(min_lat=24.85, max_lat=25.25, min_lon=54.90, max_lon=55.40)
    spill = detector.detect_spill("TEST-001", scene_bounds)
    
    env = EnvironmentalParameters(
        wind_speed_knots=15.0,
        wind_direction_deg=220.0,
        current_speed_knots=1.5,
        current_direction_deg=40.0
    )
    drift = DriftHindcastEngine.calculate_drift(spill, env)
    
    print(f"Probable Origin: {drift.probable_origin_lat}°N, {drift.probable_origin_lon}°E")
    
    # 2. Test AIS Processing with non-standard column names
    base_ts = datetime.utcnow()
    df_raw = pd.DataFrame([
        # Target 1: Tanker "EVER GIVEN" passing near origin
        {"MMSI_NUM": 477999111, "ShipName": "EVER GIVEN", "ShipType": "Crude Tanker", "BaseDateTime": (base_ts - timedelta(hours=3)).isoformat(), "LAT": drift.probable_origin_lat + 0.002, "LON": drift.probable_origin_lon - 0.003, "Speed": 2.5, "Course": 42},
        {"MMSI_NUM": 477999111, "ShipName": "EVER GIVEN", "ShipType": "Crude Tanker", "BaseDateTime": base_ts.isoformat(), "LAT": drift.probable_origin_lat + 0.03, "LON": drift.probable_origin_lon + 0.04, "Speed": 12.0, "Course": 40},

        # Target 2: Container "MAERSK PEARL" passing 12 km away
        {"MMSI_NUM": 311555222, "ShipName": "MAERSK PEARL", "ShipType": "Container", "BaseDateTime": (base_ts - timedelta(hours=2)).isoformat(), "LAT": drift.probable_origin_lat + 0.10, "LON": drift.probable_origin_lon + 0.08, "Speed": 18.5, "Course": 110},
    ])
    
    trajectories = AISTrajectoryProcessor.process_csv(df_raw)
    print(f"Reconstructed {len(trajectories)} vessel trajectories successfully.")
    
    # 3. Spatial Temporal Correlation & Scoring
    feature_list = []
    for traj in trajectories:
        feats = SpatialTemporalCorrelator.extract_vessel_features(traj, spill, drift)
        if feats:
            feature_list.append(feats)

    weights = RankingWeights(distance_weight=0.30, time_weight=0.25, trajectory_weight=0.25, course_weight=0.10, anomaly_weight=0.10)
    ranked = TransparentVesselScoringEngine.rank_vessels(feature_list, weights)
    
    for r in ranked:
        print(f"\nVessel: {r.vessel_name} (MMSI: {r.mmsi})")
        print(f"  Score: {r.composite_score}% | Status: {r.candidate_status}")
        print(f"  Min dist to origin: {r.min_distance_to_origin_km} km")
        print(f"  Evidence: {r.evidence_reasons[0]}")

if __name__ == "__main__":
    test_ais_correlation_pipeline()
