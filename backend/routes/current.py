from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from models.schemas import AQIData, Pollutants, ErrorResponse
from services.simple_air_quality_service import SimpleAirQualityService
from services.tempo_service import TEMPOService

# Load environment variables
load_dotenv()

router = APIRouter()

@router.get("/current", response_model=AQIData)
async def get_current_aqi(
    city: str = Query(..., description="City name to get AQI data for"),
    include_tempo: bool = Query(True, description="Include TEMPO satellite data")
):
    """
    Get current air quality index (AQI) data for a specific city.
    
    This endpoint combines data from multiple sources:
    - OpenAQ for ground-based measurements
    - NASA TEMPO satellite data (if available)
    """
    try:
        # Use the simple service with OpenWeatherMap API key
        openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        simple_service = SimpleAirQualityService(openweather_api_key)
        
        # Get comprehensive data
        result = await simple_service.get_comprehensive_air_quality(city, include_tempo=include_tempo)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Extract combined AQI data
        combined_aqi = result.get("combined_aqi", {})
        openaq_data = result.get("openaq_data", {})
        tempo_data = result.get("tempo_data")
        
        # Create response
        timestamp_value = combined_aqi.get("timestamp")
        if isinstance(timestamp_value, str):
            timestamp_value = datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
        elif timestamp_value is None:
            timestamp_value = datetime.now()
            
        response = AQIData(
            city=city,
            aqi=combined_aqi.get("aqi", 85),
            category=combined_aqi.get("category", "Moderate"),
            pollutants=Pollutants(**combined_aqi.get("pollutants", {
                "pm25": 28, "pm10": 52, "no2": 18, "o3": 65
            })),
            source=f"Combined: {', '.join(result.get('data_sources', ['Fallback']))}",
            timestamp=timestamp_value
        )
        
        return response
        
    except Exception as e:
        print(f"Error details: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch AQI data for {city}: {str(e)}"
        )

@router.get("/current/multiple", response_model=list[AQIData])
async def get_multiple_cities_aqi(
    cities: str = Query(..., description="Comma-separated list of cities")
):
    """
    Get current AQI data for multiple cities.
    """
    try:
        city_list = [city.strip() for city in cities.split(",")]
        
        # Get data for all cities concurrently
        tasks = []
        for city in city_list:
            tasks.append(get_current_aqi(city))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        successful_results = [
            result for result in results 
            if not isinstance(result, Exception)
        ]
        
        return successful_results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch AQI data for multiple cities: {str(e)}"
        )
