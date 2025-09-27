#!/usr/bin/env python3
"""
Direct test of the OpenWeatherMap service to verify real data
"""

import asyncio
import sys
import logging
from services.openweather_aqi_service import OpenWeatherAQService
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

load_dotenv()

async def test_new_york():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    print(f'🔑 API Key Status: {"Valid" if api_key and len(api_key) > 10 else "Missing"}')
    
    async with OpenWeatherAQService(api_key) as service:
        data = await service.get_aqi_data('New York')
        
        print('\n🗽 NEW YORK AIR QUALITY REPORT')
        print('=' * 40)
        print(f'🌪️  AQI: {data.get("aqi", "N/A")}')
        print(f'📊 Category: {data.get("category", "N/A")}')
        print(f'🛰️  Source: {data.get("source", "N/A")}')
        
        pollutants = data.get('pollutants', {})
        if pollutants:
            print('\n🏭 POLLUTANT LEVELS:')
            print(f'   PM2.5: {pollutants.get("pm25", 0):.1f} μg/m³')
            print(f'   PM10:  {pollutants.get("pm10", 0):.1f} μg/m³') 
            print(f'   NO2:   {pollutants.get("no2", 0):.1f} μg/m³')
            print(f'   O3:    {pollutants.get("o3", 0):.1f} μg/m³')
        
        coords = data.get('coordinates', {})
        if coords:
            print(f'\n📍 Location: {coords.get("latitude", "N/A")}, {coords.get("longitude", "N/A")}')
        
        is_real = 'Real-time' in data.get('source', '')
        print(f'\n✅ Status: {"REAL OpenWeatherMap data!" if is_real else "Mock data (API fallback)"}')
        
        if is_real:
            print('\n🎉 SUCCESS: Your AirVision app is now using REAL air quality data!')
            print('🌍 Users will see actual current conditions for any city they search!')
        
        return data

if __name__ == "__main__":
    result = asyncio.run(test_new_york())