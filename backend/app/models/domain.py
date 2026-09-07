from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class SatelliteScene(Base):
    __tablename__ = "satellite_scenes"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    crs = Column(String)
    min_lat = Column(Float)
    max_lat = Column(Float)
    min_lon = Column(Float)
    max_lon = Column(Float)
    acquisition_time = Column(DateTime, default=datetime.utcnow)
    resolution_meters = Column(Float)
    num_bands = Column(Integer)
    sensor_type = Column(String, default="Sentinel-1 SAR")
    created_at = Column(DateTime, default=datetime.utcnow)

    oil_spills = relationship("OilSpill", back_populates="scene", cascade="all, delete-orphan")

class OilSpill(Base):
    __tablename__ = "oil_spills"

    id = Column(String, primary_key=True, index=True)
    scene_id = Column(String, ForeignKey("satellite_scenes.id"))
    confidence = Column(Float)
    centroid_lat = Column(Float)
    centroid_lon = Column(Float)
    area_sq_km = Column(Float)
    area_sq_m = Column(Float)
    perimeter_km = Column(Float)
    polygon_geojson = Column(JSON)
    bounding_box = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    scene = relationship("SatelliteScene", back_populates="oil_spills")
    scores = relationship("VesselCandidateScoreModel", back_populates="oil_spill", cascade="all, delete-orphan")

class AISVessel(Base):
    __tablename__ = "ais_vessels"

    mmsi = Column(Integer, primary_key=True, index=True)
    imo = Column(Integer, nullable=True)
    vessel_name = Column(String)
    vessel_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    positions = relationship("AISPosition", back_populates="vessel", cascade="all, delete-orphan")

class AISPosition(Base):
    __tablename__ = "ais_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mmsi = Column(Integer, ForeignKey("ais_vessels.mmsi"))
    timestamp = Column(DateTime, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    sog = Column(Float, nullable=True)
    cog = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)

    vessel = relationship("AISVessel", back_populates="positions")

class EnvironmentalObservation(Base):
    __tablename__ = "environmental_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    wind_speed_knots = Column(Float)
    wind_direction_deg = Column(Float)
    current_speed_knots = Column(Float)
    current_direction_deg = Column(Float)

class DriftPrediction(Base):
    __tablename__ = "drift_predictions"

    id = Column(String, primary_key=True, index=True)
    spill_id = Column(String, ForeignKey("oil_spills.id"))
    probable_origin_lat = Column(Float)
    probable_origin_lon = Column(Float)
    estimated_origin_time = Column(DateTime)
    hindcast_path_json = Column(JSON)
    forecast_path_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class VesselCandidateScoreModel(Base):
    __tablename__ = "vessel_candidate_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spill_id = Column(String, ForeignKey("oil_spills.id"))
    mmsi = Column(Integer)
    vessel_name = Column(String)
    composite_score = Column(Float)
    feature_scores_json = Column(JSON)
    evidence_reasons_json = Column(JSON)
    candidate_status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    oil_spill = relationship("OilSpill", back_populates="scores")
