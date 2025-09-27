import os
from dotenv import load_dotenv
from openaq import OpenAQ
import concurrent.futures

# Load environment
load_dotenv()

print("=== OPENAQ US CITIES TEST ===")

api_key = os.getenv('OPENAQ_API_KEY')

try:
    client = OpenAQ(api_key=api_key)
    print("✅ Client initialized")
    
    # Test US cities with maximum allowed radius
    us_cities = [
        ("New York", [-74.0060, 40.7128]),
        ("Los Angeles", [-118.2437, 34.0522]),
        ("Chicago", [-87.6298, 41.8781]),
        ("Houston", [-95.3698, 29.7604]),
        ("Phoenix", [-112.0740, 33.4484]),
        ("Miami", [-80.1918, 25.7617]),
        ("Seattle", [-122.3321, 47.6062]),
        ("Denver", [-104.9903, 39.7392])
    ]
    
    found_locations = []
    
    for city_name, coords in us_cities:
        print(f"\nTesting {city_name}...")
        
        def get_city_locations():
            return client.locations.list(
                coordinates=coords,
                radius=25000,  # Maximum allowed radius
                limit=10
            )
        
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(get_city_locations)
                city_locations = future.result(timeout=30)
            
            if city_locations and hasattr(city_locations, 'results'):
                count = len(city_locations.results)
                print(f"  Found {count} locations")
                
                if count > 0:
                    found_locations.append((city_name, city_locations.results))
                    
                    for i, loc in enumerate(city_locations.results[:2]):
                        print(f"    Location {i+1}: {getattr(loc, 'name', 'Unknown')}")
                        print(f"      Country: {getattr(loc, 'country', 'Unknown')}")
                        if hasattr(loc, 'sensors') and loc.sensors:
                            sensors_info = []
                            for sensor in loc.sensors[:3]:  # Show first 3 sensors
                                param = getattr(sensor, 'parameter', 'Unknown')
                                if hasattr(param, 'name'):
                                    sensors_info.append(param.name)
                                else:
                                    sensors_info.append(str(param))
                            print(f"      Sensors: {', '.join(sensors_info)}")
            else:
                print(f"  No locations found")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Cities with monitoring locations: {len(found_locations)}")
    
    if found_locations:
        print("\nCities with real data available:")
        for city_name, locations in found_locations:
            print(f"  ✅ {city_name}: {len(locations)} locations")
            
        # Test getting actual measurements from the first available location
        print(f"\n=== TESTING MEASUREMENTS ===")
        city_name, locations = found_locations[0]
        location = locations[0]
        
        print(f"Getting measurements from {city_name} - {getattr(location, 'name', 'Unknown')}")
        
        if hasattr(location, 'sensors') and location.sensors:
            sensor = location.sensors[0]
            sensor_id = getattr(sensor, 'id', None)
            
            if sensor_id:
                def get_measurements():
                    return client.measurements.list(
                        sensors_id=sensor_id,
                        limit=5
                    )
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(get_measurements)
                    measurements = future.result(timeout=30)
                
                if measurements and hasattr(measurements, 'results'):
                    print(f"✅ Got {len(measurements.results)} measurements")
                    
                    if measurements.results:
                        measurement = measurements.results[0]
                        print(f"  Latest measurement:")
                        print(f"    Value: {getattr(measurement, 'value', 'Unknown')}")
                        print(f"    Unit: {getattr(measurement, 'unit', 'Unknown')}")
                        print(f"    Date: {getattr(measurement, 'date', 'Unknown')}")
                        print(f"    Parameter: {getattr(sensor, 'parameter', 'Unknown')}")
    else:
        print("❌ No US cities have monitoring locations in OpenAQ database")
    
    client.close()
    print("\n✅ Test completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()