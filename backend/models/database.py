"""
Database models for OpenAQ locations and air quality data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

class OpenAQLocation(Base):
    """
    Table to store all OpenAQ monitoring locations
    """
    __tablename__ = "openaq_locations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    openaq_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    # Additional location details
    is_mobile = Column(Boolean, default=False)
    is_analysis = Column(Boolean, default=False)
    entity = Column(String(100), nullable=True)
    sensor_type = Column(String(50), nullable=True)
    
    # Available parameters (JSON array)
    parameters = Column(JSON, nullable=True)
    
    # Metadata
    first_updated = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    measurements_count = Column(Integer, default=0)
    
    # Data management
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class LocationQuery(Base):
    """
    Table to cache location queries and their results
    """
    __tablename__ = "location_queries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(String(255), nullable=False, index=True)
    query_lat = Column(Float, nullable=True)
    query_lon = Column(Float, nullable=True)
    
    # Results
    closest_location_id = Column(Integer, nullable=True)  # References openaq_locations.openaq_id
    distance_km = Column(Float, nullable=True)
    
    # Cache metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    hits = Column(Integer, default=1)
    last_used = Column(DateTime, default=datetime.utcnow)

class AirQualityData(Base):
    """
    Table to cache recent air quality measurements
    """
    __tablename__ = "air_quality_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    location_openaq_id = Column(Integer, nullable=False, index=True)
    
    # Measurement data
    parameter = Column(String(10), nullable=False)  # pm25, pm10, o3, no2, etc.
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    
    # Timestamps
    measurement_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Data quality
    coordinates = Column(JSON, nullable=True)  # lat, lon of measurement
    is_valid = Column(Boolean, default=True)

class TEMPOData(Base):
    """
    Table to store TEMPO satellite data
    """
    __tablename__ = "tempo_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Location
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    location_name = Column(String(255), nullable=True)
    
    # TEMPO measurements
    no2_column = Column(Float, nullable=True)
    o3_column = Column(Float, nullable=True)
    data_quality = Column(String(20), nullable=True)
    
    # Metadata
    granule_id = Column(String(100), nullable=True)
    measurement_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Processing info
    processing_level = Column(String(10), nullable=True)
    algorithm_version = Column(String(20), nullable=True)