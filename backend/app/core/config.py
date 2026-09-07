from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "OILSPILL INTELLIGENCE"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    
    # Database Settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "oilspill_db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Default weights for Vessel Ranking
    DEFAULT_WEIGHT_DISTANCE: float = 0.30
    DEFAULT_WEIGHT_TIME: float = 0.25
    DEFAULT_WEIGHT_TRAJECTORY: float = 0.25
    DEFAULT_WEIGHT_COURSE: float = 0.10
    DEFAULT_WEIGHT_ANOMALY: float = 0.10

    class Config:
        case_sensitive = True

settings = Settings()
