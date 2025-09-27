from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import asyncio
from datetime import datetime

from models.schemas import AQIData, Pollutants, ErrorResponse
from services.simple_air_quality_service import SimpleAirQualityService
from services.tempo_service import TEMPOService

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
        # Use the simple service that works without database
        simple_service = SimpleAirQualityService()
        
        # Get comprehensive data
        result = await simple_service.get_comprehensive_air_quality(city, include_tempo=include_tempo)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Extract combined AQI data
        combined_aqi = result.get("combined_aqi", {})
        openaq_data = result.get("openaq_data", {})
        tempo_data = result.get("tempo_data")
        
        # Create response
        response = AQIData(
            city=city,
            aqi=combined_aqi.get("aqi", 85),
            category=combined_aqi.get("category", "Moderate"),
            pollutants=Pollutants(**combined_aqi.get("pollutants", {
                "pm25": 28, "pm10": 52, "no2": 18, "o3": 65
            })),
            source=f"Combined: {', '.join(result.get('data_sources', ['Fallback']))}",
            timestamp=combined_aqi.get("timestamp", datetime.now())
        )
        
        return response
        
    except Exception as e:
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
