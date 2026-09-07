from fastapi import APIRouter
from app.api.v1.endpoints import satellite, ais, analysis

api_router = APIRouter()

api_router.include_router(satellite.router, prefix="/satellite", tags=["satellite"])
api_router.include_router(ais.router, prefix="/ais", tags=["ais"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
