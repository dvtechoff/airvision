#!/usr/bin/env python3
"""
TEMPO Data Analysis Test
Shows exactly what the TEMPO service returns for analysis
"""

import asyncio
import json
import logging
from services.tempo_service_earthaccess import tempo_service_earthaccess
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

load_dotenv()

async def analyze_tempo_data():
    print("🛰️  TEMPO SATELLITE DATA ANALYSIS")
    print("=" * 60)
    
    # Test cities in TEMPO coverage area (North America)
    test_cities = [
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
        {"name": "Chicago", "lat": 41.8781, "lon": -87.6298},
        {"name": "Houston", "lat": 29.7604, "lon": -95.3698},
        {"name": "Toronto", "lat": 43.6532, "lon": -79.3832},
    ]
    
    for city_info in test_cities:
        city = city_info["name"]
        lat = city_info["lat"] 
        lon = city_info["lon"]
        
        print(f"\n🌍 Testing TEMPO data for {city}")
        print(f"📍 Coordinates: {lat}, {lon}")
        print("-" * 40)
        
        try:
            # Get TEMPO data
            tempo_data = await tempo_service_earthaccess.get_tempo_data(
                city=city, 
                lat=lat, 
                lon=lon
            )
            
            if tempo_data:
                print("✅ TEMPO Data Retrieved Successfully!")
                print("\n📊 COMPLETE DATA STRUCTURE:")
                print("=" * 40)
                
                # Pretty print the entire data structure
                formatted_data = json.dumps(tempo_data, indent=2, default=str)
                print(formatted_data)
                
                # Analyze key components
                print(f"\n🔍 KEY DATA ANALYSIS for {city}:")
                print("-" * 30)
                
                # Basic info
                if 'source' in tempo_data:
                    print(f"📡 Source: {tempo_data['source']}")
                if 'data_type' in tempo_data:
                    print(f"💾 Data Type: {tempo_data['data_type']}")
                if 'satellite' in tempo_data:
                    print(f"🛰️  Satellite: {tempo_data['satellite']}")
                if 'spatial_resolution' in tempo_data:
                    print(f"🔍 Resolution: {tempo_data['spatial_resolution']}")
                    
                # Air quality data
                if 'air_quality' in tempo_data:
                    aq = tempo_data['air_quality']
                    print(f"\n🌪️  AIR QUALITY METRICS:")
                    print(f"   AQI: {aq.get('aqi', 'N/A')}")
                    print(f"   Category: {aq.get('category', 'N/A')}")
                    print(f"   Primary Pollutant: {aq.get('primary_pollutant', 'N/A')}")
                
                # Measurements
                if 'measurements' in tempo_data:
                    meas = tempo_data['measurements']
                    print(f"\n📏 SATELLITE MEASUREMENTS:")
                    for key, value in meas.items():
                        if isinstance(value, (int, float)):
                            print(f"   {key}: {value:.2e}")
                        else:
                            print(f"   {key}: {value}")
                
                # Quality flags
                if 'quality_flags' in tempo_data:
                    quality = tempo_data['quality_flags']
                    print(f"\n🔍 DATA QUALITY:")
                    for key, value in quality.items():
                        print(f"   {key}: {value}")
                
                print("\n" + "="*50)
                
            else:
                print("❌ No TEMPO data available")
                
        except Exception as e:
            print(f"❌ Error getting TEMPO data for {city}: {e}")
            
        print("\n" + "="*60)

async def test_tempo_api_structure():
    """Test what the TEMPO API structure looks like for integration"""
    
    print("\n🔧 TEMPO API INTEGRATION ANALYSIS")
    print("=" * 50)
    
    # Test New York specifically
    tempo_data = await tempo_service_earthaccess.get_tempo_data("New York")
    
    if tempo_data:
        print("📋 DATA FIELDS AVAILABLE FOR FRONTEND:")
        print("-" * 40)
        
        def analyze_structure(data, prefix=""):
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"{prefix}{key}: (object)")
                    analyze_structure(value, prefix + "  ")
                elif isinstance(value, list):
                    print(f"{prefix}{key}: (array of {len(value)} items)")
                    if value and isinstance(value[0], dict):
                        print(f"{prefix}  Sample item structure:")
                        analyze_structure(value[0], prefix + "    ")
                else:
                    print(f"{prefix}{key}: {type(value).__name__} = {value}")
        
        analyze_structure(tempo_data)
        
        print(f"\n💡 RECOMMENDED USAGE IN FRONTEND:")
        print("-" * 40)
        print("// Access TEMPO air quality data:")
        print("const tempoAQI = tempoData.air_quality?.aqi")
        print("const tempoCategory = tempoData.air_quality?.category")
        print("")
        print("// Access satellite measurements:")
        print("const no2Column = tempoData.measurements?.no2_column")
        print("const o3Column = tempoData.measurements?.o3_column")
        print("const cloudFraction = tempoData.measurements?.cloud_fraction")
        print("")
        print("// Check data quality:")
        print("const dataQuality = tempoData.quality_flags?.data_quality")
        print("const isSimulated = tempoData.source?.includes('Simulated')")
        
    else:
        print("❌ No TEMPO data to analyze")

if __name__ == "__main__":
    asyncio.run(analyze_tempo_data())
    asyncio.run(test_tempo_api_structure())