from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from models.schemas import WeatherData, ErrorResponse
from services.weather_service import WeatherService

router = APIRouter()

@router.get("/weather", response_model=WeatherData)
async def get_weather_data(
    city: str = Query(..., description="City name to get weather data for"),
    units: str = Query("metric", description="Temperature units (metric, imperial, kelvin)")
):
    """
    Get current weather data for a specific city.
    
    This endpoint provides weather information that can influence air quality,
    including temperature, humidity, wind speed, and atmospheric pressure.
    """
    try:
        # Initialize weather service
        weather_service = WeatherService()
        
        # Get weather data
        weather_data = await weather_service.get_weather(city, units)
        
        return weather_data
        
    except Exception as e:
        # Return mock data if weather service fails
        mock_weather = generate_mock_weather(city)
        return mock_weather

def generate_mock_weather(city: str) -> WeatherData:
    """
    Generate mock weather data for demonstration purposes.
    """
    import random
    
    # Simulate realistic weather conditions
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
    
    return WeatherData(
        temperature=round(temperature, 1),
        humidity=humidity,
        wind_speed=round(wind_speed, 1),
        conditions=conditions,
        pressure=round(pressure, 1),
        visibility=round(visibility, 1)
    )

@router.get("/weather/forecast")
async def get_weather_forecast(
    city: str = Query(..., description="City name to get weather forecast for"),
    days: int = Query(5, ge=1, le=10, description="Number of days to forecast (1-10)")
):
    """
    Get weather forecast for a specific city.
    """
    try:
        weather_service = WeatherService()
        forecast = await weather_service.get_forecast(city, days)
        return forecast
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch weather forecast for {city}: {str(e)}"
        )
