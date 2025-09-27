"""
Enhanced API routes for comprehensive air quality data
Integrates database-backed location search with real-time data
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import Optional, List
from datetime import datetime

from services.enhanced_air_quality_service import EnhancedAirQualityService
from models.schemas import AQIData, Pollutants

router = APIRouter()

# Service instance
enhanced_service = EnhancedAirQualityService()

@router.get("/enhanced/aqi")
async def get_enhanced_aqi(
    city: str = Query(..., description="City name or location to get AQI data for"),
    include_tempo: bool = Query(True, description="Include NASA TEMPO satellite data"),
    include_raw_data: bool = Query(False, description="Include raw measurement data in response")
):
    """
    Get comprehensive air quality data using the enhanced service that:
    1. Finds closest OpenAQ location from database
    2. Fetches real-time measurements from OpenAQ API  
    3. Gets TEMPO satellite data for the same coordinates
    4. Combines all data sources into a comprehensive assessment
    """
    try:
        result = await enhanced_service.get_comprehensive_air_quality(
            city, 
            include_tempo=include_tempo
        )
        
        # Filter out raw data if not requested
        if not include_raw_data:
            if result.get("openaq_data"):
                # Keep only processed data, remove raw measurements
                openaq_data = result["openaq_data"]
                if "measurements" in openaq_data:
                    del openaq_data["measurements"]
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get enhanced AQI data for {city}: {str(e)}"
        )

@router.get("/enhanced/location/search")
async def search_locations(
    query: str = Query(..., description="Search query for locations"),
    max_results: int = Query(10, description="Maximum number of results to return")
):
    """
    Search for OpenAQ monitoring locations in the database
    """
    try:
        # For now, just find the closest location
        # This could be expanded to return multiple matching locations
        closest_location = await enhanced_service.location_service.find_closest_location(query)
        
        if closest_location:
            return {
                "query": query,
                "results": [closest_location],
                "total_found": 1
            }
        else:
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "message": "No monitoring stations found nearby"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search locations for {query}: {str(e)}"
        )

@router.get("/enhanced/location/{openaq_id}/measurements")
async def get_location_measurements(
    openaq_id: int,
    parameters: Optional[str] = Query(None, description="Comma-separated list of parameters (pm25,pm10,o3,no2)")
):
    """
    Get recent measurements for a specific OpenAQ location ID
    """
    try:
        param_list = parameters.split(",") if parameters else None
        
        data = await enhanced_service.location_service.get_location_air_quality_data(
            openaq_id, 
            parameters=param_list
        )
        
        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error"])
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get measurements for location {openaq_id}: {str(e)}"
        )

@router.get("/enhanced/status")
async def get_service_status():
    """
    Get comprehensive status of all services and data availability
    """
    try:
        return await enhanced_service.get_service_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service status: {str(e)}"
        )

@router.post("/enhanced/setup/database")
async def setup_database(
    background_tasks: BackgroundTasks,
    api_key: Optional[str] = Query(None, description="OpenAQ API key for fetching locations"),
    force_update: bool = Query(False, description="Force update of existing location data")
):
    """
    Initialize database and fetch all OpenAQ locations
    This is a long-running operation that will be executed in the background
    """
    try:
        # Add the database setup as a background task
        background_tasks.add_task(
            _setup_database_background, 
            api_key, 
            force_update
        )
        
        return {
            "message": "Database setup started in background",
            "status": "initiated",
            "note": "Check /enhanced/status endpoint to monitor progress"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start database setup: {str(e)}"
        )

async def _setup_database_background(api_key: Optional[str], force_update: bool):
    """Background task for database setup"""
    try:
        result = await enhanced_service.setup_database_and_fetch_locations(api_key)
        # Log the result - in a production system, you might store this in a task status table
        print(f"Database setup completed: {result}")
    except Exception as e:
        print(f"Database setup failed: {e}")

@router.get("/enhanced/database/stats")
async def get_database_stats():
    """
    Get statistics about the OpenAQ locations database
    """
    try:
        return await enhanced_service.location_service.get_database_stats()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database stats: {str(e)}"
        )

@router.get("/enhanced/compare/{city}")
async def compare_data_sources(
    city: str,
    include_raw: bool = Query(False, description="Include raw measurement data")
):
    """
    Compare air quality data from different sources for analysis
    """
    try:
        result = await enhanced_service.get_comprehensive_air_quality(city, include_tempo=True)
        
        comparison = {
            "location": city,
            "timestamp": datetime.utcnow(),
            "data_sources_found": result.get("data_sources", []),
            "comparison_analysis": {}
        }
        
        # Extract AQI values from different sources
        openaq_aqi = None
        tempo_aqi = None
        
        if result.get("openaq_data") and result["openaq_data"].get("aqi_data"):
            openaq_aqi = result["openaq_data"]["aqi_data"]["aqi"]
        
        if result.get("tempo_data") and result["tempo_data"].get("air_quality"):
            tempo_aqi = result["tempo_data"]["air_quality"]["aqi"]
        
        comparison["comparison_analysis"] = {
            "openaq_aqi": openaq_aqi,
            "tempo_aqi": tempo_aqi,
            "difference": abs(openaq_aqi - tempo_aqi) if openaq_aqi and tempo_aqi else None,
            "correlation": "good" if openaq_aqi and tempo_aqi and abs(openaq_aqi - tempo_aqi) < 25 else "moderate",
            "recommendation": "Use ground measurements" if openaq_aqi else "Use satellite data"
        }
        
        if include_raw:
            comparison["raw_data"] = result
        
        return comparison
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare data sources for {city}: {str(e)}"
        )