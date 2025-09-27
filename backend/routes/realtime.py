from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from models.schemas import AQIData, Pollutants
from services.tempo_service import TEMPOService

router = APIRouter()

@router.get("/realtime/process", response_model=AQIData)
async def process_realtime_data(
    city: str = Query(..., description="City name to process real-time data for")
):
    """Process real-time satellite data with quality filtering and caching."""
    try:
        tempo_service = TEMPOService()
        processed_data = await tempo_service.get_tempo_data(city)
        
        aqi_data = AQIData(
            city=processed_data["city"],
            aqi=processed_data["air_quality"]["aqi"],
            category=processed_data["air_quality"]["category"],
            pollutants=Pollutants(
                pm25=processed_data["surface_estimates"]["pm25"],
                pm10=processed_data["surface_estimates"]["pm10"],
                no2=processed_data["surface_estimates"]["no2"],
                o3=processed_data["surface_estimates"]["o3"]
            ),
            source=processed_data["source"],
            timestamp=processed_data["timestamp"]
        )
        
        return aqi_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process real-time data for {city}: {str(e)}"
        )

@router.get("/realtime/status")
async def get_realtime_status():
    """Get status of real-time processing systems."""
    return {
        "status": "operational",
        "processing_time": "< 1s",
        "data_sources": ["NASA TEMPO Satellite", "OpenAQ"],
        "cache_enabled": True
    }
