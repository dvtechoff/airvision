from openaq import OpenAQ
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class OpenAQService:
    """
    Service for fetching air quality data from OpenAQ API using the official Python SDK.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAQ_API_KEY")
        self.client = None
        
        # City coordinates for location-based searches
        # Updated with known working US monitoring locations from OpenAQ
        self.city_coords = {
            # Major cities with known nearby sensors
            "new york": {"lat": 43.4531, "lon": -74.5145, "radius": 25000, "known_location": "Piseco Lake"},
            "albany": {"lat": 42.6803, "lon": -73.8370, "radius": 25000, "known_location": "Albany"},
            "los angeles": {"lat": 34.0522, "lon": -118.2437, "radius": 25000, "known_location": "Multiple CA stations"},
            "chicago": {"lat": 41.8781, "lon": -87.6298, "radius": 25000, "known_location": "Multiple IL stations"},
            "houston": {"lat": 29.7604, "lon": -95.3698, "radius": 25000, "known_location": "Multiple TX stations"},
            "phoenix": {"lat": 33.4484, "lon": -112.0740, "radius": 25000, "known_location": "Multiple AZ stations"},
            "philadelphia": {"lat": 39.9526, "lon": -75.1652, "radius": 25000, "known_location": "Multiple PA stations"},
            "san francisco": {"lat": 37.7749, "lon": -122.4194, "radius": 25000, "known_location": "Multiple CA stations"},
            "boston": {"lat": 42.3601, "lon": -71.0589, "radius": 25000, "known_location": "Multiple MA stations"},
            "seattle": {"lat": 47.6062, "lon": -122.3321, "radius": 25000, "known_location": "Multiple WA stations"},
            "miami": {"lat": 25.7617, "lon": -80.1918, "radius": 25000, "known_location": "Multiple FL stations"},
            "atlanta": {"lat": 33.7490, "lon": -84.3880, "radius": 25000, "known_location": "Multiple GA stations"},
            "denver": {"lat": 39.7392, "lon": -104.9903, "radius": 25000, "known_location": "Multiple CO stations"},
            "las vegas": {"lat": 36.1699, "lon": -115.1398, "radius": 25000, "known_location": "Multiple NV stations"},
            "detroit": {"lat": 42.3314, "lon": -83.0458, "radius": 25000, "known_location": "Multiple MI stations"},
            
            # Specific known working locations  
            "piseco lake": {"lat": 43.4531, "lon": -74.5145, "radius": 5000, "known_location": "Piseco Lake"},
            "south lake tahoe": {"lat": 38.945, "lon": -119.9689, "radius": 5000, "known_location": "South Lake Tahoe"},
            "hamilton": {"lat": 39.383372, "lon": -84.544083, "radius": 5000, "known_location": "Hamilton"},
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = OpenAQ(api_key=self.api_key)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            self.client.close()
    
    async def get_aqi_data(self, city: str) -> Dict[str, Any]:
        """
        Get current AQI data for a city from OpenAQ using the new Python SDK.
        """
        try:
            # Get real data from OpenAQ API
            real_data = await self._fetch_real_data(city)
            if real_data:
                logger.info(f"Successfully fetched real OpenAQ data for {city}")
                return real_data
            else:
                logger.info(f"No real OpenAQ data available for {city}, using mock data")
                return self._get_mock_data(city)
        except Exception as e:
            logger.error(f"Error fetching OpenAQ data for {city}: {e}")
            return self._get_mock_data(city)

    async def _fetch_real_data(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real air quality data from OpenAQ API for a city using the new Python SDK
        """
        try:
            if not self.client:
                logger.warning("OpenAQ client not initialized")
                return None
            
            # Get city coordinates
            city_lower = city.lower()
            if city_lower not in self.city_coords:
                logger.warning(f"Coordinates not found for {city}")
                return None
                
            coords = self.city_coords[city_lower]
            lat, lon, radius = coords["lat"], coords["lon"], coords["radius"]
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._fetch_openaq_data_sync, 
                lat, lon, radius, city
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in _fetch_real_data: {e}")
            return None

    def _fetch_openaq_data_sync(self, lat: float, lon: float, radius: int, city: str) -> Optional[Dict[str, Any]]:
        """
        Synchronous method to fetch OpenAQ data using the Python SDK
        """
        try:
            logger.info(f"Fetching OpenAQ data for {city} at ({lat}, {lon}) with radius {radius}m")
            
            # Find locations near the city coordinates
            locations = self.client.locations.list(
                coordinates=[lon, lat], 
                radius=radius, 
                limit=50  # Increased limit to find more options
            )
            
            logger.info(f"OpenAQ API returned {len(getattr(locations, 'results', []))} locations")
            
            if not locations or not hasattr(locations, 'results') or not locations.results:
                logger.info(f"No monitoring locations found near {city}")
                return None
            
            # Process ALL available locations and their sensors
            all_measurements = {}
            location_info = None
            
            for loc_idx, location in enumerate(locations.results):
                location_name = getattr(location, 'name', f'Location_{loc_idx}')
                logger.info(f"Processing location {loc_idx + 1}: {location_name}")
                
                if not hasattr(location, 'sensors') or not location.sensors:
                    logger.info(f"  No sensors found at {location_name}")
                    continue
                
                logger.info(f"  Found {len(location.sensors)} sensors at {location_name}")
                
                # Process each sensor
                for sensor_idx, sensor in enumerate(location.sensors):
                    try:
                        sensor_id = getattr(sensor, 'id', None)
                        parameter = getattr(sensor, 'parameter', None)
                        
                        if not sensor_id or not parameter:
                            continue
                            
                        # Get parameter name
                        if hasattr(parameter, 'name'):
                            param_name = parameter.name.lower()
                        else:
                            param_name = str(parameter).lower()
                            
                        logger.info(f"    Sensor {sensor_idx + 1}: {param_name} (ID: {sensor_id})")
                        
                        # Get measurements from this sensor
                        measurements = self.client.measurements.list(
                            sensors_id=sensor_id,
                            limit=5
                        )
                        
                        if measurements and hasattr(measurements, 'results') and measurements.results:
                            latest_measurement = measurements.results[0]
                            value = getattr(latest_measurement, 'value', None)
                            
                            if value is not None and value >= 0:  # Valid measurement
                                # Map parameter names to our standard format
                                param_mapping = {
                                    'pm2.5': 'pm25',
                                    'pm25': 'pm25',
                                    'pm10': 'pm10',
                                    'no2': 'no2',
                                    'no': 'no2',  # Use NO as NO2 proxy
                                    'o3': 'o3',
                                    'ozone': 'o3',
                                    'co': 'co'
                                }
                                
                                std_param = param_mapping.get(param_name)
                                if std_param:
                                    # Convert units if needed
                                    converted_value = self._convert_units(value, parameter, std_param)
                                    all_measurements[std_param] = converted_value
                                    
                                    logger.info(f"      ✅ Got {std_param}: {converted_value}")
                                    
                                    # Save location info from first successful measurement
                                    if not location_info:
                                        location_info = {
                                            "name": location_name,
                                            "coordinates": {"lat": lat, "lon": lon},
                                            "sensors_count": len(location.sensors)
                                        }
                                else:
                                    logger.info(f"      ⚠️ Unmapped parameter: {param_name}")
                            else:
                                logger.info(f"      ⚠️ Invalid value: {value}")
                        else:
                            logger.info(f"      ❌ No measurements available")
                            
                    except Exception as sensor_error:
                        logger.warning(f"Error processing sensor {sensor_id}: {sensor_error}")
                        continue
            
            logger.info(f"Total measurements collected: {list(all_measurements.keys())}")
            
            if not all_measurements:
                logger.info(f"No valid measurements found for {city}")
                return None
            
            # Fill in missing parameters with reasonable defaults
            # Use 0 for missing pollutants rather than leaving them out
            standard_params = ['pm25', 'pm10', 'no2', 'o3']
            for param in standard_params:
                if param not in all_measurements:
                    all_measurements[param] = 0
                    logger.info(f"  Filled missing {param} with 0")
            
            # Calculate AQI from real measurements
            aqi = self._calculate_aqi(all_measurements)
            category = self._get_aqi_category(aqi)
            
            result = {
                "city": city,
                "aqi": aqi,
                "category": category,
                "pollutants": {
                    "pm25": round(all_measurements.get("pm25", 0), 1),
                    "pm10": round(all_measurements.get("pm10", 0), 1),
                    "no2": round(all_measurements.get("no2", 0), 1),
                    "o3": round(all_measurements.get("o3", 0), 1)
                },
                "source": "OpenAQ (Real Data)",
                "timestamp": datetime.now(),
                "location_info": location_info or {
                    "name": f"OpenAQ Monitoring Area",
                    "coordinates": {"lat": lat, "lon": lon},
                    "sensors_count": len(locations.results)
                }
            }
            
            logger.info(f"✅ Successfully processed real OpenAQ data for {city} - AQI: {aqi}")
            return result
            
        except Exception as e:
            logger.error(f"Error in _fetch_openaq_data_sync for {city}: {e}")
            return None

    def _convert_units(self, value: float, parameter, target_param: str) -> float:
        """
        Convert measurement units to standard format
        """
        try:
            # Get unit from parameter
            unit = None
            if hasattr(parameter, 'units'):
                unit = parameter.units.lower()
            
            # Most OpenAQ measurements are already in correct units:
            # PM2.5/PM10: µg/m³ 
            # NO2/O3: ppm -> convert to µg/m³ for consistency
            # But for AQI calculation, we'll use the values as-is
            
            if target_param in ['no2', 'o3'] and unit == 'ppm':
                # Convert ppm to µg/m³ if needed, but for now use as-is
                # NO2: 1 ppm = 1880 µg/m³
                # O3: 1 ppm = 1960 µg/m³
                if target_param == 'no2':
                    return value * 1880
                elif target_param == 'o3':
                    return value * 1960
            
            return float(value)
            
        except Exception:
            return float(value)

            return result
            
        except Exception as e:
            logger.error(f"Error in _fetch_openaq_data_sync: {e}")
            return None

    def _calculate_aqi(self, pollutants: Dict[str, float]) -> int:
        """
        Calculate AQI from pollutant concentrations using EPA AQI formula.
        """
        # Use PM2.5 as primary indicator for AQI calculation
        pm25 = pollutants.get("pm25", 0)
        
        # EPA AQI breakpoints for PM2.5 (24-hour average)
        if pm25 <= 12.0:
            return int(50 * pm25 / 12.0)
        elif pm25 <= 35.4:
            return int(50 + 50 * (pm25 - 12.0) / (35.4 - 12.0))
        elif pm25 <= 55.4:
            return int(100 + 50 * (pm25 - 35.4) / (55.4 - 35.4))
        elif pm25 <= 150.4:
            return int(150 + 50 * (pm25 - 55.4) / (150.4 - 55.4))
        elif pm25 <= 250.4:
            return int(200 + 100 * (pm25 - 150.4) / (250.4 - 150.4))
        else:
            return min(500, int(300 + 200 * (pm25 - 250.4) / (500 - 250.4)))
    
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
        Return enhanced mock data when API is unavailable.
        OpenAQ currently has limited coverage in US cities.
        """
        import random
        
        # Make mock data more realistic based on city
        city_lower = city.lower()
        if city_lower in self.city_coords:
            # Use some realistic variation based on location
            base_pm25 = random.uniform(15, 45)  # More realistic PM2.5 range
        else:
            base_pm25 = random.uniform(20, 35)  # Default range
        
        pollutants = {
            "pm25": round(base_pm25, 1),
            "pm10": round(base_pm25 * 1.5, 1),
            "no2": round(random.uniform(10, 30), 1),
            "o3": round(random.uniform(30, 80), 1)
        }
        
        aqi = self._calculate_aqi(pollutants)
        category = self._get_aqi_category(aqi)
        
        return {
            "city": city,
            "aqi": aqi,
            "category": category,
            "pollutants": pollutants,
            "source": "Mock Data (OpenAQ has limited US coverage)",
            "timestamp": datetime.now(),
            "note": "OpenAQ database currently has limited monitoring stations in US cities. Using realistic mock data based on typical urban air quality patterns."
        }