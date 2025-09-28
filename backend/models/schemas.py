from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Pollutants(BaseModel):
    pm25: float = Field(..., description="PM2.5 concentration in μg/m³")
    pm10: float = Field(..., description="PM10 concentration in μg/m³")
    no2: float = Field(..., description="NO₂ concentration in μg/m³")
    o3: float = Field(..., description="O₃ concentration in μg/m³")

class AQIData(BaseModel):
    city: str = Field(..., description="City name")
    aqi: int = Field(..., ge=0, le=500, description="Air Quality Index")
    category: str = Field(..., description="AQI category")
    pollutants: Pollutants = Field(..., description="Pollutant concentrations")
    source: str = Field(..., description="Data source")
    timestamp: datetime = Field(..., description="Data timestamp")
    real_data: Optional[bool] = Field(None, description="Whether data comes from real sources")
    metadata: Optional[dict] = Field(None, description="Additional metadata")

class ForecastPoint(BaseModel):
    time: datetime = Field(..., description="Forecast timestamp")
    aqi: int = Field(..., ge=0, le=500, description="Predicted AQI")
    category: str = Field(..., description="Predicted AQI category")

class ForecastData(BaseModel):
    city: str = Field(..., description="City name")
    forecast: List[ForecastPoint] = Field(..., description="24-hour forecast data")

class WeatherData(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: int = Field(..., ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    conditions: str = Field(..., description="Weather conditions")
    pressure: float = Field(..., description="Atmospheric pressure in hPa")
    visibility: float = Field(..., description="Visibility in km")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
