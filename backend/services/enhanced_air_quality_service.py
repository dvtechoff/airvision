"""
Enhanced Air Quality Service
Integrates OpenAQ location database, real-time measurements, and TEMPO data
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx

from services.openaq_location_service import OpenAQLocationService
from services.tempo_service import TEMPOService

logger = logging.getLogger(__name__)

class EnhancedAirQualityService:
    def __init__(self):
        self.location_service = OpenAQLocationService()
        self.tempo_service = TEMPOService()
        self.openaq_client = None
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize all services"""
        await self.location_service.initialize_client()
        # TEMPO service initializes itself when needed
        self.logger.info("Enhanced Air Quality Service initialized")

    async def get_comprehensive_air_quality(self, query: str, include_tempo: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive air quality data by:
        1. Finding closest OpenAQ location from database
        2. Fetching real-time measurements from OpenAQ API
        3. Getting TEMPO satellite data for the same coordinates
        4. Combining all data sources
        """
        await self.initialize()
        
        result = {
            "query": query,
            "timestamp": datetime.utcnow(),
            "location_found": False,
            "openaq_data": None,
            "tempo_data": None,
            "combined_aqi": None,
            "data_sources": [],
            "errors": []
        }
        
        try:
            # Step 1: Find closest OpenAQ location
            self.logger.info(f"Finding closest OpenAQ location for: {query}")
            closest_location = await self.location_service.find_closest_location(query)
            
            if not closest_location:
                self.logger.warning(f"No OpenAQ location found for {query}")
                result["errors"].append("No OpenAQ monitoring station found nearby")
                return await self._fallback_response(query, result)
            
            result["location_found"] = True
            result["location_info"] = {
                "openaq_id": closest_location["openaq_id"],
                "name": closest_location["name"],
                "city": closest_location["city"],
                "country": closest_location["country"],
                "coordinates": {
                    "latitude": closest_location["latitude"],
                    "longitude": closest_location["longitude"]
                },
                "distance_km": closest_location["distance_km"],
                "available_parameters": closest_location["parameters"]
            }
            
            self.logger.info(f"Found location: {closest_location['name']} (ID: {closest_location['openaq_id']}, Distance: {closest_location['distance_km']:.2f}km)")
            
            # Step 2: Get real-time OpenAQ measurements
            try:
                openaq_data = await self.location_service.get_location_air_quality_data(
                    closest_location["openaq_id"],
                    parameters=["pm25", "pm10", "o3", "no2", "so2", "co"]
                )
                
                if "error" not in openaq_data:
                    result["openaq_data"] = openaq_data
                    result["data_sources"].append("OpenAQ Real-time Measurements")
                    self.logger.info(f"Retrieved {openaq_data.get('total_measurements', 0)} OpenAQ measurements")
                else:
                    result["errors"].append(f"OpenAQ API Error: {openaq_data['error']}")
                    
            except Exception as e:
                self.logger.error(f"Error fetching OpenAQ data: {e}")
                result["errors"].append(f"OpenAQ fetch error: {str(e)}")
            
            # Step 3: Get TEMPO satellite data for the same coordinates
            if include_tempo:
                try:
                    lat = closest_location["latitude"]
                    lon = closest_location["longitude"]
                    
                    # Use the location name for TEMPO query
                    tempo_query = closest_location["city"] or closest_location["name"] or query
                    
                    async with self.tempo_service:
                        tempo_data = await self.tempo_service.get_tempo_data(tempo_query)
                    
                    if tempo_data and "error" not in tempo_data:
                        result["tempo_data"] = tempo_data
                        result["data_sources"].append("NASA TEMPO Satellite")
                        self.logger.info(f"Retrieved TEMPO data for coordinates ({lat:.4f}, {lon:.4f})")
                    else:
                        result["errors"].append("TEMPO data unavailable")
                        
                except Exception as e:
                    self.logger.error(f"Error fetching TEMPO data: {e}")
                    result["errors"].append(f"TEMPO fetch error: {str(e)}")
            
            # Step 4: Combine and analyze all data
            result["combined_aqi"] = self._combine_air_quality_data(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in get_comprehensive_air_quality for {query}: {e}")
            result["errors"].append(f"Service error: {str(e)}")
            return await self._fallback_response(query, result)

    def _combine_air_quality_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine OpenAQ and TEMPO data into a comprehensive AQI assessment
        """
        combined = {
            "primary_source": None,
            "aqi": None,
            "category": "Unknown",
            "pollutants": {},
            "confidence": "low",
            "data_freshness": None,
            "health_advisory": None
        }
        
        try:
            openaq_data = result.get("openaq_data")
            tempo_data = result.get("tempo_data")
            
            # Prioritize OpenAQ real measurements if available
            if openaq_data and openaq_data.get("aqi_data"):
                aqi_data = openaq_data["aqi_data"]
                combined.update({
                    "primary_source": "OpenAQ Ground Measurements",
                    "aqi": aqi_data["aqi"],
                    "category": aqi_data["category"],
                    "pollutants": aqi_data["pollutants"],
                    "confidence": "high",
                    "dominant_pollutant": aqi_data.get("dominant_pollutant")
                })
                
                # Check data freshness
                latest_measurements = openaq_data.get("latest_by_parameter", {})
                if latest_measurements:
                    most_recent = max(
                        [datetime.fromisoformat(m["date"].replace('Z', '+00:00')) 
                         for m in latest_measurements.values() if m.get("date")],
                        default=None
                    )
                    if most_recent:
                        hours_old = (datetime.utcnow() - most_recent.replace(tzinfo=None)).total_seconds() / 3600
                        combined["data_freshness"] = f"{hours_old:.1f} hours old"
                        if hours_old < 2:
                            combined["confidence"] = "very_high"
                        elif hours_old > 24:
                            combined["confidence"] = "medium"
            
            # Enhance with TEMPO satellite data
            elif tempo_data and tempo_data.get("air_quality"):
                tempo_aqi = tempo_data["air_quality"]
                combined.update({
                    "primary_source": "NASA TEMPO Satellite",
                    "aqi": tempo_aqi["aqi"],
                    "category": tempo_aqi["category"],
                    "confidence": "medium"
                })
                
                # Add TEMPO-specific pollutants
                if tempo_data.get("surface_estimates"):
                    combined["pollutants"] = tempo_data["surface_estimates"]
            
            # If we have both sources, create a hybrid assessment
            if (openaq_data and openaq_data.get("aqi_data") and 
                tempo_data and tempo_data.get("air_quality")):
                
                self._create_hybrid_assessment(combined, openaq_data["aqi_data"], tempo_data["air_quality"])
            
            # Add health advisory
            combined["health_advisory"] = self._get_health_advisory(combined["aqi"], combined["category"])
            
            return combined
            
        except Exception as e:
            self.logger.error(f"Error combining air quality data: {e}")
            return combined

    def _create_hybrid_assessment(self, combined: Dict, openaq_aqi: Dict, tempo_aqi: Dict):
        """Create a hybrid assessment when both OpenAQ and TEMPO data are available"""
        openaq_value = openaq_aqi["aqi"]
        tempo_value = tempo_aqi["aqi"]
        
        # Weighted average (OpenAQ gets higher weight as ground truth)
        hybrid_aqi = int(openaq_value * 0.7 + tempo_value * 0.3)
        
        combined.update({
            "primary_source": "Hybrid (Ground + Satellite)",
            "aqi": hybrid_aqi,
            "category": self._get_aqi_category(hybrid_aqi),
            "confidence": "very_high",
            "ground_aqi": openaq_value,
            "satellite_aqi": tempo_value,
            "correlation": "good" if abs(openaq_value - tempo_value) < 20 else "moderate"
        })

    def _get_aqi_category(self, aqi: float) -> str:
        """Get AQI category based on value"""
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

    def _get_health_advisory(self, aqi: Optional[int], category: str) -> str:
        """Get health advisory based on AQI"""
        if not aqi:
            return "Data unavailable - general precautions recommended"
        
        advisories = {
            "Good": "Air quality is satisfactory. Enjoy outdoor activities.",
            "Moderate": "Air quality is acceptable. Sensitive individuals should consider limiting prolonged outdoor exertion.",
            "Unhealthy for Sensitive Groups": "Members of sensitive groups may experience health effects. Reduce prolonged outdoor exertion.",
            "Unhealthy": "Everyone may begin to experience health effects. Avoid prolonged outdoor exertion.",
            "Very Unhealthy": "Health alert: everyone may experience serious health effects. Avoid outdoor activities.",
            "Hazardous": "Health emergency: everyone should avoid all outdoor exertion."
        }
        
        return advisories.get(category, "Exercise caution with outdoor activities.")

    async def _fallback_response(self, query: str, base_result: Dict) -> Dict[str, Any]:
        """
        Generate fallback response when no real data is available
        """
        base_result.update({
            "fallback_data": {
                "aqi": 75,
                "category": "Moderate",
                "source": "Estimated (No monitoring stations nearby)",
                "note": "This is an estimated value. For accurate readings, consider locations with nearby monitoring stations."
            }
        })
        
        return base_result

    async def setup_database_and_fetch_locations(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Initialize database and fetch all OpenAQ locations
        This should be run once during setup or periodically to update the location database
        """
        try:
            # Initialize database
            from database.config import db_manager
            
            # Test database connection
            if not db_manager.test_connection():
                return {"error": "Database connection failed"}
            
            # Create tables if they don't exist
            db_manager.create_tables()
            
            # Fetch and store all locations
            self.logger.info("Starting location fetch and database population...")
            stats = await self.location_service.fetch_and_store_all_locations(api_key)
            
            return {
                "success": True,
                "message": "Database setup and location fetch completed",
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"Error in setup_database_and_fetch_locations: {e}")
            return {"error": str(e)}

    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all services and data availability
        """
        status = {
            "timestamp": datetime.utcnow(),
            "services": {},
            "database": {},
            "overall_status": "unknown"
        }
        
        try:
            # Check database status
            db_stats = await self.location_service.get_database_stats()
            status["database"] = db_stats
            
            # Check OpenAQ API
            await self.location_service.initialize_client()
            status["services"]["openaq_api"] = "available"
            
            # Check TEMPO service
            try:
                async with self.tempo_service:
                    status["services"]["tempo_api"] = "available"
            except:
                status["services"]["tempo_api"] = "limited"
            
            # Determine overall status
            if (status["database"].get("database_available") and 
                status["services"].get("openaq_api") == "available"):
                status["overall_status"] = "operational"
            else:
                status["overall_status"] = "degraded"
                
        except Exception as e:
            status["error"] = str(e)
            status["overall_status"] = "error"
            
        return status