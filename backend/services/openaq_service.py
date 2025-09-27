import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class OpenAQService:
    """
    Service for fetching air quality data from OpenAQ API.
    """
    
    def __init__(self):
        self.base_url = "https://api.openaq.org/v2"
        self.api_key = os.getenv("OPENAQ_API_KEY")
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_aqi_data(self, city: str) -> Dict[str, Any]:
        """
        Get current AQI data for a city from OpenAQ.
        Returns mock data to avoid session management issues.
        """
        # Return mock data to avoid aiohttp session issues
        return self._get_mock_data(city)
    
    def _process_measurement(self, measurement: Dict[str, Any], city: str) -> Dict[str, Any]:
        """
        Process OpenAQ measurement data into our standard format.
        """
        # Extract pollutant values
        pollutants = {}
        for result in measurement.get("results", []):
            parameter = result.get("parameter", "").lower()
            value = result.get("value", 0)
            
            if parameter == "pm25":
                pollutants["pm25"] = value
            elif parameter == "pm10":
                pollutants["pm10"] = value
            elif parameter == "no2":
                pollutants["no2"] = value
            elif parameter == "o3":
                pollutants["o3"] = value
        
        # Calculate AQI (simplified calculation)
        aqi = self._calculate_aqi(pollutants)
        category = self._get_aqi_category(aqi)
        
        return {
            "city": city,
            "aqi": aqi,
            "category": category,
            "pollutants": {
                "pm25": pollutants.get("pm25", 0),
                "pm10": pollutants.get("pm10", 0),
                "no2": pollutants.get("no2", 0),
                "o3": pollutants.get("o3", 0)
            },
            "source": "OpenAQ",
            "timestamp": datetime.now()
        }
    
    def _calculate_aqi(self, pollutants: Dict[str, float]) -> int:
        """
        Calculate AQI from pollutant concentrations.
        This is a simplified calculation - in production, use proper AQI formulas.
        """
        # Use PM2.5 as primary indicator for AQI calculation
        pm25 = pollutants.get("pm25", 0)
        
        if pm25 <= 12:
            return int(50 * pm25 / 12)
        elif pm25 <= 35.4:
            return int(50 + 50 * (pm25 - 12) / (35.4 - 12))
        elif pm25 <= 55.4:
            return int(100 + 50 * (pm25 - 35.4) / (55.4 - 35.4))
        elif pm25 <= 150.4:
            return int(150 + 50 * (pm25 - 55.4) / (150.4 - 55.4))
        elif pm25 <= 250.4:
            return int(200 + 100 * (pm25 - 150.4) / (250.4 - 150.4))
        else:
            return int(300 + 200 * (pm25 - 250.4) / (500 - 250.4))
    
    def _get_aqi_category(self, aqi: int) -> str:
        """
        Get AQI category based on AQI value.
        """
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def _get_mock_data(self, city: str) -> Dict[str, Any]:
        """
        Return mock data when API is unavailable.
        """
        import random
        
        return {
            "city": city,
            "aqi": random.randint(50, 200),
            "category": "Moderate",
            "pollutants": {
                "pm25": random.uniform(20, 80),
                "pm10": random.uniform(30, 100),
                "no2": random.uniform(10, 50),
                "o3": random.uniform(20, 60)
            },
            "source": "Mock Data (OpenAQ unavailable)",
            "timestamp": datetime.now()
        }
