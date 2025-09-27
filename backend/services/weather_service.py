import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    """
    Service for fetching weather data from OpenWeatherMap API.
    """
    
    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_weather(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather data for a city from OpenWeatherMap.
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            if not self.api_key:
                return self._get_mock_weather(city)
            
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_weather_data(data)
                else:
                    return self._get_mock_weather(city)
                    
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self._get_mock_weather(city)
    
    async def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """
        Get weather forecast for a city.
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            if not self.api_key:
                return self._get_mock_forecast(city, days)
            
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_forecast_data(data, days)
                else:
                    return self._get_mock_forecast(city, days)
                    
        except Exception as e:
            print(f"Error fetching weather forecast: {e}")
            return self._get_mock_forecast(city, days)
    
    def _process_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process OpenWeatherMap data into our standard format.
        """
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        visibility = data.get("visibility", 10000) / 1000  # Convert to km
        
        return {
            "temperature": round(main.get("temp", 0), 1),
            "humidity": main.get("humidity", 0),
            "wind_speed": round(wind.get("speed", 0), 1),
            "conditions": weather.get("description", "Unknown").title(),
            "pressure": round(main.get("pressure", 1013), 1),
            "visibility": round(visibility, 1)
        }
    
    def _process_forecast_data(self, data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """
        Process forecast data.
        """
        forecasts = []
        for item in data.get("list", [])[:days * 8]:
            forecast = {
                "datetime": item.get("dt_txt"),
                "temperature": round(item.get("main", {}).get("temp", 0), 1),
                "humidity": item.get("main", {}).get("humidity", 0),
                "wind_speed": round(item.get("wind", {}).get("speed", 0), 1),
                "conditions": item.get("weather", [{}])[0].get("description", "Unknown").title(),
                "pressure": round(item.get("main", {}).get("pressure", 1013), 1)
            }
            forecasts.append(forecast)
        
        return {
            "city": data.get("city", {}).get("name", "Unknown"),
            "forecasts": forecasts
        }
    
    def _get_mock_weather(self, city: str) -> Dict[str, Any]:
        """
        Return mock weather data when API is unavailable.
        """
        import random
        
        temperature = random.uniform(15, 35)
        humidity = random.randint(30, 90)
        wind_speed = random.uniform(2, 15)
        pressure = random.uniform(1000, 1020)
        visibility = random.uniform(3, 15)
        
        # Weather conditions based on temperature and humidity
        if temperature > 30 and humidity > 70:
            conditions = "Haze"
        elif temperature < 10:
            conditions = "Clear"
        elif humidity > 80:
            conditions = "Cloudy"
        elif wind_speed > 10:
            conditions = "Windy"
        else:
            conditions = "Partly Cloudy"
        
        return {
            "temperature": round(temperature, 1),
            "humidity": humidity,
            "wind_speed": round(wind_speed, 1),
            "conditions": conditions,
            "pressure": round(pressure, 1),
            "visibility": round(visibility, 1)
        }
    
    def _get_mock_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """
        Return mock forecast data.
        """
        import random
        from datetime import datetime, timedelta
        
        forecasts = []
        for i in range(days * 8):  # 8 forecasts per day
            temperature = random.uniform(15, 35)
            humidity = random.randint(30, 90)
            wind_speed = random.uniform(2, 15)
            pressure = random.uniform(1000, 1020)
            
            forecast = {
                "datetime": (datetime.now() + timedelta(hours=i*3)).strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": round(temperature, 1),
                "humidity": humidity,
                "wind_speed": round(wind_speed, 1),
                "conditions": "Partly Cloudy",
                "pressure": round(pressure, 1)
            }
            forecasts.append(forecast)
        
        return {
            "city": city,
            "forecasts": forecasts
        }
