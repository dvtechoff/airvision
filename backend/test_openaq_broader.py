import os
from dotenv import load_dotenv
from openaq import OpenAQ
import concurrent.futures

# Load environment
load_dotenv()

print("=== OPENAQ API BROADER TEST ===")

api_key = os.getenv('OPENAQ_API_KEY')

try:
    client = OpenAQ(api_key=api_key)
    print("✅ Client initialized")
    
    # Test 1: List some locations without coordinates (get any locations)
    print("\n1. Getting any available locations...")
    
    def get_any_locations():
        return client.locations.list(limit=10)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_any_locations)
        locations = future.result(timeout=30)
    
    if locations and hasattr(locations, 'results'):
        print(f"✅ Found {len(locations.results)} locations worldwide")
        
        if locations.results:
            for i, loc in enumerate(locations.results[:3]):
                print(f"\nLocation {i+1}:")
                print(f"  Name: {getattr(loc, 'name', 'Unknown')}")
                print(f"  Country: {getattr(loc, 'country', 'Unknown')}")
                print(f"  City: {getattr(loc, 'city', 'Unknown')}")
                print(f"  Coordinates: {getattr(loc, 'coordinates', 'Unknown')}")
                if hasattr(loc, 'sensors'):
                    print(f"  Sensors: {len(loc.sensors) if loc.sensors else 0}")
    
    # Test 2: Try different US cities
    us_cities = [
        ("Los Angeles", [-118.2437, 34.0522]),
        ("Chicago", [-87.6298, 41.8781]),
        ("Houston", [-95.3698, 29.7604]),
        ("Phoenix", [-112.0740, 33.4484])
    ]
    
    print(f"\n2. Testing US cities with larger radius...")
    
    for city_name, coords in us_cities:
        print(f"\nTesting {city_name}...")
        
        def get_city_locations():
            return client.locations.list(
                coordinates=coords,
                radius=50000,  # 50km radius
                limit=5
            )
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(get_city_locations)
            city_locations = future.result(timeout=30)
        
        if city_locations and hasattr(city_locations, 'results'):
            count = len(city_locations.results)
            print(f"  Found {count} locations")
            
            if count > 0 and city_locations.results:
                loc = city_locations.results[0]
                print(f"  First location: {getattr(loc, 'name', 'Unknown')}")
                if hasattr(loc, 'sensors') and loc.sensors:
                    sensor = loc.sensors[0]
                    print(f"  First sensor parameter: {getattr(sensor, 'parameter', 'Unknown')}")
        else:
            print(f"  No locations found")
    
    client.close()
    print("\n✅ Test completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()