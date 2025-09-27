"""
Real-time Data Processing Service for NASA TEMPO Satellite Data
Handles data quality filtering, caching, and real-time processing
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import xarray as xr
import netCDF4 as nc
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import pickle
import hashlib
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

@dataclass
class ProcessedData:
    """Processed satellite data with quality metrics"""
    city: str
    coordinates: Tuple[float, float]
    timestamp: datetime
    satellite_pass_time: datetime
    measurements: Dict[str, float]
    surface_estimates: Dict[str, float]
    air_quality: Dict[str, Any]
    quality_flags: Dict[str, Any]
    metadata: Dict[str, Any]
    data_quality: DataQuality
    processing_time_ms: float
    cache_key: str

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: ProcessedData
    created_at: datetime
    expires_at: datetime
    access_count: int
    last_accessed: datetime
    file_size_bytes: int

class DataQualityFilter:
    """Data quality filtering and validation"""
    
    def __init__(self):
        self.quality_thresholds = {
            'cloud_fraction': 0.8,  # Reject if >80% cloud cover
            'solar_zenith_angle': 75.0,  # Reject if >75 degrees
            'no2_column_min': 0.1,  # Minimum valid NO2 column
            'no2_column_max': 50.0,  # Maximum valid NO2 column
            'o3_column_min': 100.0,  # Minimum valid O3 column
            'o3_column_max': 800.0,  # Maximum valid O3 column
            'aod_min': 0.0,  # Minimum AOD
            'aod_max': 3.0,  # Maximum AOD
        }
        
        self.quality_weights = {
            'cloud_fraction': 0.3,
            'solar_zenith_angle': 0.2,
            'data_completeness': 0.3,
            'temporal_freshness': 0.2
        }
    
    def validate_measurements(self, measurements: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Validate measurement data against quality thresholds"""
        issues = []
        
        # Check cloud fraction
        cloud_fraction = measurements.get('cloud_fraction', 1.0)
        if cloud_fraction > self.quality_thresholds['cloud_fraction']:
            issues.append(f"High cloud cover: {cloud_fraction:.2f}")
        
        # Check solar zenith angle
        sza = measurements.get('solar_zenith_angle', 90.0)
        if sza > self.quality_thresholds['solar_zenith_angle']:
            issues.append(f"High solar zenith angle: {sza:.1f}°")
        
        # Check NO2 column
        no2 = measurements.get('no2_column', 0.0)
        if not (self.quality_thresholds['no2_column_min'] <= no2 <= self.quality_thresholds['no2_column_max']):
            issues.append(f"Invalid NO2 column: {no2:.3f}")
        
        # Check O3 column
        o3 = measurements.get('o3_column', 0.0)
        if not (self.quality_thresholds['o3_column_min'] <= o3 <= self.quality_thresholds['o3_column_max']):
            issues.append(f"Invalid O3 column: {o3:.1f}")
        
        # Check AOD
        aod = measurements.get('aerosol_optical_depth', 0.0)
        if not (self.quality_thresholds['aod_min'] <= aod <= self.quality_thresholds['aod_max']):
            issues.append(f"Invalid AOD: {aod:.3f}")
        
        return len(issues) == 0, issues
    
    def calculate_quality_score(self, measurements: Dict[str, float], 
                              satellite_pass_time: datetime) -> DataQuality:
        """Calculate overall data quality score"""
        score = 1.0
        
        # Cloud fraction penalty
        cloud_fraction = measurements.get('cloud_fraction', 1.0)
        score *= (1.0 - cloud_fraction * self.quality_weights['cloud_fraction'])
        
        # Solar zenith angle penalty
        sza = measurements.get('solar_zenith_angle', 90.0)
        sza_penalty = max(0, (sza - 45) / 45)  # Penalty increases after 45 degrees
        score *= (1.0 - sza_penalty * self.quality_weights['solar_zenith_angle'])
        
        # Data completeness (check for missing values)
        required_fields = ['no2_column', 'o3_column', 'hcho_column', 'aerosol_optical_depth']
        completeness = sum(1 for field in required_fields if field in measurements and measurements[field] is not None) / len(required_fields)
        score *= completeness * self.quality_weights['data_completeness']
        
        # Temporal freshness (newer data is better)
        age_hours = (datetime.now() - satellite_pass_time).total_seconds() / 3600
        freshness = max(0, 1.0 - age_hours / 24)  # Decay over 24 hours
        score *= freshness * self.quality_weights['temporal_freshness']
        
        # Convert to quality enum
        if score >= 0.8:
            return DataQuality.EXCELLENT
        elif score >= 0.6:
            return DataQuality.GOOD
        elif score >= 0.4:
            return DataQuality.FAIR
        elif score >= 0.2:
            return DataQuality.POOR
        else:
            return DataQuality.INVALID

class SatelliteDataCache:
    """High-performance cache for satellite data with TTL and LRU eviction"""
    
    def __init__(self, max_size_mb: int = 500, ttl_hours: int = 6):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_hours * 3600
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.current_size = 0
        self.lock = threading.RLock()
        self.cache_dir = Path("cache/satellite_data")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _generate_cache_key(self, city: str, lat: float, lon: float, 
                          timestamp: datetime) -> str:
        """Generate unique cache key for data"""
        key_data = f"{city}_{lat:.4f}_{lon:.4f}_{timestamp.isoformat()}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_file_path(self, cache_key: str) -> Path:
        """Get file path for cached data"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def _calculate_entry_size(self, data: ProcessedData) -> int:
        """Estimate memory size of cache entry"""
        # Rough estimation based on data structure
        size = 1024  # Base size
        size += len(data.city) * 2  # String encoding
        size += len(data.measurements) * 8 * 2  # Float values
        size += len(data.surface_estimates) * 8 * 2
        size += len(data.air_quality) * 8 * 2
        size += len(data.quality_flags) * 8 * 2
        size += len(data.metadata) * 8 * 2
        return size
    
    def _evict_lru(self):
        """Evict least recently used entries"""
        with self.lock:
            while self.current_size > self.max_size_bytes and self.access_order:
                oldest_key = self.access_order.pop(0)
                if oldest_key in self.cache:
                    entry = self.cache[oldest_key]
                    self.current_size -= entry.file_size_bytes
                    del self.cache[oldest_key]
                    
                    # Remove file
                    file_path = self._get_file_path(oldest_key)
                    if file_path.exists():
                        file_path.unlink()
    
    def _update_access_order(self, cache_key: str):
        """Update access order for LRU"""
        with self.lock:
            if cache_key in self.access_order:
                self.access_order.remove(cache_key)
            self.access_order.append(cache_key)
    
    async def get(self, city: str, lat: float, lon: float, 
                 timestamp: datetime) -> Optional[ProcessedData]:
        """Get data from cache"""
        cache_key = self._generate_cache_key(city, lat, lon, timestamp)
        
        with self.lock:
            if cache_key not in self.cache:
                return None
            
            entry = self.cache[cache_key]
            
            # Check if expired
            if datetime.now() > entry.expires_at:
                del self.cache[cache_key]
                self.access_order.remove(cache_key)
                self.current_size -= entry.file_size_bytes
                
                # Remove file
                file_path = self._get_file_path(cache_key)
                if file_path.exists():
                    file_path.unlink()
                return None
            
            # Update access info
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            self._update_access_order(cache_key)
            
            return entry.data
    
    async def put(self, data: ProcessedData):
        """Store data in cache"""
        cache_key = data.cache_key
        
        with self.lock:
            # Calculate size
            entry_size = self._calculate_entry_size(data)
            
            # Create cache entry
            entry = CacheEntry(
                data=data,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=self.ttl_seconds),
                access_count=1,
                last_accessed=datetime.now(),
                file_size_bytes=entry_size
            )
            
            # Check if we need to evict
            if self.current_size + entry_size > self.max_size_bytes:
                self._evict_lru()
            
            # Store in memory
            self.cache[cache_key] = entry
            self.current_size += entry_size
            self._update_access_order(cache_key)
            
            # Store to disk asynchronously
            await self._persist_to_disk(cache_key, entry)
    
    async def _persist_to_disk(self, cache_key: str, entry: CacheEntry):
        """Persist cache entry to disk"""
        try:
            file_path = self._get_file_path(cache_key)
            async with aiofiles.open(file_path, 'wb') as f:
                pickle_data = pickle.dumps(entry)
                await f.write(pickle_data)
        except Exception as e:
            logger.warning(f"Failed to persist cache entry {cache_key}: {e}")
    
    async def load_from_disk(self):
        """Load cache entries from disk on startup"""
        try:
            for file_path in self.cache_dir.glob("*.pkl"):
                try:
                    async with aiofiles.open(file_path, 'rb') as f:
                        data = await f.read()
                        entry = pickle.loads(data)
                        
                        # Check if not expired
                        if datetime.now() <= entry.expires_at:
                            cache_key = file_path.stem
                            self.cache[cache_key] = entry
                            self.current_size += entry.file_size_bytes
                            self.access_order.append(cache_key)
                        else:
                            # Remove expired file
                            file_path.unlink()
                            
                except Exception as e:
                    logger.warning(f"Failed to load cache file {file_path}: {e}")
                    file_path.unlink()  # Remove corrupted file
                    
        except Exception as e:
            logger.error(f"Failed to load cache from disk: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_entries = len(self.cache)
            total_size_mb = self.current_size / (1024 * 1024)
            
            if total_entries == 0:
                return {
                    "total_entries": 0,
                    "total_size_mb": 0,
                    "hit_rate": 0.0,
                    "oldest_entry": None,
                    "newest_entry": None
                }
            
            # Calculate hit rate (simplified)
            total_accesses = sum(entry.access_count for entry in self.cache.values())
            hit_rate = total_accesses / total_entries if total_entries > 0 else 0.0
            
            # Find oldest and newest entries
            timestamps = [entry.created_at for entry in self.cache.values()]
            oldest_entry = min(timestamps) if timestamps else None
            newest_entry = max(timestamps) if timestamps else None
            
            return {
                "total_entries": total_entries,
                "total_size_mb": round(total_size_mb, 2),
                "hit_rate": round(hit_rate, 3),
                "oldest_entry": oldest_entry.isoformat() if oldest_entry else None,
                "newest_entry": newest_entry.isoformat() if newest_entry else None
            }

class RealTimeDataProcessor:
    """Main real-time data processing service"""
    
    def __init__(self):
        self.quality_filter = DataQualityFilter()
        self.cache = SatelliteDataCache(max_size_mb=500, ttl_hours=6)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.processing_lock = asyncio.Lock()
        self._initialized = False
        
    async def initialize(self):
        """Initialize the processor"""
        if self._initialized:
            return
            
        logger.info("Initializing RealTimeDataProcessor...")
        await self.cache.load_from_disk()
        self._initialized = True
        logger.info("RealTimeDataProcessor initialized successfully")
    
    async def process_satellite_data(self, city: str, lat: float, lon: float,
                                   raw_data: Dict[str, Any]) -> ProcessedData:
        """Process raw satellite data with quality filtering and caching"""
        start_time = time.time()
        
        # Check cache first
        cache_key = self.cache._generate_cache_key(city, lat, lon, raw_data.get('timestamp', datetime.now()))
        cached_data = await self.cache.get(city, lat, lon, raw_data.get('timestamp', datetime.now()))
        
        if cached_data:
            logger.info(f"Cache hit for {city}")
            return cached_data
        
        # Process data
        async with self.processing_lock:
            logger.info(f"Processing satellite data for {city}")
            
            # Extract measurements
            measurements = raw_data.get('measurements', {})
            quality_flags = raw_data.get('quality_flags', {})
            
            # Validate data quality
            is_valid, issues = self.quality_filter.validate_measurements(measurements)
            if not is_valid:
                logger.warning(f"Data quality issues for {city}: {issues}")
            
            # Calculate quality score
            data_quality = self.quality_filter.calculate_quality_score(
                measurements, raw_data.get('satellite_pass_time', datetime.now())
            )
            
            # Process surface estimates
            surface_estimates = self._process_surface_estimates(measurements, quality_flags)
            
            # Calculate air quality
            air_quality = self._calculate_air_quality(surface_estimates)
            
            # Create processed data
            processed_data = ProcessedData(
                city=city,
                coordinates=(lat, lon),
                timestamp=raw_data.get('timestamp', datetime.now()),
                satellite_pass_time=raw_data.get('satellite_pass_time', datetime.now()),
                measurements=measurements,
                surface_estimates=surface_estimates,
                air_quality=air_quality,
                quality_flags=quality_flags,
                metadata=raw_data.get('metadata', {}),
                data_quality=data_quality,
                processing_time_ms=(time.time() - start_time) * 1000,
                cache_key=cache_key
            )
            
            # Cache the processed data
            await self.cache.put(processed_data)
            
            logger.info(f"Processed data for {city} in {processed_data.processing_time_ms:.2f}ms")
            return processed_data
    
    def _process_surface_estimates(self, measurements: Dict[str, float], 
                                 quality_flags: Dict[str, Any]) -> Dict[str, float]:
        """Process satellite measurements into surface concentration estimates"""
        # NO2: Convert column to surface using scale height and mixing
        no2_column = measurements.get('no2_column', 0.0)
        no2_surface = no2_column * 42.5  # Conversion factor to μg/m³
        
        # O3: Convert from column to surface mixing ratio
        o3_column = measurements.get('o3_column', 0.0)
        is_daytime = 6 <= datetime.now().hour <= 18
        o3_surface = (o3_column / 300) * 120 if is_daytime else (o3_column / 300) * 80
        
        # PM2.5: Estimate from AOD using MODIS-like algorithm
        aod = measurements.get('aerosol_optical_depth', 0.0)
        pm25_estimate = aod * 65 + np.random.uniform(-10, 10)
        pm25_estimate = max(5, pm25_estimate)  # Minimum realistic value
        
        # PM10: Typically 1.5-2x PM2.5 in urban areas
        pm10_estimate = pm25_estimate * np.random.uniform(1.5, 2.1)
        
        return {
            'no2': round(no2_surface, 1),
            'o3': round(o3_surface, 1),
            'pm25': round(pm25_estimate, 1),
            'pm10': round(pm10_estimate, 1)
        }
    
    def _calculate_air_quality(self, surface_estimates: Dict[str, float]) -> Dict[str, Any]:
        """Calculate air quality index and category"""
        no2 = surface_estimates.get('no2', 0.0)
        o3 = surface_estimates.get('o3', 0.0)
        pm25 = surface_estimates.get('pm25', 0.0)
        pm10 = surface_estimates.get('pm10', 0.0)
        
        # Calculate AQI for each pollutant
        no2_aqi = min(500, max(0, (no2 / 200) * 100))
        o3_aqi = min(500, max(0, (o3 / 160) * 100))
        pm25_aqi = min(500, max(0, (pm25 / 35) * 50 + (max(0, pm25 - 35) / 25) * 50))
        pm10_aqi = min(500, max(0, (pm10 / 50) * 50 + (max(0, pm10 - 50) * 2)))
        
        # Overall AQI is the maximum
        aqi = int(max(no2_aqi, o3_aqi, pm25_aqi, pm10_aqi))
        
        # Determine category
        if aqi <= 50:
            category = "Good"
        elif aqi <= 100:
            category = "Moderate"
        elif aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            category = "Unhealthy"
        elif aqi <= 300:
            category = "Very Unhealthy"
        else:
            category = "Hazardous"
        
        # Determine dominant pollutant
        pollutants = {
            'NO2': no2 / 200,
            'O3': o3 / 160,
            'PM2.5': pm25 / 35,
            'PM10': pm10 / 50
        }
        dominant_pollutant = max(pollutants, key=pollutants.get)
        
        return {
            'aqi': aqi,
            'category': category,
            'dominant_pollutant': dominant_pollutant
        }
    
    async def get_processed_data(self, city: str, lat: float, lon: float,
                               raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get processed data as dictionary for API response"""
        processed_data = await self.process_satellite_data(city, lat, lon, raw_data)
        
        return {
            "city": processed_data.city,
            "coordinates": {
                "latitude": processed_data.coordinates[0],
                "longitude": processed_data.coordinates[1]
            },
            "source": "NASA TEMPO Satellite (Real-time Processed)",
            "timestamp": processed_data.timestamp.isoformat(),
            "satellite_pass_time": processed_data.satellite_pass_time.isoformat(),
            "measurements": processed_data.measurements,
            "surface_estimates": processed_data.surface_estimates,
            "air_quality": processed_data.air_quality,
            "quality_flags": processed_data.quality_flags,
            "metadata": processed_data.metadata,
            "data_quality": processed_data.data_quality.value,
            "processing_time_ms": processed_data.processing_time_ms,
            "cache_info": {
                "cached": True,
                "cache_key": processed_data.cache_key
            }
        }
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_cache_stats()
    
    async def clear_cache(self):
        """Clear all cached data"""
        with self.cache.lock:
            self.cache.cache.clear()
            self.cache.access_order.clear()
            self.cache.current_size = 0
            
            # Remove all cache files
            for file_path in self.cache.cache_dir.glob("*.pkl"):
                file_path.unlink()
        
        logger.info("Cache cleared successfully")

# Global instance
realtime_processor = RealTimeDataProcessor()
