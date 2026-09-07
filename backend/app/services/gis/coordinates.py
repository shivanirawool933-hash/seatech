import math
from typing import List, Tuple, Dict, Any, Optional
from shapely.geometry import Polygon, Point, MultiPolygon, shape
from shapely.ops import transform
import pyproj
from functools import partial
import logging

logger = logging.getLogger(__name__)

class GISCoordinateTransformer:
    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates exact spherical distance between two points in km."""
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def reproject_polygon(poly: Polygon, source_crs: str, target_crs: str = "EPSG:4326") -> Polygon:
        """Reprojects Shapely Polygon from source CRS (e.g. EPSG:32639) to target CRS (EPSG:4326 WGS84)."""
        if source_crs == target_crs or "4326" in source_crs:
            return poly
        try:
            project = partial(
                pyproj.transform,
                pyproj.Proj(source_crs),
                pyproj.Proj(target_crs)
            )
            return transform(project, poly)
        except Exception as e:
            logger.warning(f"Polygon CRS reprojection failed ({source_crs} -> {target_crs}): {e}")
            return poly

    @staticmethod
    def calculate_polygon_metrics(coords_lon_lat: List[List[float]]) -> Tuple[float, float, float]:
        """
        Takes lon/lat coordinates polygon and returns (area_sq_km, area_sq_m, perimeter_km)
        using equal-area projection transformation (World Mollweide ESRI:54009).
        """
        try:
            poly = Polygon(coords_lon_lat)
            if not poly.is_valid:
                poly = poly.buffer(0)
            
            project = partial(
                pyproj.transform,
                pyproj.Proj("EPSG:4326"),
                pyproj.Proj("ESRI:54009") # World Mollweide equal area
            )
            poly_projected = transform(project, poly)
            area_sq_m = abs(poly_projected.area)
            area_sq_km = area_sq_m / 1e6
            perimeter_km = abs(poly_projected.length) / 1000.0
            
            return area_sq_km, area_sq_m, perimeter_km
        except Exception:
            poly = Polygon(coords_lon_lat)
            center_lat = poly.centroid.y
            deg_lat_km = 111.0
            deg_lon_km = 111.0 * math.cos(math.radians(center_lat))
            
            km_coords = [(x * deg_lon_km, y * deg_lat_km) for x, y in coords_lon_lat]
            poly_km = Polygon(km_coords)
            area_sq_km = abs(poly_km.area)
            perimeter_km = abs(poly_km.length)
            return area_sq_km, area_sq_km * 1e6, perimeter_km

    @staticmethod
    def point_to_polygon_min_distance_km(point_lat: float, point_lon: float, poly_coords_lon_lat: List[List[float]]) -> float:
        """Calculates minimum distance from a point (lat, lon) to polygon boundary in km."""
        poly = Polygon(poly_coords_lon_lat)
        pt = Point(point_lon, point_lat)
        
        if poly.contains(pt):
            return 0.0
        
        min_dist = float('inf')
        for coord in poly_coords_lon_lat:
            dist = GISCoordinateTransformer.haversine_distance_km(point_lat, point_lon, coord[1], coord[0])
            if dist < min_dist:
                min_dist = dist
        return min_dist
