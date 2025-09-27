from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from datetime import datetime

from services.openaq_service import OpenAQService
from services.tempo_service import TEMPOService

router = APIRouter()

@router.get("/test/openaq", response_model=Dict[str, Any])
async def test_openaq_real_data(
    city: str = Query(..., description="City name to test OpenAQ real data for")
):
    """
    Test endpoint to specifically fetch real OpenAQ data and show if it's available.
    """
    try:
        async with OpenAQService() as service:
            result = await service.get_aqi_data(city)
            
            # Add test metadata
            result["test_info"] = {
                "endpoint": "test_openaq_real_data",
                "data_type": "real" if "Real Data" in result.get("source", "") else "mock",
                "api_available": "Real Data" in result.get("source", ""),
                "tested_at": datetime.now().isoformat()
            }
            
            return result
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test OpenAQ data for {city}: {str(e)}"
        )

@router.get("/test/tempo", response_model=Dict[str, Any])
async def test_tempo_real_data(
    city: str = Query(..., description="City name to test TEMPO real data for")
):
    """
    Test endpoint to specifically fetch real TEMPO data and show if it's available.
    """
    try:
        async with TEMPOService() as service:
            result = await service.get_tempo_data(city)
            
            # Add test metadata
            result["test_info"] = {
                "endpoint": "test_tempo_real_data",
                "data_type": "real" if "Real Data" in result.get("source", "") else "mock",
                "api_available": "Real Data" in result.get("source", ""),
                "tested_at": datetime.now().isoformat(),
                "credentials_configured": bool(service.username and service.password)
            }
            
            return result
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test TEMPO data for {city}: {str(e)}"
        )

@router.get("/test/data-sources", response_model=Dict[str, Any])
async def test_all_data_sources(
    city: str = Query(..., description="City name to test all data sources for")
):
    """
    Test endpoint to check the availability of all data sources.
    """
    try:
        results = {
            "city": city,
            "test_timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        # Test OpenAQ
        try:
            async with OpenAQService() as openaq_service:
                openaq_result = await openaq_service.get_aqi_data(city)
                results["sources"]["openaq"] = {
                    "available": "Real Data" in openaq_result.get("source", ""),
                    "source": openaq_result.get("source", ""),
                    "aqi": openaq_result.get("aqi", 0),
                    "status": "success"
                }
        except Exception as e:
            results["sources"]["openaq"] = {
                "available": False,
                "source": "Error",
                "error": str(e),
                "status": "error"
            }
        
        # Test TEMPO
        try:
            async with TEMPOService() as tempo_service:
                tempo_result = await tempo_service.get_tempo_data(city)
                results["sources"]["tempo"] = {
                    "available": "Real Data" in tempo_result.get("source", ""),
                    "source": tempo_result.get("source", ""),
                    "has_measurements": bool(tempo_result.get("measurements")),
                    "credentials_configured": bool(tempo_service.username and tempo_service.password),
                    "status": "success"
                }
        except Exception as e:
            results["sources"]["tempo"] = {
                "available": False,
                "source": "Error",
                "error": str(e),
                "status": "error"
            }
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test data sources for {city}: {str(e)}"
        )