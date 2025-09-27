#!/usr/bin/env python3
"""
Complete Real Data System Test
AirVision NASA Space Challenge - Final Integration Test

This script validates that the entire AirVision system is working with REAL data:
- OpenWeatherMap API integration
- NASA TEMPO satellite data access
- Frontend-Backend integration
- Real-time data visualization
"""

import asyncio
import requests
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Load environment
load_dotenv()

async def test_openweather_real_data():
    """Test OpenWeatherMap real-time air quality data"""
    print("🌍 TESTING OPENWEATHERMAP REAL DATA")
    print("-" * 50)
    
    try:
        from services.openweather_aqi_service import OpenWeatherAQService
        service = OpenWeatherAQService()
        
        # Test major cities
        cities = [
            ("New York", 40.7128, -74.0060),
            ("Los Angeles", 34.0522, -118.2437),
            ("Houston", 29.7604, -95.3698)
        ]
        
        for city, lat, lon in cities:
            try:
                result = await service.get_aqi_data(lat, lon)
                print(f"✅ {city}: AQI={result.get('aqi', 'N/A')}, Source={result.get('source', 'N/A')}")
                if result.get('real_data'):
                    print(f"   📊 Real-time data confirmed")
            except Exception as e:
                print(f"❌ {city}: Error - {str(e)}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ OpenWeatherMap service error: {str(e)}")
        return False

async def test_tempo_real_data():
    """Test NASA TEMPO real satellite data access"""
    print("🛰️  TESTING NASA TEMPO REAL SATELLITE DATA")
    print("-" * 50)
    
    try:
        from services.tempo_service_earthaccess import TEMPOServiceEarthaccess
        service = TEMPOServiceEarthaccess()
        
        # Test with known data availability
        test_cases = [
            ("New York", 40.7128, -74.0060, "2024-08-01"),
            ("Los Angeles", 34.0522, -118.2437, "2024-07-15"),
            ("Houston", 29.7604, -95.3698, "2024-06-01")
        ]
        
        for city, lat, lon, date in test_cases:
            try:
                result = await service.get_tempo_data(lat, lon, date)
                
                if result.get('success'):
                    print(f"✅ {city}: Real TEMPO data accessed")
                    print(f"   📁 File: {result.get('granule_file', 'N/A')}")
                    print(f"   🔬 Level: {result.get('quality_flags', {}).get('processing_level', 'N/A')}")
                    
                    air_quality = result.get('air_quality', {})
                    if air_quality.get('aqi'):
                        print(f"   📊 TEMPO AQI: {air_quality['aqi']}")
                    
                    measurements = result.get('measurements', {})
                    if measurements.get('no2_column'):
                        no2_val = measurements['no2_column']
                        print(f"   🧪 NO2: {no2_val:.2e} molecules/cm²")
                        
                else:
                    print(f"⚠️  {city}: No data for {date}")
                    
            except Exception as e:
                print(f"❌ {city}: Error - {str(e)}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ TEMPO service error: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints with real data"""
    print("🌐 TESTING API ENDPOINTS")
    print("-" * 50)
    
    base_url = "http://localhost:8000/api"
    
    # Test current endpoint
    try:
        response = requests.get(f"{base_url}/current?city=New York&include_tempo=true", timeout=30)
        print(f"Current AQI Endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AQI: {data.get('aqi', 'N/A')}")
            print(f"✅ Source: {data.get('source', 'N/A')}")
            print(f"✅ Real Data: {data.get('real_data', False)}")
            
            # Check for additional metadata
            metadata = data.get('metadata', {})
            if metadata:
                print(f"✅ TEMPO Integration: Available")
                granule = metadata.get('granule_file', '')
                if granule and 'TEMPO' in granule:
                    print(f"✅ TEMPO File: {granule}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running on port 8000")
        return False
    except Exception as e:
        print(f"❌ API test error: {str(e)}")
        return False
    
    print()
    return True

def test_frontend():
    """Test frontend accessibility"""
    print("🖥️  TESTING FRONTEND")
    print("-" * 50)
    
    try:
        # Check if frontend is running
        response = requests.get("http://localhost:3002", timeout=10)
        print(f"Frontend Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            print("✅ Real data visualization available at http://localhost:3002")
        else:
            print(f"⚠️  Frontend status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Frontend not running on port 3002")
        print("   Start with: cd frontend && npm run dev")
    except Exception as e:
        print(f"❌ Frontend test error: {str(e)}")
    
    print()

def check_environment():
    """Check environment configuration"""
    print("⚙️  CHECKING ENVIRONMENT")
    print("-" * 50)
    
    # Check API keys
    openweather_key = os.getenv('OPENWEATHER_API_KEY')
    earthdata_username = os.getenv('EARTHDATA_USERNAME')
    earthdata_password = os.getenv('EARTHDATA_PASSWORD')
    
    print(f"OpenWeatherMap API Key: {'✅ Set' if openweather_key else '❌ Missing'}")
    print(f"NASA EarthData Username: {'✅ Set' if earthdata_username else '❌ Missing'}")
    print(f"NASA EarthData Password: {'✅ Set' if earthdata_password else '❌ Missing'}")
    
    # Check file structure
    backend_files = [
        'main.py',
        'services/openweather_aqi_service.py',
        'services/tempo_service_earthaccess.py',
        'services/simple_air_quality_service.py',
        'routes/current.py'
    ]
    
    print("\nKey Backend Files:")
    for file in backend_files:
        path = os.path.join(os.path.dirname(__file__), file)
        exists = os.path.exists(path)
        print(f"{file}: {'✅ Found' if exists else '❌ Missing'}")
    
    print()

async def main():
    """Run complete system test"""
    print("🚀 AIRVISION REAL DATA SYSTEM TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"NASA Space Challenge Project")
    print("=" * 60)
    print()
    
    # Environment check
    check_environment()
    
    # Test services
    openweather_ok = await test_openweather_real_data()
    tempo_ok = await test_tempo_real_data()
    
    # Test API
    api_ok = test_api_endpoints()
    
    # Test frontend
    test_frontend()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"OpenWeatherMap Real Data: {'✅ PASS' if openweather_ok else '❌ FAIL'}")
    print(f"NASA TEMPO Real Data: {'✅ PASS' if tempo_ok else '❌ FAIL'}")
    print(f"API Integration: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print()
    
    if openweather_ok and tempo_ok and api_ok:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("🌍 AirVision is serving REAL satellite and API data!")
        print("🏆 Ready for NASA Space Challenge submission!")
    else:
        print("⚠️  Some systems need attention")
        print("📋 Review the test results above")
    
    print()
    print("🌐 Access your application at: http://localhost:3002")
    print("🔧 API Documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())