"""
OpenAQ Location Management Service
Handles fetching, storing, and querying OpenAQ monitoring locations
"""

import asyncio
import logging
import math
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import httpx
from geopy.distance import geodesic

# Database imports (will work when SQLAlchemy is installed)
try:
    from sqlalchemy.orm import Session
    from sqlalchemy import and_, func, desc
    from models.database import OpenAQLocation, LocationQuery, AirQualityData
    from database.config import db_manager
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False

logger = logging.getLogger(__name__)

class OpenAQLocationService:
    def __init__(self):
        self.client = None
        self.logger = logging.getLogger(__name__)
        self.locations_cache = {}  # In-memory cache as fallback
        
    async def initialize_client(self):
        """Initialize HTTP client for OpenAQ API"""
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url="https://api.openaq.org/v3/",
                headers={
                    "User-Agent": "NASA-AirVision-App/1.0",
                    "Accept": "application/json"
                },
                timeout=60.0
            )
            self.logger.info("OpenAQ location service initialized")

    async def fetch_and_store_all_locations(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch all OpenAQ locations and store them in the database
        """
        await self.initialize_client()
        
        if api_key:
            self.client.headers["X-API-Key"] = api_key
        
        stats = {
            "total_fetched": 0,
            "stored_in_db": 0,
            "updated_existing": 0,
            "errors": 0,
            "countries": set(),
            "parameters": set(),
            "start_time": datetime.utcnow()
        }
        
        try:
            page = 1
            limit = 1000  # Maximum allowed by OpenAQ API
            
            while True:
                self.logger.info(f"Fetching locations page {page}...")
                
                response = await self.client.get(
                    "locations",
                    params={
                        "limit": limit,
                        "page": page,
                        "sort": "asc",
                        "order_by": "id"
                    }
                )
                
                if response.status_code == 401:
                    self.logger.error("OpenAQ API authentication required")
                    stats["error"] = "Authentication required - API key needed"
                    break
                elif response.status_code != 200:
                    self.logger.error(f"API error {response.status_code}: {response.text}")
                    stats["errors"] += 1
                    break
                
                data = response.json()
                locations = data.get("results", [])
                
                if not locations:
                    self.logger.info(f"No more locations found at page {page}")
                    break
                
                self.logger.info(f"Processing {len(locations)} locations from page {page}")
                
                # Process and store locations
                for location in locations:
                    try:
                        if await self._process_and_store_location(location):
                            stats["stored_in_db"] += 1
                        else:
                            stats["updated_existing"] += 1
                        
                        stats["total_fetched"] += 1
                        
                        # Track statistics
                        stats["countries"].add(location.get("country", "Unknown"))
                        if location.get("parameters"):
                            for param in location["parameters"]:
                                if isinstance(param, dict):
                                    stats["parameters"].add(param.get("parameter", ""))
                                else:
                                    stats["parameters"].add(str(param))
                        
                    except Exception as e:
                        self.logger.error(f"Error processing location {location.get('id', 'unknown')}: {e}")
                        stats["errors"] += 1
                
                # Check if we have more pages
                meta = data.get("meta", {})
                if page >= meta.get("pages", 1):
                    break
                
                page += 1
                
                # Add small delay to be respectful to the API
                await asyncio.sleep(0.1)
        
        except Exception as e:
            self.logger.error(f"Error in fetch_and_store_all_locations: {e}")
            stats["error"] = str(e)
        
        finally:
            stats["end_time"] = datetime.utcnow()
            stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()
            stats["countries"] = list(stats["countries"])
            stats["parameters"] = list(stats["parameters"])
            
            self.logger.info(f"Location fetch completed: {stats['total_fetched']} locations processed")
        
        return stats

    async def _process_and_store_location(self, location_data: Dict) -> bool:
        """
        Process and store a single location in the database
        Returns True if new location was created, False if existing was updated
        """
        if not HAS_DATABASE:
            # Store in memory cache as fallback
            self.locations_cache[location_data.get("id")] = location_data
            return True
        
        try:
            with db_manager.get_session() as session:
                openaq_id = location_data.get("id")
                
                # Check if location already exists
                existing = session.query(OpenAQLocation).filter_by(openaq_id=openaq_id).first()
                
                if existing:
                    # Update existing location
                    self._update_location_from_data(existing, location_data)
                    existing.updated_at = datetime.utcnow()
                    return False
                else:
                    # Create new location
                    new_location = self._create_location_from_data(location_data)
                    session.add(new_location)
                    return True
                    
        except Exception as e:
            self.logger.error(f"Database error storing location {location_data.get('id')}: {e}")
            raise

    def _create_location_from_data(self, data: Dict) -> 'OpenAQLocation':
        """Create OpenAQLocation object from API data"""
        coordinates = data.get("coordinates", {})
        
        return OpenAQLocation(
            openaq_id=data.get("id"),
            name=data.get("name", ""),
            display_name=data.get("displayName", ""),
            city=data.get("city"),
            country=data.get("country", ""),
            latitude=coordinates.get("latitude", 0.0),
            longitude=coordinates.get("longitude", 0.0),
            is_mobile=data.get("isMobile", False),
            is_analysis=data.get("isAnalysis", False),
            entity=data.get("entity"),
            sensor_type=data.get("sensorType"),
            parameters=[param.get("parameter") if isinstance(param, dict) else str(param) 
                       for param in data.get("parameters", [])],
            first_updated=self._parse_datetime(data.get("firstUpdated")),
            last_updated=self._parse_datetime(data.get("lastUpdated")),
            measurements_count=data.get("measurements", 0)
        )

    def _update_location_from_data(self, location: 'OpenAQLocation', data: Dict):
        """Update existing location with new data"""
        coordinates = data.get("coordinates", {})
        
        location.name = data.get("name", location.name)
        location.display_name = data.get("displayName", location.display_name)
        location.city = data.get("city", location.city)
        location.latitude = coordinates.get("latitude", location.latitude)
        location.longitude = coordinates.get("longitude", location.longitude)
        location.is_mobile = data.get("isMobile", location.is_mobile)
        location.is_analysis = data.get("isAnalysis", location.is_analysis)
        location.entity = data.get("entity", location.entity)
        location.sensor_type = data.get("sensorType", location.sensor_type)
        location.parameters = [param.get("parameter") if isinstance(param, dict) else str(param) 
                              for param in data.get("parameters", [])]
        location.last_updated = self._parse_datetime(data.get("lastUpdated"))
        location.measurements_count = data.get("measurements", location.measurements_count)

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from OpenAQ API"""
        if not date_str:
            return None
        try:
            # OpenAQ uses ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

    async def find_closest_location(self, query: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Find the closest OpenAQ location for a given query or coordinates
        """
        if not HAS_DATABASE:
            return await self._find_closest_location_fallback(query, lat, lon)
        
        try:
            with db_manager.get_session() as session:
                # First, check if we have a cached query result
                cached_result = self._get_cached_query_result(session, query)
                if cached_result:
                    return cached_result
                
                # If coordinates not provided, try to geocode the query
                if lat is None or lon is None:
                    coords = await self._geocode_query(query)
                    if coords:
                        lat, lon = coords
                    else:
                        # Fallback: search by name in database
                        return await self._search_by_name(session, query)
                
                # Find closest location using spatial query
                closest_location = self._find_closest_by_coordinates(session, lat, lon)
                
                if closest_location:
                    # Cache the result
                    self._cache_query_result(session, query, lat, lon, closest_location)
                    
                    return {
                        "openaq_id": closest_location.openaq_id,
                        "name": closest_location.display_name or closest_location.name,
                        "city": closest_location.city,
                        "country": closest_location.country,
                        "latitude": closest_location.latitude,
                        "longitude": closest_location.longitude,
                        "parameters": closest_location.parameters,
                        "distance_km": self._calculate_distance(lat, lon, closest_location.latitude, closest_location.longitude),
                        "measurements_count": closest_location.measurements_count,
                        "last_updated": closest_location.last_updated
                    }
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error finding closest location for {query}: {e}")
            return None

    def _find_closest_by_coordinates(self, session: Session, lat: float, lon: float, max_distance_km: float = 100) -> Optional['OpenAQLocation']:
        """Find closest location using database spatial operations"""
        # Using simple distance calculation (can be optimized with PostGIS)
        locations = session.query(OpenAQLocation).filter(
            and_(
                OpenAQLocation.is_active == True,
                OpenAQLocation.measurements_count > 0
            )
        ).all()
        
        closest_location = None
        min_distance = float('inf')
        
        for location in locations:
            distance = self._calculate_distance(lat, lon, location.latitude, location.longitude)
            if distance < min_distance and distance <= max_distance_km:
                min_distance = distance
                closest_location = location
        
        return closest_location

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers

    async def _geocode_query(self, query: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a query string to coordinates
        This is a simplified version - you might want to use a proper geocoding service
        """
        # Common city coordinates (expand this as needed)
        city_coords = {
            "new york": (40.7128, -74.0060),
            "los angeles": (34.0522, -118.2437),
            "chicago": (41.8781, -87.6298),
            "houston": (29.7604, -95.3698),
            "phoenix": (33.4484, -112.0740),
            "philadelphia": (39.9526, -75.1652),
            "san francisco": (37.7749, -122.4194),
            "boston": (42.3601, -71.0589),
            "seattle": (47.6062, -122.3321),
            "miami": (25.7617, -80.1918),
            "piseco lake": (43.4531, -74.5145),
        }
        
        return city_coords.get(query.lower())

    def _get_cached_query_result(self, session: 'Session', query: str) -> Optional[Dict[str, Any]]:
        """Get cached query result from database"""
        try:
            cached = session.query(LocationQuery).filter_by(query_text=query.lower()).first()
            if cached and cached.closest_location_id:
                # Update usage stats
                cached.hits += 1
                cached.last_used = datetime.utcnow()
                
                # Get the location details
                location = session.query(OpenAQLocation).filter_by(openaq_id=cached.closest_location_id).first()
                if location:
                    return {
                        "openaq_id": location.openaq_id,
                        "name": location.display_name or location.name,
                        "city": location.city,
                        "country": location.country,
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "parameters": location.parameters,
                        "distance_km": cached.distance_km,
                        "measurements_count": location.measurements_count,
                        "last_updated": location.last_updated
                    }
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached query result: {e}")
            return None

    def _cache_query_result(self, session: 'Session', query: str, lat: float, lon: float, location: 'OpenAQLocation'):
        """Cache query result in database"""
        try:
            distance = self._calculate_distance(lat, lon, location.latitude, location.longitude)
            
            # Check if query already exists
            existing = session.query(LocationQuery).filter_by(query_text=query.lower()).first()
            if existing:
                existing.closest_location_id = location.openaq_id
                existing.distance_km = distance
                existing.hits += 1
                existing.last_used = datetime.utcnow()
            else:
                new_query = LocationQuery(
                    query_text=query.lower(),
                    query_lat=lat,
                    query_lon=lon,
                    closest_location_id=location.openaq_id,
                    distance_km=distance
                )
                session.add(new_query)
        except Exception as e:
            self.logger.error(f"Error caching query result: {e}")

    async def _search_by_name(self, session: 'Session', query: str) -> Optional[Dict[str, Any]]:
        """Search locations by name when coordinates are not available"""
        try:
            # Search by city or display name
            locations = session.query(OpenAQLocation).filter(
                and_(
                    OpenAQLocation.is_active == True,
                    func.lower(OpenAQLocation.display_name).contains(query.lower()) |
                    func.lower(OpenAQLocation.city).contains(query.lower()) |
                    func.lower(OpenAQLocation.name).contains(query.lower())
                )
            ).limit(5).all()
            
            if locations:
                # Return the first match (could be improved with better ranking)
                location = locations[0]
                return {
                    "openaq_id": location.openaq_id,
                    "name": location.display_name or location.name,
                    "city": location.city,
                    "country": location.country,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "parameters": location.parameters,
                    "distance_km": 0,  # Unknown distance for name-based search
                    "measurements_count": location.measurements_count,
                    "last_updated": location.last_updated
                }
            
            return None
        except Exception as e:
            self.logger.error(f"Error searching by name: {e}")
            return None

    async def _cache_measurements(self, openaq_id: int, measurements: List[Dict]):
        """Cache measurements in database if available"""
        if not HAS_DATABASE:
            return
        
        try:
            with db_manager.get_session() as session:
                for measurement in measurements:
                    # Only cache recent measurements
                    measurement_date = self._parse_datetime(measurement.get("date"))
                    if measurement_date and (datetime.utcnow() - measurement_date.replace(tzinfo=None)).days <= 1:
                        
                        # Check if measurement already exists
                        existing = session.query(AirQualityData).filter(
                            and_(
                                AirQualityData.location_openaq_id == openaq_id,
                                AirQualityData.parameter == measurement.get("parameter"),
                                AirQualityData.measurement_date == measurement_date
                            )
                        ).first()
                        
                        if not existing:
                            new_measurement = AirQualityData(
                                location_openaq_id=openaq_id,
                                parameter=measurement.get("parameter"),
                                value=measurement.get("value"),
                                unit=measurement.get("unit"),
                                measurement_date=measurement_date,
                                coordinates=measurement.get("coordinates"),
                                is_valid=True
                            )
                            session.add(new_measurement)
                            
        except Exception as e:
            self.logger.error(f"Error caching measurements: {e}")

    async def _find_closest_location_fallback(self, query: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Fallback location search using geocoding when database is not available
        """
        try:
            # If coordinates not provided, try to geocode
            if lat is None or lon is None:
                coords = await self._geocode_query(query)
                if coords:
                    lat, lon = coords
                else:
                    self.logger.warning(f"Could not geocode query: {query}")
                    return None
            
            # For fallback, we'll create a mock location based on geocoding
            # In a real implementation, you might want to use a static list of major stations
            return {
                "openaq_id": 999999,  # Mock ID
                "name": f"Nearest station to {query}",
                "city": query,
                "country": "US",
                "latitude": lat,
                "longitude": lon,
                "parameters": ["pm25", "pm10", "o3", "no2"],
                "distance_km": 0.0,
                "measurements_count": 100,
                "last_updated": datetime.utcnow() - timedelta(hours=1),
                "note": "Fallback location - database not available"
            }
            
        except Exception as e:
            self.logger.error(f"Error in fallback location search: {e}")
            return None
        """
        Get recent air quality data for a specific OpenAQ location
        """
        await self.initialize_client()
        
        try:
            # Get recent measurements from OpenAQ API
            params = {
                "locations_id": openaq_id,
                "limit": 100,
                "sort": "desc",
                "order_by": "datetime"
            }
            
            if parameters:
                params["parameter"] = ",".join(parameters)
            
            response = await self.client.get("measurements", params=params)
            
            if response.status_code == 401:
                self.logger.warning("OpenAQ API authentication required for measurements")
                return {"error": "API key required", "measurements": []}
            elif response.status_code != 200:
                self.logger.error(f"Measurements API error {response.status_code}")
                return {"error": f"API error {response.status_code}", "measurements": []}
            
            data = response.json()
            measurements = data.get("results", [])
            
            # Process measurements into a structured format
            processed_data = self._process_measurements(measurements)
            
            # Store in database cache if available
            if HAS_DATABASE:
                await self._cache_measurements(openaq_id, measurements)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error fetching air quality data for location {openaq_id}: {e}")
            return {"error": str(e), "measurements": []}

    def _process_measurements(self, measurements: List[Dict]) -> Dict[str, Any]:
        """Process raw measurements into structured air quality data"""
        if not measurements:
            return {"measurements": [], "latest_by_parameter": {}, "aqi_data": None}
        
        latest_by_parameter = {}
        
        for measurement in measurements:
            parameter = measurement.get("parameter")
            if parameter and parameter not in latest_by_parameter:
                latest_by_parameter[parameter] = {
                    "value": measurement.get("value"),
                    "unit": measurement.get("unit"),
                    "date": measurement.get("date"),
                    "coordinates": measurement.get("coordinates")
                }
        
        # Calculate AQI if we have the right parameters
        aqi_data = self._calculate_aqi_from_measurements(latest_by_parameter)
        
        return {
            "measurements": measurements,
            "latest_by_parameter": latest_by_parameter,
            "aqi_data": aqi_data,
            "total_measurements": len(measurements)
        }

    def _calculate_aqi_from_measurements(self, measurements: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
        """Calculate AQI from measurement data"""
        # This is a simplified AQI calculation - you might want to use a more comprehensive library
        aqi_values = []
        pollutants = {}
        
        # EPA AQI breakpoints (simplified)
        breakpoints = {
            "pm25": [(0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150)],
            "pm10": [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150)],
            "o3": [(0, 54, 0, 50), (55, 70, 51, 100), (71, 85, 101, 150)],
            "no2": [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150)]
        }
        
        for param, data in measurements.items():
            if param in breakpoints:
                value = data.get("value")
                if value is not None:
                    pollutants[param] = value
                    aqi = self._calculate_single_aqi(param, value, breakpoints[param])
                    if aqi is not None:
                        aqi_values.append(aqi)
        
        if aqi_values:
            overall_aqi = max(aqi_values)
            return {
                "aqi": int(overall_aqi),
                "category": self._get_aqi_category(overall_aqi),
                "pollutants": pollutants,
                "dominant_pollutant": max(measurements.keys(), key=lambda k: aqi_values[list(measurements.keys()).index(k)] if k in measurements else 0)
            }
        
        return None

    def _calculate_single_aqi(self, pollutant: str, concentration: float, breakpoints: List[Tuple]) -> Optional[int]:
        """Calculate AQI for a single pollutant"""
        for c_low, c_high, aqi_low, aqi_high in breakpoints:
            if c_low <= concentration <= c_high:
                aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (concentration - c_low) + aqi_low
                return int(aqi)
        return 500  # Hazardous if above all breakpoints

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

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about stored locations"""
        if not HAS_DATABASE:
            return {"error": "Database not available", "cache_size": len(self.locations_cache)}
        
        try:
            with db_manager.get_session() as session:
                total_locations = session.query(OpenAQLocation).count()
                active_locations = session.query(OpenAQLocation).filter_by(is_active=True).count()
                countries = session.query(OpenAQLocation.country).distinct().count()
                
                # Most recent update
                latest_update = session.query(func.max(OpenAQLocation.updated_at)).scalar()
                
                return {
                    "total_locations": total_locations,
                    "active_locations": active_locations,
                    "countries": countries,
                    "latest_update": latest_update,
                    "database_available": True
                }
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {"error": str(e), "database_available": False}