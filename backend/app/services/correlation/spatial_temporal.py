from typing import List, Dict, Any, Tuple
from datetime import datetime
from app.schemas.dto import VesselTrajectory, OilSpillDetectionResult, DriftAnalysisResult, AISPositionPoint
from app.services.gis.coordinates import GISCoordinateTransformer

class SpatialTemporalCorrelator:
    @staticmethod
    def extract_vessel_features(
        trajectory: VesselTrajectory,
        spill: OilSpillDetectionResult,
        drift: DriftAnalysisResult,
        search_radius_km: float = 50.0,
        time_window_hours: float = 12.0
    ) -> Dict[str, Any]:
        """
        Extracts spatial and temporal features for a vessel trajectory relative to the oil spill polygon
        and estimated origin point.
        """
        if not trajectory.positions:
            return None

        origin_lat = drift.probable_origin_lat
        origin_lon = drift.probable_origin_lon
        origin_time = drift.estimated_origin_time

        min_dist_spill = float('inf')
        min_dist_origin = float('inf')
        closest_point: AISPositionPoint = trajectory.positions[0]
        min_time_delta_hours = float('inf')

        poly_coords = spill.polygon.coordinates[0]

        for pos in trajectory.positions:
            # Distance to spill polygon boundary
            dist_spill = GISCoordinateTransformer.point_to_polygon_min_distance_km(pos.latitude, pos.longitude, poly_coords)
            if dist_spill < min_dist_spill:
                min_dist_spill = dist_spill

            # Distance to estimated origin
            dist_origin = GISCoordinateTransformer.haversine_distance_km(pos.latitude, pos.longitude, origin_lat, origin_lon)
            if dist_origin < min_dist_origin:
                min_dist_origin = dist_origin
                closest_point = pos

            # Time delta from origin time
            time_delta = abs((pos.timestamp - origin_time).total_seconds()) / 3600.0
            if time_delta < min_time_delta_hours:
                min_time_delta_hours = time_delta

        # Filter out vessels outside the search radius
        if min_dist_spill > search_radius_km and min_dist_origin > search_radius_km:
            return None

        return {
            "vessel_name": trajectory.vessel_name,
            "mmsi": trajectory.mmsi,
            "imo": trajectory.imo,
            "vessel_type": trajectory.vessel_type,
            "min_dist_spill_km": min_dist_spill,
            "min_dist_origin_km": min_dist_origin,
            "min_time_delta_hours": min_time_delta_hours,
            "closest_point": closest_point,
            "total_trajectory_points": len(trajectory.positions),
            "trajectory_distance_km": trajectory.total_distance_km
        }
