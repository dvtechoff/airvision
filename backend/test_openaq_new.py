#!/usr/bin/env python3
"""
Test the updated OpenAQ service with the new Python SDK
"""
import sys
import asyncio
sys.path.append('.')

from services.openaq_service import OpenAQService

async def test_new_openaq():
    print("=== TESTING NEW OPENAQ PYTHON SDK ===\n")
    
    try:
        async with OpenAQService() as service:
            print("Testing OpenAQ service with New York...")
            result = await service.get_aqi_data('New York')
            
            print(f"City: {result.get('city')}")
            print(f"Source: {result.get('source')}")
            print(f"AQI: {result.get('aqi')}")
            print(f"Category: {result.get('category')}")
            print(f"Pollutants: {result.get('pollutants')}")
            
            if 'Real Data' in result.get('source', ''):
                print("✅ SUCCESS: Got real data from OpenAQ!")
                if 'location_info' in result:
                    loc_info = result['location_info']
                    print(f"Location: {loc_info.get('name')}")
                    print(f"Sensors: {loc_info.get('sensors_count')}")
            else:
                print("⚠️ Using mock data - check API key configuration")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_openaq())