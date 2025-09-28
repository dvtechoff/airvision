from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional

from routes import current, forecast, weather
from routes import realtime_test as realtime
from services.enhanced_forecast_service import EnhancedForecastService
from services.openweather_aqi_service import OpenWeatherAQService
from services.tempo_service import TEMPOService
from services.gemini_ai_service import GeminiAIService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="TEMPO Air Quality API",
    description="Real-time air quality monitoring using NASA TEMPO satellite data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "https://tempo-air-quality.vercel.app","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(current.router, prefix="/api", tags=["current"])
app.include_router(forecast.router, prefix="/api", tags=["forecast"])
app.include_router(weather.router, prefix="/api", tags=["weather"])
app.include_router(realtime.router, prefix="/api", tags=["realtime"])

@app.get("/")
async def root():
    return {
        "message": "TEMPO Air Quality API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "current": "/api/current?city=New York",
            "forecast": "/api/forecast?city=New York", 
            "weather": "/api/weather?city=New York",
            "realtime": "/api/realtime/process?city=New York",
            "verify_forecast_data": "/api/verify-forecast-data?city=New York&hours=3",
            "data_sources": "/api/data-sources-status"
        }
    }

@app.get("/api/verify-forecast-data")
async def verify_forecast_data(
    city: str = Query(..., description="City name to verify data for"),
    hours: int = Query(3, ge=1, le=24, description="Number of hours to analyze")
):
    """
    Comprehensive data verification endpoint showing all data sources
    used in the forecasting system for complete transparency.
    """
    try:
        # Initialize services
        forecast_service = EnhancedForecastService()
        openweather_service = OpenWeatherAQService(os.getenv('OPENWEATHER_API_KEY'))
        tempo_service = TEMPOService()
        
        verification_data = {
            "city": city,
            "timestamp": datetime.now().isoformat(),
            "verification_type": "Complete Forecast Data Verification",
            "status": "success"
        }
        
        # 1. Get OpenWeatherMap baseline data
        try:
            openweather_data = await openweather_service.get_aqi_data(city)
            verification_data["openweathermap_data"] = {
                "status": "success" if openweather_data else "no_data",
                "data": openweather_data,
                "source": "OpenWeatherMap Air Pollution API",
                "purpose": "Ground-level pollutant baseline measurements"
            }
        except Exception as e:
            verification_data["openweathermap_data"] = {
                "status": "error",
                "error": str(e),
                "source": "OpenWeatherMap Air Pollution API"
            }
        
        # 2. Get TEMPO satellite data
        try:
            tempo_data = await tempo_service.get_tempo_data(city)
            verification_data["tempo_satellite_data"] = {
                "status": "success" if tempo_data else "no_data",
                "data": tempo_data,
                "source": "NASA TEMPO Satellite",
                "purpose": "Atmospheric column measurements and quality flags"
            }
        except Exception as e:
            verification_data["tempo_satellite_data"] = {
                "status": "error", 
                "error": str(e),
                "source": "NASA TEMPO Satellite"
            }
        
        # 3. Get actual forecast with detailed breakdown
        try:
            forecast_result = await forecast_service.get_forecast(city, hours)
            forecast_points_data = []
            
            for i, point in enumerate(forecast_result.forecast):
                point_data = {
                    "hour": i,
                    "time": point.time.isoformat(),
                    "predicted_aqi": point.aqi,
                    "category": point.category,
                    "factors_used": await get_factors_for_hour(
                        city, i, openweather_data, tempo_data
                    )
                }
                forecast_points_data.append(point_data)
            
            verification_data["forecast_predictions"] = {
                "status": "success",
                "city": forecast_result.city,
                "total_hours": len(forecast_result.forecast),
                "predictions": forecast_points_data,
                "algorithm": "TEMPO-Enhanced Multi-Factor Prediction"
            }
            
        except Exception as e:
            verification_data["forecast_predictions"] = {
                "status": "error",
                "error": str(e)
            }
        
        # 4. Factor Analysis Breakdown
        verification_data["factor_analysis"] = await get_detailed_factor_analysis(
            city, openweather_data, tempo_data
        )
        
        # 5. Data Quality Assessment
        verification_data["data_quality"] = {
            "openweather_quality": assess_openweather_quality(openweather_data),
            "tempo_quality": assess_tempo_quality(tempo_data),
            "overall_confidence": calculate_overall_confidence(
                openweather_data, tempo_data
            )
        }
        
        return verification_data
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/data-sources-status")
async def data_sources_status():
    """
    Check the status of all data sources used in the forecasting system.
    """
    try:
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": {}
        }
        
        # Check OpenWeatherMap API
        try:
            openweather_service = OpenWeatherAQService(os.getenv('OPENWEATHER_API_KEY'))
            test_data = await openweather_service.get_aqi_data("New York")
            status_data["data_sources"]["openweathermap"] = {
                "status": "operational" if test_data else "no_data",
                "api_key_configured": bool(os.getenv('OPENWEATHER_API_KEY')),
                "test_city_response": bool(test_data),
                "description": "Ground-level air pollution data"
            }
        except Exception as e:
            status_data["data_sources"]["openweathermap"] = {
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(os.getenv('OPENWEATHER_API_KEY'))
            }
        
        # Check TEMPO service
        try:
            tempo_service = TEMPOService()
            tempo_test = await tempo_service.get_tempo_data("New York")
            status_data["data_sources"]["tempo_satellite"] = {
                "status": "operational" if tempo_test else "no_data",
                "credentials_configured": bool(
                    os.getenv('EARTHDATA_USERNAME') and os.getenv('EARTHDATA_PASSWORD')
                ),
                "test_city_response": bool(tempo_test),
                "description": "NASA TEMPO atmospheric column measurements"
            }
        except Exception as e:
            status_data["data_sources"]["tempo_satellite"] = {
                "status": "error",
                "error": str(e),
                "credentials_configured": bool(
                    os.getenv('EARTHDATA_USERNAME') and os.getenv('EARTHDATA_PASSWORD')
                )
            }
        
        return status_data
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Helper functions for detailed analysis
async def get_factors_for_hour(city: str, hour: int, openweather_data: dict, tempo_data: dict):
    """Get detailed factor breakdown for a specific forecast hour."""
    current_time = datetime.now() + timedelta(hours=hour)
    
    factors = {
        "base_data": {
            "current_aqi": openweather_data.get('aqi', 0) if openweather_data else 0,
            "current_pollutants": openweather_data.get('pollutants', {}) if openweather_data else {}
        },
        "temporal_factors": {
            "hour_of_day": current_time.hour,
            "day_of_week": current_time.weekday(),
            "rush_hour_factor": get_rush_hour_factor(current_time.hour),
            "weekend_factor": get_weekend_factor(current_time.weekday())
        },
        "tempo_satellite_factors": {},
        "weather_factors": {},
        "time_decay_factor": 1.0 - (hour * 0.02)
    }
    
    if tempo_data and tempo_data.get('measurements'):
        measurements = tempo_data['measurements']
        factors["tempo_satellite_factors"] = {
            "no2_column": measurements.get('no2_column', 0),
            "o3_column": measurements.get('o3_column', 0),
            "hcho_column": measurements.get('hcho_column', 0),
            "aerosol_optical_depth": measurements.get('aerosol_optical_depth', 0),
            "cloud_fraction": measurements.get('cloud_fraction', 0),
            "no2_enhancement_factor": get_no2_factor(measurements.get('no2_column', 0)),
            "aerosol_enhancement_factor": get_aerosol_factor(measurements.get('aerosol_optical_depth', 0))
        }
    
    return factors

async def get_detailed_factor_analysis(city: str, openweather_data: dict, tempo_data: dict):
    """Provide detailed analysis of all factors affecting the forecast."""
    analysis = {
        "ground_level_analysis": {},
        "atmospheric_analysis": {},
        "meteorological_analysis": {},
        "temporal_analysis": {}
    }
    
    # Ground level analysis
    if openweather_data:
        pollutants = openweather_data.get('pollutants', {})
        analysis["ground_level_analysis"] = {
            "pm25_level": pollutants.get('pm25', 0),
            "pm10_level": pollutants.get('pm10', 0),
            "no2_level": pollutants.get('no2', 0),
            "o3_level": pollutants.get('o3', 0),
            "dominant_pollutant": get_dominant_pollutant(pollutants),
            "baseline_aqi": openweather_data.get('aqi', 0)
        }
    
    # Atmospheric analysis from TEMPO
    if tempo_data and tempo_data.get('measurements'):
        measurements = tempo_data['measurements']
        analysis["atmospheric_analysis"] = {
            "tropospheric_no2": measurements.get('no2_column', 0),
            "total_ozone": measurements.get('o3_column', 0),
            "formaldehyde": measurements.get('hcho_column', 0),
            "aerosol_loading": measurements.get('aerosol_optical_depth', 0),
            "atmospheric_clarity": 1 - measurements.get('cloud_fraction', 0),
            "pollution_transport_potential": calculate_transport_potential(measurements)
        }
    
    return analysis

# Utility functions
def assess_openweather_quality(data):
    if not data:
        return {"quality": "no_data", "confidence": 0}
    
    pollutants = data.get('pollutants', {})
    completeness = sum(1 for v in pollutants.values() if v > 0) / 4
    
    return {
        "quality": "excellent" if completeness > 0.75 else "good" if completeness > 0.5 else "limited",
        "confidence": completeness,
        "available_pollutants": list(pollutants.keys()),
        "data_age_hours": 0  # Real-time data
    }

def assess_tempo_quality(data):
    if not data or not data.get('measurements'):
        return {"quality": "no_data", "confidence": 0}
    
    measurements = data['measurements']
    measurement_count = sum(1 for v in measurements.values() if v > 0)
    
    return {
        "quality": "excellent" if measurement_count > 4 else "good" if measurement_count > 2 else "limited",
        "confidence": measurement_count / 6,
        "available_measurements": list(measurements.keys()),
        "satellite_pass_quality": data.get('data_quality', 'unknown')
    }

def calculate_overall_confidence(openweather_data, tempo_data):
    ow_conf = assess_openweather_quality(openweather_data)["confidence"]
    tempo_conf = assess_tempo_quality(tempo_data)["confidence"]
    
    # Weighted average (OpenWeather 60%, TEMPO 40%)
    overall = (ow_conf * 0.6) + (tempo_conf * 0.4)
    
    return {
        "score": round(overall, 2),
        "level": "high" if overall > 0.8 else "medium" if overall > 0.5 else "low",
        "openweather_contribution": ow_conf,
        "tempo_contribution": tempo_conf
    }

def get_rush_hour_factor(hour):
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        return 1.2  # 20% increase during rush hours
    return 1.0

def get_weekend_factor(day_of_week):
    if day_of_week >= 5:  # Saturday=5, Sunday=6
        return 0.9  # 10% decrease on weekends
    return 1.0

def get_no2_factor(no2_column):
    if no2_column > 5e15:
        return 1.15
    elif no2_column > 3e15:
        return 1.08
    elif no2_column < 1e15:
        return 0.92
    return 1.0

def get_aerosol_factor(aod):
    if aod > 0.5:
        return 1.20
    elif aod > 0.3:
        return 1.10
    elif aod < 0.1:
        return 0.85
    return 1.0

def get_dominant_pollutant(pollutants):
    if not pollutants:
        return "unknown"
    
    max_pollutant = max(pollutants, key=pollutants.get)
    return max_pollutant

def calculate_transport_potential(measurements):
    # Simplified calculation based on wind and atmospheric conditions
    no2 = measurements.get('no2_column', 0)
    aod = measurements.get('aerosol_optical_depth', 0)
    
    # Higher values indicate more pollution transport
    transport_score = (no2 / 1e15 * 0.3) + (aod * 2)
    
    if transport_score > 2:
        return "high"
    elif transport_score > 1:
        return "medium"
    else:
        return "low"

# AI Suggestions endpoints using Gemini AI
@app.get("/api/ai-suggestions")
async def get_ai_suggestions(
    city: str = Query(..., description="City name for AQI suggestions"),
    user_profile: Optional[str] = Query(None, description="JSON string with user profile (age_group, health_conditions, activity_level)")
):
    """
    Get AI-powered personalized suggestions based on AQI forecast
    """
    try:
        # Get forecast data for AI analysis
        enhanced_forecast = EnhancedForecastService()
        forecast_result = await enhanced_forecast.get_forecast(city)
        
        # Parse user profile if provided
        parsed_profile = None
        if user_profile:
            import json
            try:
                parsed_profile = json.loads(user_profile)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid user_profile JSON format")
        
        # Initialize Gemini AI service
        gemini_service = GeminiAIService()
        
        # Prepare forecast data for AI analysis
        forecast_data = []
        if hasattr(forecast_result, 'forecast') and forecast_result.forecast:
            for point in forecast_result.forecast:
                forecast_data.append({
                    "time": point.time.isoformat() if hasattr(point.time, 'isoformat') else str(point.time),
                    "aqi": point.aqi,
                    "category": point.category
                })
        
        # Get AI suggestions
        ai_suggestions = await gemini_service.get_aqi_suggestions(
            city=city,
            forecast_data=forecast_data,
            user_profile=parsed_profile
        )
        
        return ai_suggestions
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting AI suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI suggestions: {str(e)}")

@app.get("/api/health-impact-analysis")
async def get_health_impact_analysis(
    city: str = Query(..., description="City name for health impact analysis"),
    duration_hours: int = Query(24, description="Forecast duration in hours (default 24)")
):
    """
    Get detailed health impact analysis based on AQI forecast
    """
    try:
        # Get enhanced forecast data
        enhanced_forecast = EnhancedForecastService()
        forecast_result = await enhanced_forecast.get_forecast(city)
        
        # Initialize Gemini AI service
        gemini_service = GeminiAIService()
        
        # Prepare forecast data
        forecast_data = []
        if hasattr(forecast_result, 'forecast') and forecast_result.forecast:
            for point in forecast_result.forecast[:duration_hours]:
                forecast_data.append({
                    "time": point.time.isoformat() if hasattr(point.time, 'isoformat') else str(point.time),
                    "aqi": point.aqi,
                    "category": point.category
                })
        
        # Get health impact analysis
        health_analysis = await gemini_service.get_health_impact_analysis(
            city=city,
            forecast_data=forecast_data,
            duration_hours=duration_hours
        )
        
        return health_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting health impact analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate health analysis: {str(e)}")

@app.get("/api/personalized-recommendations")
async def get_personalized_recommendations(
    city: str = Query(..., description="City name"),
    age_group: Optional[str] = Query("adult", description="Age group: child, adult, elderly"),
    health_conditions: Optional[str] = Query(None, description="Comma-separated health conditions"),
    activity_level: Optional[str] = Query("moderate", description="Activity level: low, moderate, high"),
    planning_hours: int = Query(6, description="Hours to plan ahead (default 6)")
):
    """
    Get personalized recommendations based on user profile and AQI forecast
    """
    try:
        # Build user profile
        user_profile = {
            "age_group": age_group,
            "activity_level": activity_level
        }
        
        if health_conditions:
            user_profile["health_conditions"] = [condition.strip() for condition in health_conditions.split(",")]
        else:
            user_profile["health_conditions"] = []
        
        # Get forecast data
        enhanced_forecast = EnhancedForecastService()
        forecast_result = await enhanced_forecast.get_forecast(city)
        
        # Initialize Gemini AI service
        gemini_service = GeminiAIService()
        
        # Prepare forecast data for specified planning hours
        forecast_data = []
        if hasattr(forecast_result, 'forecast') and forecast_result.forecast:
            for point in forecast_result.forecast[:planning_hours]:
                forecast_data.append({
                    "time": point.time.isoformat() if hasattr(point.time, 'isoformat') else str(point.time),
                    "aqi": point.aqi,
                    "category": point.category
                })
        
        # Get personalized AI suggestions
        recommendations = await gemini_service.get_aqi_suggestions(
            city=city,
            forecast_data=forecast_data,
            user_profile=user_profile
        )
        
        # Add user profile to response
        recommendations["user_profile"] = user_profile
        recommendations["planning_duration_hours"] = planning_hours
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tempo-air-quality-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
