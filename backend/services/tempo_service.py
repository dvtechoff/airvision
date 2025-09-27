"""
Enhanced TEMPO Service with Real Earth Data Integration
Integrates with NASA EarthData and real-time processing
"""

import asyncio
import aiohttp
import requests
import os
import json
import numpy as np
import xarray as xr
import netCDF4 as nc
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging
from pathlib import Path
import tempfile
import shutil
from dotenv import load_dotenv

# Import our real-time processor
try:
    from services.realtime_data_processor import realtime_processor, ProcessedData, DataQuality
except ImportError:
    from .realtime_data_processor import realtime_processor, ProcessedData, DataQuality

load_dotenv()

logger = logging.getLogger(__name__)

class TEMPOService:
    """
    Enhanced TEMPO service with real NASA EarthData integration,
    real-time processing, and intelligent caching
    """
    
    def __init__(self):
        self.earthdata_url = "https://cmr.earthdata.nasa.gov/search"
        self.tempo_base_url = "https://asdc.larc.nasa.gov/data/TEMPO"
        self.username = os.getenv('EARTHDATA_USERNAME')
        self.password = os.getenv('EARTHDATA_PASSWORD')
        self.session = None
        self.tempo_collections = {
            'no2_l3': 'C2764221647-LARC_ASDC',  # TEMPO NO2 Level 3
            'o3_l3': 'C2764221648-LARC_ASDC',   # TEMPO O3 Level 3
            'hcho_l3': 'C2764221649-LARC_ASDC', # TEMPO HCHO Level 3
        }
        self.temp_dir = Path(tempfile.gettempdir()) / "tempo_data"
        self.temp_dir.mkdir(exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(self.username, self.password),
            timeout=aiohttp.ClientTimeout(total=30)
        )
        await realtime_processor.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_tempo_data(self, city: str) -> Dict[str, Any]:
        """
        Get real TEMPO satellite data for a city with real-time processing
        """
        lat, lon = self.get_city_coordinates(city)
        
        try:
            # Try to get real data first
            real_data = await self.fetch_real_tempo_data(lat, lon)
            if real_data:
                logger.info(f"Using real TEMPO data for {city}")
                return await realtime_processor.get_processed_data(city, lat, lon, real_data)
            else:
                logger.info(f"Real data unavailable, using enhanced mock for {city}")
                mock_data = self._get_enhanced_mock_data(city, lat, lon)
                return await realtime_processor.get_processed_data(city, lat, lon, mock_data)
                
        except Exception as e:
            logger.error(f"Error getting TEMPO data for {city}: {e}")
            # Fallback to enhanced mock data
            mock_data = self._get_enhanced_mock_data(city, lat, lon)
            return await realtime_processor.get_processed_data(city, lat, lon, mock_data)
    
    async def fetch_real_tempo_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """
        Fetch real TEMPO data from NASA EarthData API
        """
        try:
            if not self.username or not self.password:
                logger.warning("NASA EarthData credentials not provided")
                return None
            
            # Search for recent TEMPO data
            search_results = await self._search_tempo_granules(lat, lon)
            if not search_results:
                logger.info("No recent TEMPO data found")
                return None
            
            # Process the most recent granule
            latest_granule = search_results[0]
            processed_data = await self._process_tempo_granule(latest_granule, lat, lon)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error fetching real TEMPO data: {e}")
            return None
    
    async def _search_tempo_granules(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Search for TEMPO granules near the given coordinates"""
        try:
            # Search for NO2 data (most commonly available)
            collection_id = self.tempo_collections['no2_l3']
            
            # Create bounding box around the point
            bbox_size = 0.5  # degrees
            bbox = f"{lon-bbox_size},{lat-bbox_size},{lon+bbox_size},{lat+bbox_size}"
            
            # Search for data from the last 7 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            temporal = f"{start_date.strftime('%Y-%m-%d')}T00:00:00Z,{end_date.strftime('%Y-%m-%d')}T23:59:59Z"
            
            search_url = f"{self.earthdata_url}/granules.json"
            params = {
                'collection_concept_id': collection_id,
                'bounding_box': bbox,
                'temporal': temporal,
                'page_size': 5,
                'sort_key': 'start_date',
                'sort_order': 'desc'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    granules = data.get('feed', {}).get('entry', [])
                    
                    logger.info(f"Found {len(granules)} TEMPO granules")
                    return granules
                else:
                    logger.warning(f"Search failed with status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching for TEMPO granules: {e}")
            return []
    
    async def _process_tempo_granule(self, granule: Dict[str, Any], 
                                   lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Process a TEMPO granule and extract data for the given coordinates"""
        try:
            # Get data download links
            links = granule.get('links', [])
            data_links = [link for link in links if 'data' in link.get('rel', '')]
            
            if not data_links:
                logger.warning("No data links found in granule")
                return None
            
            # Download and process the first data file
            data_url = data_links[0]['href']
            file_path = await self._download_tempo_file(data_url)
            
            if not file_path:
                return None
            
            # Process the NetCDF file
            processed_data = await self._process_netcdf_file(file_path, lat, lon, granule)
            
            # Clean up temporary file
            if file_path.exists():
                file_path.unlink()
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing TEMPO granule: {e}")
            return None
    
    async def _download_tempo_file(self, data_url: str) -> Optional[Path]:
        """Download TEMPO data file"""
        try:
            filename = data_url.split('/')[-1]
            file_path = self.temp_dir / filename
            
            async with self.session.get(data_url) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    logger.info(f"Downloaded TEMPO file: {filename}")
                    return file_path
                else:
                    logger.warning(f"Download failed with status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading TEMPO file: {e}")
            return None
    
    async def _process_netcdf_file(self, file_path: Path, lat: float, lon: float,
                                 granule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process NetCDF file and extract data for specific coordinates"""
        try:
            # Process in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._process_netcdf_sync, file_path, lat, lon, granule
            )
            return result
            
        except Exception as e:
            logger.error(f"Error processing NetCDF file: {e}")
            return None
    
    def _process_netcdf_sync(self, file_path: Path, lat: float, lon: float,
                           granule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Synchronous NetCDF processing"""
        try:
            with nc.Dataset(str(file_path)) as ds:
                # Extract coordinates
                lats = ds.variables['latitude'][:]
                lons = ds.variables['longitude'][:]
                
                # Find nearest pixel
                lat_idx = np.argmin(np.abs(lats - lat))
                lon_idx = np.argmin(np.abs(lons - lon))
                
                # Extract measurements
                measurements = {}
                quality_flags = {}
                
                # Try to access product group
                if 'product' in ds.groups:
                    prod = ds.groups['product']
                    
                    # NO2 measurements
                    if 'vertical_column_troposphere' in prod.variables:
                        no2_var = prod.variables['vertical_column_troposphere']
                        no2_data = no2_var[lat_idx, lon_idx]
                        fill_value = no2_var.getncattr('_FillValue')
                        
                        if no2_data != fill_value and not np.isnan(no2_data):
                            measurements['no2_column'] = float(no2_data)
                    
                    # O3 measurements
                    if 'vertical_column_o3' in prod.variables:
                        o3_var = prod.variables['vertical_column_o3']
                        o3_data = o3_var[lat_idx, lon_idx]
                        fill_value = o3_var.getncattr('_FillValue')
                        
                        if o3_data != fill_value and not np.isnan(o3_data):
                            measurements['o3_column'] = float(o3_data)
                    
                    # Quality flags
                    if 'main_data_quality_flag' in prod.variables:
                        qf_data = prod.variables['main_data_quality_flag'][lat_idx, lon_idx]
                        quality_flags['data_quality_flag'] = int(qf_data)
                
                # Cloud fraction
                if 'cloud_fraction' in ds.variables:
                    cloud_data = ds.variables['cloud_fraction'][lat_idx, lon_idx]
                    measurements['cloud_fraction'] = float(cloud_data)
                
                # Solar zenith angle
                if 'solar_zenith_angle' in ds.variables:
                    sza_data = ds.variables['solar_zenith_angle'][lat_idx, lon_idx]
                    measurements['solar_zenith_angle'] = float(sza_data)
                
                # Aerosol optical depth (if available)
                if 'aerosol_optical_depth' in ds.variables:
                    aod_data = ds.variables['aerosol_optical_depth'][lat_idx, lon_idx]
                    measurements['aerosol_optical_depth'] = float(aod_data)
                
                # HCHO (if available)
                if 'hcho_column' in ds.variables:
                    hcho_data = ds.variables['hcho_column'][lat_idx, lon_idx]
                    measurements['hcho_column'] = float(hcho_data)
                
                # Get granule metadata
                granule_id = granule.get('id', 'unknown')
                start_time = granule.get('time_start', datetime.now().isoformat())
                
                # Parse start time
                try:
                    satellite_pass_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                except:
                    satellite_pass_time = datetime.now()
                
                return {
                    'city': f"Location ({lat:.2f}, {lon:.2f})",
                    'coordinates': {'latitude': lat, 'longitude': lon},
                    'source': 'NASA TEMPO Satellite (Real Data)',
                    'timestamp': datetime.now(),
                    'satellite_pass_time': satellite_pass_time,
                    'measurements': measurements,
                    'quality_flags': quality_flags,
                    'metadata': {
                        'granule_id': granule_id,
                        'file_name': file_path.name,
                        'processing_level': 'L3',
                        'spatial_resolution': '2.1 km x 4.4 km',
                        'temporal_resolution': 'Hourly',
                        'retrieval_algorithm': 'TEMPO Standard Product v1.0'
                    }
                }
                
        except Exception as e:
            logger.error(f"Error processing NetCDF file: {e}")
            return None
    
    def _get_enhanced_mock_data(self, city: str, lat: float, lon: float) -> Dict[str, Any]:
        """
        Generate enhanced realistic TEMPO satellite data based on real-world patterns.
        This is used as fallback when real data is not available.
        """
        import random
        from math import sin, cos, pi
        
        # Time-based variations
        hour = datetime.now().hour
        is_rush_hour = hour in [7, 8, 9, 17, 18, 19]
        is_daytime = 6 <= hour <= 18
        
        # City-specific pollution factors
        pollution_factors = {
            'new york': {'base_factor': 1.6, 'industrial': True, 'coastal': True},
            'los angeles': {'base_factor': 2.1, 'industrial': True, 'coastal': True},
            'chicago': {'base_factor': 1.5, 'industrial': True, 'coastal': False},
            'houston': {'base_factor': 1.9, 'industrial': True, 'coastal': True},
            'phoenix': {'base_factor': 1.4, 'industrial': False, 'coastal': False},
            'philadelphia': {'base_factor': 1.5, 'industrial': True, 'coastal': False},
            'san antonio': {'base_factor': 1.3, 'industrial': False, 'coastal': False},
            'san diego': {'base_factor': 1.2, 'industrial': False, 'coastal': True},
            'dallas': {'base_factor': 1.4, 'industrial': True, 'coastal': False},
            'san francisco': {'base_factor': 1.1, 'industrial': False, 'coastal': True},
            'denver': {'base_factor': 1.3, 'industrial': False, 'coastal': False},
            'seattle': {'base_factor': 1.0, 'industrial': False, 'coastal': True},
            'atlanta': {'base_factor': 1.4, 'industrial': True, 'coastal': False},
            'miami': {'base_factor': 1.2, 'industrial': False, 'coastal': True},
            'boston': {'base_factor': 1.3, 'industrial': False, 'coastal': True},
            'detroit': {'base_factor': 1.6, 'industrial': True, 'coastal': False},
            'washington': {'base_factor': 1.3, 'industrial': False, 'coastal': False},
            'portland': {'base_factor': 1.1, 'industrial': False, 'coastal': True},
            'toronto': {'base_factor': 1.3, 'industrial': True, 'coastal': False},
            'vancouver': {'base_factor': 1.0, 'industrial': False, 'coastal': True},
            'montreal': {'base_factor': 1.2, 'industrial': True, 'coastal': False},
            'calgary': {'base_factor': 1.1, 'industrial': True, 'coastal': False},
            'ottawa': {'base_factor': 1.0, 'industrial': False, 'coastal': False},
            'mexico city': {'base_factor': 2.5, 'industrial': True, 'coastal': False},
            'guadalajara': {'base_factor': 1.8, 'industrial': True, 'coastal': False},
            'monterrey': {'base_factor': 1.7, 'industrial': True, 'coastal': False},
        }
        
        factor = pollution_factors.get(city.lower(), {'base_factor': 1.2, 'industrial': False, 'coastal': False})
        base_multiplier = factor['base_factor']
        
        # Rush hour multiplier
        rush_multiplier = 1.4 if is_rush_hour else 1.0
        
        # Daytime ozone production
        ozone_multiplier = 1.3 if is_daytime else 0.8
        
        # Realistic TEMPO measurements with proper units
        no2_column = random.uniform(0.8, 4.2) * base_multiplier * rush_multiplier
        o3_column = random.uniform(250, 380) * ozone_multiplier
        hcho_column = random.uniform(0.3, 1.8) * base_multiplier
        aerosol_optical_depth = random.uniform(0.05, 0.6) * base_multiplier
        
        # Quality flags based on realistic satellite conditions
        cloud_cover = random.uniform(0, 0.8)
        solar_zenith_angle = random.uniform(20, 70)
        
        return {
            'city': city,
            'coordinates': {'latitude': lat, 'longitude': lon},
            'source': 'NASA TEMPO Satellite (Enhanced Mock)',
            'timestamp': datetime.now(),
            'satellite_pass_time': datetime.now() - timedelta(minutes=random.randint(15, 120)),
            'measurements': {
                'no2_column': round(no2_column, 3),
                'o3_column': round(o3_column, 1),
                'hcho_column': round(hcho_column, 3),
                'aerosol_optical_depth': round(aerosol_optical_depth, 3),
                'cloud_fraction': round(cloud_cover, 2),
                'solar_zenith_angle': round(solar_zenith_angle, 1)
            },
            'quality_flags': {
                'cloud_cover': cloud_cover,
                'solar_zenith_angle': solar_zenith_angle,
                'pixel_corner_coordinates': [
                    [lat - 0.01, lon - 0.01],
                    [lat - 0.01, lon + 0.01],
                    [lat + 0.01, lon + 0.01],
                    [lat + 0.01, lon - 0.01]
                ]
            },
            'metadata': {
                'retrieval_algorithm': 'TEMPO Standard Product v1.0',
                'spatial_resolution': '2.1 km x 4.4 km',
                'temporal_resolution': 'Hourly',
                'processing_level': 'L3',
                'data_type': 'enhanced_mock'
            }
        }
    
    def get_city_coordinates(self, city: str) -> Tuple[float, float]:
        """Get latitude and longitude coordinates for a city"""
        city_coords = {
            # United States
            "new york": (40.7128, -74.0060),
            "los angeles": (34.0522, -118.2437),
            "chicago": (41.8781, -87.6298),
            "houston": (29.7604, -95.3698),
            "phoenix": (33.4484, -112.0740),
            "philadelphia": (39.9526, -75.1652),
            "san antonio": (29.4241, -98.4936),
            "san diego": (32.7157, -117.1611),
            "dallas": (32.7767, -96.7970),
            "san francisco": (37.7749, -122.4194),
            "denver": (39.7392, -104.9903),
            "seattle": (47.6062, -122.3321),
            "atlanta": (33.7490, -84.3880),
            "miami": (25.7617, -80.1918),
            "boston": (42.3601, -71.0589),
            "detroit": (42.3314, -83.0458),
            "washington": (38.9072, -77.0369),
            "portland": (45.5152, -122.6784),
            
            # Canada
            "toronto": (43.6532, -79.3832),
            "vancouver": (49.2827, -123.1207),
            "montreal": (45.5017, -73.5673),
            "calgary": (51.0447, -114.0719),
            "ottawa": (45.4215, -75.6972),
            "edmonton": (53.5461, -113.4938),
            "quebec city": (46.8139, -71.2082),
            
            # Mexico (northern regions)
            "mexico city": (19.4326, -99.1332),
            "guadalajara": (20.6597, -103.3496),
            "monterrey": (25.6866, -100.3161),
            "tijuana": (32.5027, -117.0382),
        }
        
        return city_coords.get(city.lower(), (40.7128, -74.0060))  # Default to New York
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return await realtime_processor.get_cache_stats()
    
    async def clear_cache(self):
        """Clear all cached data"""
        await realtime_processor.clear_cache()
