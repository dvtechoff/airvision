"""
Test the working backend API endpoints
"""

import asyncio
from services.simple_air_quality_service import SimpleAirQualityService

async def test_working_backend():
    """Test the simplified service"""
    print("=== TESTING WORKING BACKEND SERVICES ===\n")
    
    service = SimpleAirQualityService()
    
    # Test cities
    cities = ["Piseco Lake", "New York", "Los Angeles", "Chicago"]
    
    for city in cities:
        print(f"Testing: {city}")
        try:
            result = await service.get_comprehensive_air_quality(city, include_tempo=True)
            
            combined_aqi = result.get("combined_aqi", {})
            print(f"  ✅ AQI: {combined_aqi.get('aqi', 'N/A')} ({combined_aqi.get('category', 'Unknown')})")
            print(f"  📊 Source: {combined_aqi.get('primary_source', 'Unknown')}")
            print(f"  🔌 Data Sources: {', '.join(result.get('data_sources', ['None']))}")
            print(f"  🎯 Confidence: {combined_aqi.get('confidence', 'unknown')}")
            
            if combined_aqi.get("pollutants"):
                pollutants = combined_aqi["pollutants"]
                print(f"  🌬️  Pollutants: PM2.5={pollutants.get('pm25', 'N/A')}, PM10={pollutants.get('pm10', 'N/A')}, NO2={pollutants.get('no2', 'N/A')}, O3={pollutants.get('o3', 'N/A')}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_working_backend())