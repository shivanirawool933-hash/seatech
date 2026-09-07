import math
from datetime import datetime, timedelta
from typing import List, Tuple
from app.schemas.dto import EnvironmentalParameters, DriftAnalysisResult, DriftPathPoint, OilSpillDetectionResult
import logging

logger = logging.getLogger(__name__)

class DriftHindcastEngine:
    """
    Ekman Spiral Ocean Drift & Backward Hindcasting Engine
    Models oil slick transport driven by surface ocean currents (100% advection)
    and surface wind drift (3% windage factor + 25° Ekman angle deflection).
    """
    @staticmethod
    def calculate_drift(
        spill: OilSpillDetectionResult,
        env: EnvironmentalParameters,
        hours_back: float = 12.0,
        hours_forward: float = 12.0,
        step_hours: float = 1.0
    ) -> DriftAnalysisResult:
        
        centroid_lat = spill.centroid_lat
        centroid_lon = spill.centroid_lon
        base_time = datetime.utcnow()

        if env.wind_speed_knots == 0.0 and env.current_speed_knots == 0.0:
            return DriftAnalysisResult(
                probable_origin_lat=centroid_lat,
                probable_origin_lon=centroid_lon,
                estimated_origin_time=base_time - timedelta(hours=hours_back),
                hindcast_path=[DriftPathPoint(timestamp=base_time, latitude=centroid_lat, longitude=centroid_lon, hours_offset=0.0)],
                forecast_path=[DriftPathPoint(timestamp=base_time, latitude=centroid_lat, longitude=centroid_lon, hours_offset=0.0)],
                environmental_data_used=False,
                status_message="Drift analysis unavailable — environmental data not provided."
            )

        # 1 knot = 1.852 km/h
        # 1. Ocean Surface Current Advection (100% vector)
        current_rad = math.radians(env.current_direction_deg)
        curr_u_kmh = env.current_speed_knots * 1.852 * math.sin(current_rad)
        curr_v_kmh = env.current_speed_knots * 1.852 * math.cos(current_rad)

        # 2. Surface Wind Drift (3% windage factor + 25° Ekman Deflection Angle)
        ekman_deflection_deg = 25.0
        effective_wind_dir = (env.wind_direction_deg + ekman_deflection_deg) % 360.0
        wind_rad = math.radians(effective_wind_dir)
        
        wind_u_kmh = (env.wind_speed_knots * 0.03) * 1.852 * math.sin(wind_rad)
        wind_v_kmh = (env.wind_speed_knots * 0.03) * 1.852 * math.cos(wind_rad)

        # Net drift vector (km/h)
        net_u_kmh = curr_u_kmh + wind_u_kmh
        net_v_kmh = curr_v_kmh + wind_v_kmh

        deg_lat_km = 111.0
        deg_lon_km = 111.0 * math.cos(math.radians(centroid_lat))

        # Backward Hindcasting (t = 0 down to -hours_back)
        hindcast_path: List[DriftPathPoint] = []
        curr_lat, curr_lon = centroid_lat, centroid_lon
        
        steps_back = int(hours_back / step_hours)
        for i in range(steps_back + 1):
            h_offset = -i * step_hours
            ts = base_time + timedelta(hours=h_offset)
            
            hindcast_path.append(DriftPathPoint(
                timestamp=ts,
                latitude=round(curr_lat, 6),
                longitude=round(curr_lon, 6),
                hours_offset=h_offset
            ))
            
            # Step backward in time (reverse vector)
            curr_lat -= (net_v_kmh * step_hours) / deg_lat_km
            curr_lon -= (net_u_kmh * step_hours) / deg_lon_km

        probable_origin = hindcast_path[-1]

        # Forward Forecasting (t = 0 up to +hours_forward)
        forecast_path: List[DriftPathPoint] = []
        curr_lat, curr_lon = centroid_lat, centroid_lon
        
        steps_fwd = int(hours_forward / step_hours)
        for i in range(steps_fwd + 1):
            h_offset = i * step_hours
            ts = base_time + timedelta(hours=h_offset)
            
            forecast_path.append(DriftPathPoint(
                timestamp=ts,
                latitude=round(curr_lat, 6),
                longitude=round(curr_lon, 6),
                hours_offset=h_offset
            ))
            
            # Step forward in time
            curr_lat += (net_v_kmh * step_hours) / deg_lat_km
            curr_lon += (net_u_kmh * step_hours) / deg_lon_km

        return DriftAnalysisResult(
            probable_origin_lat=probable_origin.latitude,
            probable_origin_lon=probable_origin.longitude,
            estimated_origin_time=probable_origin.timestamp,
            hindcast_path=hindcast_path,
            forecast_path=forecast_path,
            environmental_data_used=True,
            status_message=f"Ekman ocean drift vector applied ({env.wind_speed_knots}kts wind, {env.current_speed_knots}kts current)."
        )
