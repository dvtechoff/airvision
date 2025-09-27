"""
No-Database Air Quality Service
Simplified version that works without PostgreSQL, using the existing working services
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from services.openaq_service_http import OpenAQService
from services.tempo_service import TEMPOService

logger = logging.getLogger(__name__)

class SimpleAirQualityService:
    def __init__(self):
        self.openaq_service = OpenAQService()
        self.tempo_service = TEMPOService()
        self.logger = logging.getLogger(__name__)

    async def get_comprehensive_air_quality(self, city: str, include_tempo: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive air quality data using existing working services
        """
        result = {
            "city": city,
            "timestamp": datetime.utcnow(),
            "openaq_data": None,
            "tempo_data": None,
            "combined_aqi": None,
            "data_sources": [],
            "source": "Simple Service (No Database)"
        }
        
        try:
            # Get OpenAQ data (will be mock data since API requires key)
            self.logger.info(f"Getting OpenAQ data for {city}")
            openaq_data = await self.openaq_service.get_aqi_data(city)
            
            if openaq_data:
                result["openaq_data"] = openaq_data
                result["data_sources"].append("OpenAQ Service")
                
            # Get TEMPO data if requested
            if include_tempo:
                self.logger.info(f"Getting TEMPO data for {city}")
                try:
                    async with self.tempo_service:
                        tempo_data = await self.tempo_service.get_tempo_data(city)
                    
                    if tempo_data and "error" not in tempo_data:
                        result["tempo_data"] = tempo_data
                        result["data_sources"].append("NASA TEMPO")
                except Exception as e:
                    self.logger.warning(f"TEMPO data unavailable for {city}: {e}")
            
            # Create combined result prioritizing the best available data
            result["combined_aqi"] = self._create_combined_result(openaq_data, result.get("tempo_data"))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting air quality data for {city}: {e}")
            return {
                "city": city,
                "timestamp": datetime.utcnow(),
                "error": str(e),
                "combined_aqi": {
                    "aqi": 75,
                    "category": "Moderate",
                    "source": "Fallback (Service Error)",
                    "pollutants": {"pm25": 25, "pm10": 45, "no2": 15, "o3": 60}
                }
            }

    def _create_combined_result(self, openaq_data: Optional[Dict], tempo_data: Optional[Dict]) -> Dict[str, Any]:
        """Create combined AQI result from available data sources"""
        
        # Prioritize OpenAQ data if available and reliable
        if openaq_data and openaq_data.get("aqi"):
            return {
                "aqi": openaq_data["aqi"],
                "category": openaq_data["category"],
                "pollutants": openaq_data.get("pollutants", {}),
                "source": openaq_data.get("source", "OpenAQ"),
                "timestamp": openaq_data.get("timestamp", datetime.utcnow()),
                "primary_source": "OpenAQ Ground Measurements" if "Real Data" in openaq_data.get("source", "") else "OpenAQ Mock Data",
                "confidence": "high" if "Real Data" in openaq_data.get("source", "") else "medium",
                "note": openaq_data.get("note", "")
            }
        
        # Fallback to TEMPO data
        elif tempo_data and tempo_data.get("air_quality"):
            tempo_aqi = tempo_data["air_quality"]
            return {
                "aqi": tempo_aqi["aqi"],
                "category": tempo_aqi["category"],
                "pollutants": tempo_data.get("surface_estimates", {}),
                "source": tempo_data.get("source", "NASA TEMPO"),
                "timestamp": tempo_data.get("timestamp", datetime.utcnow()),
                "primary_source": "NASA TEMPO Satellite",
                "confidence": "medium"
            }
        
        # Emergency fallback
        else:
            return {
                "aqi": 85,
                "category": "Moderate",
                "pollutants": {"pm25": 28, "pm10": 52, "no2": 18, "o3": 65},
                "source": "Fallback Data",
                "timestamp": datetime.utcnow(),
                "primary_source": "Emergency Fallback",
                "confidence": "low",
                "note": "No real data sources available - using estimated values"
            }