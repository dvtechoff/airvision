import asyncio
import sys
from services.openaq_service import OpenAQService

async def debug_service():
    """Debug the service step by step"""
    print("=== DEBUGGING OPENAQ SERVICE ===\n")
    
    service = OpenAQService()
    
    # Test direct API call
    print("1. Testing direct SDK call:")
    try:
        import openaq
        api = openaq.OpenAQ()
        
        # Test locations search
        print("   Testing locations search...")
        locations = api.locations.get(
            coordinates=(43.4, -74.5),  # Piseco Lake area
            radius=50000,
            limit=5
        )
        print(f"   Found {len(locations.results)} locations")
        for loc in locations.results[:3]:
            print(f"   - {loc.displayName} (ID: {loc.id})")
        
        if locations.results:
            location_id = locations.results[0].id
            print(f"\n   Testing measurements for location {location_id}:")
            measurements = api.measurements.get(
                locations_id=location_id,
                limit=10,
                date_from='2024-01-01'
            )
            print(f"   Found {len(measurements.results)} measurements")
            for m in measurements.results[:3]:
                print(f"   - {m.parameter}: {m.value} {m.unit} at {m.date}")
        
    except Exception as e:
        print(f"   SDK Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test service call
    print("\n2. Testing service call:")
    try:
        result = await service.get_aqi_data("Piseco Lake")
        print(f"   Service result: {result}")
    except Exception as e:
        print(f"   Service Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_service())