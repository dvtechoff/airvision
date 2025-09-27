from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

from models.schemas import AQIData, Pollutants, ErrorResponse
from services.openweather_aqi_service import OpenWeatherAQService

# Load environment variables
load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/current-fast", response_model=AQIData)
async def get_current_aqi_fast(
    city: str = Query(..., description="City name to get AQI data for")
):
    """
    Get current air quality index (AQI) data for a specific city - FAST VERSION.
    
    This endpoint only uses OpenWeatherMap for fastest response time.
    """
    try:
        # Use direct OpenWeatherMap service for fastest response
        openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        if not openweather_api_key:
            logger.warning("No OpenWeatherMap API key found in environment")
            raise HTTPException(status_code=500, detail="API key not configured")
        
        openweather_service = OpenWeatherAQService(openweather_api_key)
        
        # Get fast air quality data
        logger.info(f"Fetching FAST air quality data for {city}")
        start_time = datetime.now()
        
        result = await openweather_service.get_aqi_data(city)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        logger.info(f"Fast AQI data retrieved in {processing_time:.2f}ms for {city}")
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No air quality data found for {city}")
        
        # Create response in the expected format
        response_data = {
            "city": city,
            "aqi": result.get("aqi", 0),
            "category": result.get("category", "Unknown"),
            "pollutants": {
                "pm25": result.get("pollutants", {}).get("pm25", 0),
                "pm10": result.get("pollutants", {}).get("pm10", 0),
                "no2": result.get("pollutants", {}).get("no2", 0),
                "o3": result.get("pollutants", {}).get("o3", 0),
            },
            "source": "OpenWeatherMap Air Pollution API (Real-time)",
            "timestamp": datetime.utcnow().isoformat(),
            "real_data": True,
            "processing_time_ms": processing_time
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting fast AQI data for {city}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve air quality data: {str(e)}")