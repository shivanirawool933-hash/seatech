from fastapi import APIRouter, UploadFile, File, HTTPException, Body
import pandas as pd
import io
from typing import List, Optional
from app.schemas.dto import VesselTrajectory, AISColumnMapping
from app.services.ais.trajectory import AISTrajectoryProcessor

router = APIRouter()

@router.post("/upload", response_model=List[VesselTrajectory])
async def upload_ais_csv(
    file: UploadFile = File(...),
    mmsi_col: str = "mmsi",
    imo_col: Optional[str] = "imo",
    name_col: Optional[str] = "vessel_name",
    timestamp_col: str = "timestamp",
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    sog_col: Optional[str] = "sog",
    cog_col: Optional[str] = "cog",
    heading_col: Optional[str] = "heading",
    vessel_type_col: Optional[str] = "vessel_type"
):
    """Upload AIS CSV file, validate columns, clean records, and reconstruct trajectories."""
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file format: {e}")

    mapping = AISColumnMapping(
        mmsi_col=mmsi_col,
        imo_col=imo_col,
        name_col=name_col,
        timestamp_col=timestamp_col,
        lat_col=lat_col,
        lon_col=lon_col,
        sog_col=sog_col,
        cog_col=cog_col,
        heading_col=heading_col,
        vessel_type_col=vessel_type_col
    )

    try:
        trajectories = AISTrajectoryProcessor.process_csv(df, mapping)
        return trajectories
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"AIS ingestion failed: {str(e)}")
