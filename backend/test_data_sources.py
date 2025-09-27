#!/usr/bin/env python3
"""
Test script to check current AQI data sources
"""
import sys
import os
import asyncio
sys.path.append('.')

from services.openaq_service import OpenAQService
from services.tempo_service import TEMPOService

async def check_data_sources():
    print("=== CURRENT AQI DATA SOURCES ===\n")
    
    # Check environment configuration
    print("📋 Environment Configuration:")
    print(f"   EARTHDATA_USERNAME: {'✅ SET' if os.getenv('EARTHDATA_USERNAME') else '❌ NOT SET'}")
    print(f"   EARTHDATA_PASSWORD: {'✅ SET' if os.getenv('EARTHDATA_PASSWORD') else '❌ NOT SET'}")
    print(f"   OPENAQ_API_KEY: {'✅ SET' if os.getenv('OPENAQ_API_KEY') else '❌ NOT SET'}")
    print()
    
    # Test OpenAQ Service
    print("🌍 Testing OpenAQ Service (Ground Stations):")
    try:
        async with OpenAQService() as openaq_service:
            result = await openaq_service.get_aqi_data('New York')
            source = result.get('source', 'Unknown')
            aqi = result.get('aqi', 'Unknown')
            
            print(f"   Source: {source}")
            print(f"   AQI: {aqi}")
            
            if 'Real Data' in source:
                print("   Status: ✅ USING REAL OPENAQ DATA")
            else:
                print("   Status: ❌ USING MOCK DATA (API unavailable)")
    except Exception as e:
        print(f"   Status: ❌ ERROR - {e}")
    
    print()
    
    # Test TEMPO Service  
    print("🛰️ Testing TEMPO Service (NASA Satellite):")
    try:
        async with TEMPOService() as tempo_service:
            result = await tempo_service.get_tempo_data('New York')
            source = result.get('source', 'Unknown')
            
            print(f"   Source: {source}")
            
            if 'Real Data' in source:
                print("   Status: ✅ USING REAL TEMPO DATA")
            else:
                print("   Status: ❌ USING MOCK DATA (credentials needed)")
                
            # Check if has processed air quality data
            if 'air_quality' in result:
                aqi = result['air_quality'].get('aqi', 'Unknown')
                print(f"   Processed AQI: {aqi}")
            
    except Exception as e:
        print(f"   Status: ❌ ERROR - {e}")
    
    print()
    print("=== SUMMARY ===")
    print("Current application is fetching AQI from:")
    print("1. 🔴 MOCK OpenAQ data (real API returning HTTP 410)")
    print("2. 🔴 MOCK TEMPO data (NASA credentials not configured)")
    print("\nTo get real data:")
    print("- Set NASA EarthData credentials in .env file")  
    print("- Update OpenAQ integration to use v3 API")

if __name__ == "__main__":
    asyncio.run(check_data_sources())