import os
import sys
import numpy as np

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.satellite.metadata import SatelliteMetadataExtractor
from app.services.oil_detection.segmentation import OilSpillDetectorModule
from app.schemas.dto import GeoBounds

def create_synthetic_geotiff(output_path: str):
    import rasterio
    from rasterio.transform import from_origin
    
    # 256x256 pixel synthetic SAR raster centered around 25.075 N, 55.145 E
    width, height = 256, 256
    transform = from_origin(55.0, 25.2, 0.001, 0.001) # ~100m resolution per pixel
    
    # Background sea surface (medium intensity ~150)
    data = np.random.normal(loc=150, scale=15, size=(height, width)).astype(np.uint16)
    
    # Inject synthetic dark slick region (low backscatter ~30)
    rr, cc = np.ogrid[:height, :width]
    slick_mask = ((rr - 128)**2 / 30.0**2 + (cc - 128)**2 / 60.0**2) <= 1.0
    data[slick_mask] = np.random.normal(loc=30, scale=5, size=np.sum(slick_mask)).astype(np.uint16)
    
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=data.dtype,
        crs='EPSG:4326',
        transform=transform,
    ) as dst:
        dst.write(data, 1)
        dst.update_tags(ACQUISITION_TIME="2026-09-07T10:15:00Z", SENSOR="Sentinel-1 SAR C-Band")

def test_geotiff_pipeline():
    test_dir = os.path.join(os.path.dirname(__file__), "scratch")
    os.makedirs(test_dir, exist_ok=True)
    geotiff_path = os.path.join(test_dir, "test_synthetic_sar.tif")
    
    create_synthetic_geotiff(geotiff_path)
    print(f"Created synthetic GeoTIFF at {geotiff_path}")
    
    # Test Metadata Extractor
    meta = SatelliteMetadataExtractor.extract_metadata(geotiff_path, "TEST-SCENE-001")
    print(f"Extracted CRS: {meta.crs}")
    print(f"Extracted Bounds: {meta.bounds}")
    print(f"Extracted Resolution: {meta.resolution_meters}m")
    
    # Test Detector & Polygonization
    detector = OilSpillDetectorModule()
    spill = detector.detect_spill_from_file(geotiff_path, meta.bounds)
    
    print(f"Spill Detected: {spill.detected}")
    print(f"Area: {spill.area_sq_km} km² ({spill.area_sq_m} m²)")
    print(f"Perimeter: {spill.perimeter_km} km")
    print(f"Centroid: {spill.centroid_lat}°N, {spill.centroid_lon}°E")
    print(f"Polygon vertex count: {len(spill.polygon.coordinates[0])}")

if __name__ == "__main__":
    test_geotiff_pipeline()
