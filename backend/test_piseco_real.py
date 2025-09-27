import os
from dotenv import load_dotenv
import asyncio
import sys
sys.path.append('.')

from services.openaq_service import OpenAQService

async def test_piseco_real_data():
    print("=== TESTING PISECO LAKE REAL DATA ===\n")
    
    try:
        async with OpenAQService() as service:
            # Test with "Piseco Lake" directly
            print("1. Testing with 'Piseco Lake':")
            result1 = await service.get_aqi_data('Piseco Lake')
            print(f"   Source: {result1.get('source')}")
            print(f"   AQI: {result1.get('aqi')}")
            print(f"   Pollutants: {result1.get('pollutants')}")
            
            # Test with "New York" (should now find Piseco Lake area)
            print("\n2. Testing with 'New York' (mapped to Piseco Lake area):")
            result2 = await service.get_aqi_data('New York')
            print(f"   Source: {result2.get('source')}")
            print(f"   AQI: {result2.get('aqi')}")
            print(f"   Pollutants: {result2.get('pollutants')}")
            
            # Check if we got real data
            for i, (city, result) in enumerate([("Piseco Lake", result1), ("New York", result2)], 1):
                if 'Real Data' in result.get('source', ''):
                    print(f"\n✅ SUCCESS for {city}! Got real OpenAQ data:")
                    print(f"   🎯 Source: {result['source']}")
                    if 'location_info' in result:
                        loc_info = result['location_info']
                        print(f"   📍 Location: {loc_info.get('name', 'Unknown')}")
                        print(f"   📊 Sensors: {loc_info.get('sensors_count', 0)}")
                        print(f"   🌍 Coordinates: {loc_info.get('coordinates', {})}")
                else:
                    print(f"\n⚠️ {city} still using mock data: {result['source']}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_piseco_real_data())