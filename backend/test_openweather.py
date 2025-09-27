"""
Quick test for OpenWeatherMap Air Pollution API service
"""

import asyncio
from services.openweather_aqi_service import OpenWeatherAQService

async def test_openweather_service():
    """Test OpenWeatherMap service"""
    print("=== TESTING OPENWEATHERMAP AIR POLLUTION API ===\n")
    
    # Initialize with a placeholder API key
    service = OpenWeatherAQService("83e3bee9f9fbb3dcaa85a810d4dc56e3")  # Replace with real key
    
    cities = ["New York", "Los Angeles", "Chicago", "Piseco Lake"]
    
    for city in cities:
        print(f"Testing: {city}")
        try:
            result = await service.get_aqi_data(city)
            
            print(f"  🌟 AQI: {result.get('aqi', 'N/A')} ({result.get('category', 'Unknown')})")
            print(f"  📍 Source: {result.get('source', 'Unknown')}")
            
            if result.get("coordinates"):
                coords = result["coordinates"]
                print(f"  📍 Coordinates: ({coords['lat']:.4f}, {coords['lon']:.4f})")
            
            if result.get("pollutants"):
                pollutants = result["pollutants"]
                print(f"  🌬️  Pollutants:")
                for pollutant, value in pollutants.items():
                    print(f"      {pollutant.upper()}: {value}")
            
            print(f"  ⏰ Note: {result.get('note', 'No note')}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_openweather_service())