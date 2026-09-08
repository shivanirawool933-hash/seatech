import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from app.schemas.dto import AISColumnMapping, VesselTrajectory, AISPositionPoint
from app.services.gis.coordinates import GISCoordinateTransformer
import logging

logger = logging.getLogger(__name__)

# NOAA MarineCadastre AIS VesselType Code mapping
MARINECADASTRE_VESSEL_TYPES = {
    1001: "Fishing",
    1002: "Tug / Towing",
    1003: "Cargo / Container",
    1004: "Tanker / Oil Carrier",
    1012: "Passenger",
    1019: "Pleasure Craft",
    1024: "Sailing",
    80: "Tanker",
    70: "Cargo",
    60: "Passenger",
    30: "Fishing"
}

class AISTrajectoryProcessor:
    @staticmethod
    def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        """Fuzzy column resolver matching exact or normalized header strings."""
        cols = list(df.columns)
        for cand in candidates:
            for col in cols:
                if str(col).strip().lower() == cand.strip().lower():
                    return col
        for cand in candidates:
            for col in cols:
                clean_col = re.sub(r'[^a-zA-Z0-9]', '', str(col)).lower()
                clean_cand = re.sub(r'[^a-zA-Z0-9]', '', cand).lower()
                if clean_cand in clean_col or clean_col in clean_cand:
                    return col
        return None

    @staticmethod
    def decode_vessel_type(val: Any) -> str:
        if pd.isnull(val):
            return "Cargo/Tanker"
        try:
            num_code = int(float(val))
            if num_code in MARINECADASTRE_VESSEL_TYPES:
                return MARINECADASTRE_VESSEL_TYPES[num_code]
        except Exception:
            pass
        val_str = str(val).strip()
        return val_str if val_str else "Cargo/Tanker"

    @staticmethod
    def process_csv(
        df: pd.DataFrame, 
        mapping: Optional[AISColumnMapping] = None
    ) -> List[VesselTrajectory]:
        """
        Ingests MarineCadastre / NOAA standard AIS CSV datasets automatically,
        resolves column headers (MMSI, BaseDateTime, LAT, LON, SOG, COG, VesselName, VesselType),
        cleans coordinates (-90 to 90 lat / -180 to 180 lon), filters GPS spikes,
        sorts chronologically by MMSI & timestamp, and reconstructs trajectories.
        """
        mmsi_c = AISTrajectoryProcessor._find_column(df, ["mmsi", "mmsi_num", "vessel_mmsi", "target_mmsi", "id"]) or "MMSI"
        time_c = AISTrajectoryProcessor._find_column(df, ["basedatetime", "timestamp", "time", "date_time", "datetime", "ts"]) or "BaseDateTime"
        lat_c = AISTrajectoryProcessor._find_column(df, ["lat", "latitude", "latitude_degrees", "y"]) or "LAT"
        lon_c = AISTrajectoryProcessor._find_column(df, ["lon", "longitude", "long", "longitude_degrees", "x"]) or "LON"
        
        imo_c = AISTrajectoryProcessor._find_column(df, ["imo", "imo_num", "vessel_imo"])
        name_c = AISTrajectoryProcessor._find_column(df, ["vesselname", "vessel_name", "ship_name", "name"])
        sog_c = AISTrajectoryProcessor._find_column(df, ["sog", "speed", "speed_over_ground", "knots"])
        cog_c = AISTrajectoryProcessor._find_column(df, ["cog", "course", "course_over_ground", "heading_deg"])
        head_c = AISTrajectoryProcessor._find_column(df, ["heading", "true_heading", "hdg"])
        type_c = AISTrajectoryProcessor._find_column(df, ["vesseltype", "vessel_type", "ship_type", "type", "cargo"])

        if mapping:
            if mapping.mmsi_col in df.columns: mmsi_c = mapping.mmsi_col
            if mapping.timestamp_col in df.columns: time_c = mapping.timestamp_col
            if mapping.lat_col in df.columns: lat_c = mapping.lat_col
            if mapping.lon_col in df.columns: lon_c = mapping.lon_col

        if mmsi_c not in df.columns or time_c not in df.columns or lat_c not in df.columns or lon_c not in df.columns:
            raise ValueError(f"Missing required AIS columns. Found columns: {list(df.columns)}")

        rename_dict = {
            mmsi_c: "mmsi",
            time_c: "timestamp",
            lat_c: "latitude",
            lon_c: "longitude"
        }
        if imo_c and imo_c in df.columns: rename_dict[imo_c] = "imo"
        if name_c and name_c in df.columns: rename_dict[name_c] = "vessel_name"
        if sog_c and sog_c in df.columns: rename_dict[sog_c] = "sog"
        if cog_c and cog_c in df.columns: rename_dict[cog_c] = "cog"
        if head_c and head_c in df.columns: rename_dict[head_c] = "heading"
        if type_c and type_c in df.columns: rename_dict[type_c] = "vessel_type"

        work_df = df.rename(columns=rename_dict).copy()

        work_df = work_df.dropna(subset=["mmsi", "latitude", "longitude", "timestamp"])
        work_df["latitude"] = pd.to_numeric(work_df["latitude"], errors="coerce")
        work_df["longitude"] = pd.to_numeric(work_df["longitude"], errors="coerce")
        work_df["mmsi"] = pd.to_numeric(work_df["mmsi"], errors="coerce").fillna(0).astype(int)

        work_df = work_df[(work_df["mmsi"] >= 100000000) & (work_df["mmsi"] <= 999999999)]

        work_df = work_df[
            (work_df["latitude"] >= -90.0) & (work_df["latitude"] <= 90.0) &
            (work_df["longitude"] >= -180.0) & (work_df["longitude"] <= 180.0)
        ]

        work_df["timestamp"] = pd.to_datetime(work_df["timestamp"], errors="coerce")
        work_df = work_df.dropna(subset=["timestamp"])

        if "imo" not in work_df.columns: work_df["imo"] = None
        if "vessel_name" not in work_df.columns: work_df["vessel_name"] = work_df["mmsi"].apply(lambda m: f"Vessel_{m}")
        if "sog" not in work_df.columns: work_df["sog"] = 0.0
        if "cog" not in work_df.columns: work_df["cog"] = 0.0
        if "heading" not in work_df.columns: work_df["heading"] = 0.0
        if "vessel_type" not in work_df.columns: work_df["vessel_type"] = "Cargo/Tanker"

        work_df["sog"] = pd.to_numeric(work_df["sog"], errors="coerce").fillna(0.0)
        work_df = work_df[work_df["sog"] <= 60.0]

        work_df = work_df.sort_values(by=["mmsi", "timestamp"])

        trajectories: List[VesselTrajectory] = []

        for mmsi, group in work_df.groupby("mmsi"):
            positions: List[AISPositionPoint] = []
            total_dist_km = 0.0
            prev_lat, prev_lon = None, None

            for _, row in group.iterrows():
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                ts = row["timestamp"].to_pydatetime()

                if prev_lat is not None and prev_lon is not None:
                    dist = GISCoordinateTransformer.haversine_distance_km(prev_lat, prev_lon, lat, lon)
                    if dist < 500.0:
                        total_dist_km += dist

                prev_lat, prev_lon = lat, lon

                positions.append(AISPositionPoint(
                    timestamp=ts,
                    latitude=lat,
                    longitude=lon,
                    sog=float(row["sog"]) if pd.notnull(row["sog"]) else None,
                    cog=float(row["cog"]) if pd.notnull(row["cog"]) else None,
                    heading=float(row["heading"]) if pd.notnull(row["heading"]) else None
                ))

            if positions:
                first_row = group.iloc[0]
                v_name = str(first_row["vessel_name"]) if pd.notnull(first_row["vessel_name"]) else f"Vessel {mmsi}"
                v_type = AISTrajectoryProcessor.decode_vessel_type(first_row.get("vessel_type"))
                
                raw_imo = first_row.get("imo")
                v_imo = None
                if pd.notnull(raw_imo):
                    imo_digits = re.sub(r'\D', '', str(raw_imo))
                    if imo_digits and len(imo_digits) >= 7:
                        v_imo = int(imo_digits[:7])

                trajectories.append(VesselTrajectory(
                    mmsi=int(mmsi),
                    imo=v_imo,
                    vessel_name=v_name,
                    vessel_type=v_type,
                    positions=positions,
                    total_distance_km=round(total_dist_km, 2)
                ))

        return trajectories
