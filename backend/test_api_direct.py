"""
Test the API endpoint directly with OpenWeatherMap integration
"""

import asyncio
from routes.current import get_current_aqi

async def test_api_endpoint():
    """Test the current AQI endpoint"""
    print("=== TESTING API ENDPOINT WITH OPENWEATHERMAP ===\n")
    
    cities = ["New York", "Los Angeles", "Chicago", "Piseco Lake"]
    
    for city in cities:
        print(f"Testing API for: {city}")
        try:
            result = await get_current_aqi(city, include_tempo=True)
            
            print(f"  ✅ AQI: {result.aqi} ({result.category})")
            print(f"  📍 Source: {result.source}")
            print(f"  🌬️  Pollutants:")
            print(f"      PM2.5: {result.pollutants.pm25}")
            print(f"      PM10: {result.pollutants.pm10}")
            print(f"      NO2: {result.pollutants.no2}")
            print(f"      O3: {result.pollutants.o3}")
            print(f"  ⏰ Timestamp: {result.timestamp}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_api_endpoint())