"""
OpenWeatherMap Air Pollution API Service
Fast implementation using OpenWeatherMap's air quality data
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

class OpenWeatherAQService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "your_openweather_api_key_here"  # Replace with actual key
        self.client = None
        self.logger = logging.getLogger(__name__)
        
        # City coordinates mapping
        self.city_coords = {
            "piseco lake": {"lat": 43.4531, "lon": -74.5145},
            "new york": {"lat": 40.7128, "lon": -74.0060},
            "los angeles": {"lat": 34.0522, "lon": -118.2437},
            "chicago": {"lat": 41.8781, "lon": -87.6298},
            "houston": {"lat": 29.7604, "lon": -95.3698},
            "phoenix": {"lat": 33.4484, "lon": -112.0740},
            "philadelphia": {"lat": 39.9526, "lon": -75.1652},
            "san francisco": {"lat": 37.7749, "lon": -122.4194},
            "boston": {"lat": 42.3601, "lon": -71.0589},
            "seattle": {"lat": 47.6062, "lon": -122.3321},
            "miami": {"lat": 25.7617, "lon": -80.1918},
            "atlanta": {"lat": 33.7490, "lon": -84.3880},
            "denver": {"lat": 39.7392, "lon": -104.9903},
            "las vegas": {"lat": 36.1699, "lon": -115.1398},
            "detroit": {"lat": 42.3314, "lon": -83.0458},
        }

    async def initialize_client(self):
        """Initialize HTTP client"""
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": "AirVision-App/1.0"}
            )
            self.logger.info("OpenWeatherMap Air Pollution client initialized")

    async def get_aqi_data(self, city: str) -> Dict[str, Any]:
        """Get AQI data from OpenWeatherMap Air Pollution API"""
        await self.initialize_client()
        
        # Get coordinates for city
        coords = self.city_coords.get(city.lower())
        if not coords:
            self.logger.warning(f"No coordinates found for {city}")
            return self._get_fallback_data(city)
        
        try:
            # Call OpenWeatherMap Air Pollution API
            url = "http://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": self.api_key
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 401:
                self.logger.warning("OpenWeatherMap API key invalid or missing")
                return self._get_fallback_data(city)
            elif response.status_code != 200:
                self.logger.error(f"OpenWeatherMap API error: {response.status_code}")
                return self._get_fallback_data(city)
            
            data = response.json()
            return self._process_openweather_data(city, data, coords)
            
        except Exception as e:
            self.logger.error(f"Error fetching OpenWeatherMap data for {city}: {e}")
            return self._get_fallback_data(city)

    def _process_openweather_data(self, city: str, data: Dict, coords: Dict) -> Dict[str, Any]:
        """Process OpenWeatherMap air pollution response"""
        try:
            if not data.get("list"):
                return self._get_fallback_data(city)
            
            # Get current air quality data (first item in list)
            current_data = data["list"][0]
            
            # Extract AQI (OpenWeatherMap uses 1-5 scale, convert to EPA scale)
            ow_aqi = current_data.get("main", {}).get("aqi", 1)
            epa_aqi = self._convert_ow_aqi_to_epa(ow_aqi)
            
            # Extract pollutant components (in μg/m³)
            components = current_data.get("components", {})
            
            pollutants = {
                "pm25": components.get("pm2_5", 0),
                "pm10": components.get("pm10", 0),
                "no2": components.get("no2", 0),
                "o3": components.get("o3", 0),
                "so2": components.get("so2", 0),
                "co": components.get("co", 0) / 1000,  # Convert from μg/m³ to mg/m³
            }
            
            return {
                "city": city,
                "aqi": epa_aqi,
                "category": self._get_aqi_category(epa_aqi),
                "pollutants": {k: round(v, 1) for k, v in pollutants.items() if v > 0},
                "source": "OpenWeatherMap Air Pollution API",
                "timestamp": datetime.utcnow(),
                "coordinates": coords,
                "openweather_aqi": ow_aqi,
                "note": "Real-time air quality data from OpenWeatherMap"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing OpenWeatherMap data: {e}")
            return self._get_fallback_data(city)

    def _convert_ow_aqi_to_epa(self, ow_aqi: int) -> int:
        """Convert OpenWeatherMap AQI (1-5) to EPA AQI (0-500)"""
        conversion_map = {
            1: 25,   # Good
            2: 75,   # Fair
            3: 125,  # Moderate
            4: 175,  # Poor
            5: 275   # Very Poor
        }
        return conversion_map.get(ow_aqi, 75)

    def _get_aqi_category(self, aqi: int) -> str:
        """Get AQI category based on EPA scale"""
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

    def _get_fallback_data(self, city: str) -> Dict[str, Any]:
        """Generate fallback data when API is unavailable"""
        import random
        random.seed(hash(city) + hash(datetime.now().date()))
        
        base_aqi = random.randint(45, 120)
        
        return {
            "city": city,
            "aqi": base_aqi,
            "category": self._get_aqi_category(base_aqi),
            "pollutants": {
                "pm25": round(random.uniform(8, 45), 1),
                "pm10": round(random.uniform(15, 65), 1),
                "no2": round(random.uniform(5, 25), 1),
                "o3": round(random.uniform(40, 85), 1)
            },
            "source": "Fallback Data (OpenWeatherMap API unavailable)",
            "timestamp": datetime.utcnow(),
            "note": "API key required for real data from OpenWeatherMap"
        }