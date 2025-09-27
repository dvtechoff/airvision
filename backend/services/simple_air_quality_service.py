"""
No-Database Air Quality Service
Simplified version that works without PostgreSQL, using the existing working services
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from services.openweather_aqi_service import OpenWeatherAQService
from services.tempo_service_earthaccess import tempo_service_earthaccess

logger = logging.getLogger(__name__)

class SimpleAirQualityService:
    def __init__(self, openweather_api_key: Optional[str] = None):
        self.openweather_service = OpenWeatherAQService(openweather_api_key)
        self.tempo_service = tempo_service_earthaccess
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
            # Get OpenWeatherMap data (real air quality data)
            self.logger.info(f"Getting OpenWeatherMap AQI data for {city}")
            async with self.openweather_service:
                openweather_data = await self.openweather_service.get_aqi_data(city)
            
            if openweather_data:
                result["openaq_data"] = openweather_data  # Keep same key for compatibility
                result["data_sources"].append("OpenWeatherMap Air Pollution API")
                
            # Get TEMPO data if requested
            if include_tempo:
                self.logger.info(f"Getting TEMPO data for {city}")
                try:
                    tempo_data = await self.tempo_service.get_tempo_data(city)
                    
                    if tempo_data and tempo_data.get("success"):
                        result["tempo_data"] = tempo_data
                        result["data_sources"].append("NASA TEMPO")
                        self.logger.info(f"Successfully retrieved TEMPO data for {city}")
                    else:
                        self.logger.warning(f"TEMPO data not available for {city}")
                except Exception as e:
                    self.logger.warning(f"TEMPO data unavailable for {city}: {e}")
            
            # Create combined result prioritizing the best available data
            result["combined_aqi"] = self._create_combined_result(openweather_data, result.get("tempo_data"))
            
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

    def _create_combined_result(self, openweather_data: Optional[Dict], tempo_data: Optional[Dict]) -> Dict[str, Any]:
        """Create combined AQI result from available data sources"""
        
        # Prioritize OpenWeatherMap data if available and reliable
        if openweather_data and openweather_data.get("aqi"):
            return {
                "aqi": openweather_data["aqi"],
                "category": openweather_data["category"],
                "pollutants": openweather_data.get("pollutants", {}),
                "source": openweather_data.get("source", "OpenWeatherMap"),
                "timestamp": openweather_data.get("timestamp", datetime.utcnow()),
                "primary_source": "OpenWeatherMap Real Data" if "Real-time" in openweather_data.get("source", "") else "OpenWeatherMap Fallback",
                "confidence": "high" if "Real-time" in openweather_data.get("source", "") else "medium",
                "note": openweather_data.get("note", ""),
                "coordinates": openweather_data.get("coordinates")
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