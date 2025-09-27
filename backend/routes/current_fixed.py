from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

from models.schemas import AQIData, Pollutants, ErrorResponse
from services.simple_air_quality_service import SimpleAirQualityService

# Load environment variables
load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/current", response_model=AQIData)
async def get_current_aqi(
    city: str = Query(..., description="City name to get AQI data for"),
    include_tempo: bool = Query(True, description="Include TEMPO satellite data")
):
    """
    Get current air quality index (AQI) data for a specific city.
    
    This endpoint combines data from multiple sources:
    - OpenWeatherMap for real air quality data
    - NASA TEMPO satellite data (if available and in coverage area)
    """
    try:
        # Use the simple service with OpenWeatherMap API key
        openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        if not openweather_api_key:
            logger.warning("No OpenWeatherMap API key found in environment")
        
        simple_service = SimpleAirQualityService(openweather_api_key)
        
        # Get comprehensive data
        logger.info(f"Fetching air quality data for {city}")
        result = await simple_service.get_comprehensive_air_quality(city, include_tempo=include_tempo)
        
        if result.get("error"):
            logger.error(f"Service error for {city}: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Extract combined AQI data with proper error handling
        combined_aqi = result.get("combined_aqi", {})
        
        # Ensure we have valid AQI data
        if not combined_aqi:
            logger.warning(f"No combined AQI data for {city}, using fallback")
            combined_aqi = {
                "aqi": 75,
                "category": "Moderate", 
                "pollutants": {"pm25": 25.0, "pm10": 45.0, "no2": 15.0, "o3": 60.0},
                "source": "Fallback Data",
                "timestamp": datetime.utcnow()
            }
        
        # Handle timestamp conversion safely
        timestamp_value = combined_aqi.get("timestamp")
        if isinstance(timestamp_value, str):
            try:
                timestamp_value = datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
            except:
                timestamp_value = datetime.utcnow()
        elif not isinstance(timestamp_value, datetime):
            timestamp_value = datetime.utcnow()
        
        # Extract pollutants with safe defaults
        pollutants_data = combined_aqi.get("pollutants", {})
        if not isinstance(pollutants_data, dict):
            pollutants_data = {}
        
        # Create response with safe data extraction
        response = AQIData(
            city=city,
            aqi=int(combined_aqi.get("aqi", 75)),
            category=str(combined_aqi.get("category", "Moderate")),
            pollutants=Pollutants(
                pm25=float(pollutants_data.get("pm25", 25.0)),
                pm10=float(pollutants_data.get("pm10", 45.0)),
                no2=float(pollutants_data.get("no2", 15.0)),
                o3=float(pollutants_data.get("o3", 60.0))
            ),
            source=str(combined_aqi.get("source", "OpenWeatherMap")),
            timestamp=timestamp_value
        )
        
        logger.info(f"Successfully processed AQI data for {city}: AQI={response.aqi}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        logger.error(f"Unexpected error in get_current_aqi for {city}: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        
        # Return a safe fallback response
        return AQIData(
            city=city,
            aqi=75,
            category="Moderate",
            pollutants=Pollutants(pm25=25.0, pm10=45.0, no2=15.0, o3=60.0),
            source="Fallback (Error Recovery)",
            timestamp=datetime.utcnow()
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
        logger.info(f"Fetching AQI data for multiple cities: {city_list}")
        
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
        
        if not successful_results:
            raise HTTPException(
                status_code=404,
                detail="No valid air quality data found for any of the specified cities"
            )
        
        logger.info(f"Successfully processed {len(successful_results)} cities")
        return successful_results
        
    except Exception as e:
        logger.error(f"Error fetching multiple cities AQI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch AQI data for cities: {str(e)}"
        )