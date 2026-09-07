from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import shutil
from app.schemas.dto import SatelliteSceneInfo, OilSpillDetectionResult
from app.services.satellite.metadata import SatelliteMetadataExtractor
from app.services.oil_detection.segmentation import OilSpillDetectorModule

router = APIRouter()
detector = OilSpillDetectorModule()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../../uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=SatelliteSceneInfo)
async def upload_satellite_image(file: UploadFile = File(...)):
    """Upload georeferenced satellite image (GeoTIFF / Sentinel-1 SAR) and extract metadata."""
    scene_id = f"SCENE-{uuid.uuid4().hex[:8].upper()}"
    file_path = os.path.join(UPLOAD_DIR, f"{scene_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    info = SatelliteMetadataExtractor.extract_metadata(file_path, scene_id)
    return info

@router.post("/detect/{scene_id}", response_model=OilSpillDetectionResult)
async def run_oil_spill_detection(scene_id: str, scene_info: SatelliteSceneInfo):
    """Run PyTorch U-Net oil spill segmentation & GIS polygonization model on satellite scene."""
    # Check if scene file exists in upload store
    target_file = None
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(scene_id):
            target_file = os.path.join(UPLOAD_DIR, fname)
            break

    if target_file and os.path.exists(target_file):
        result = detector.detect_spill_from_file(target_file, scene_info.bounds)
    else:
        result = detector.detect_spill(scene_id, scene_info.bounds)

    return result
