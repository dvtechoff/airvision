import os
from dotenv import load_dotenv
from openaq import OpenAQ
import concurrent.futures

# Load environment
load_dotenv()

print("=== OPENAQ API TEST WITH KEY ===")

api_key = os.getenv('OPENAQ_API_KEY')
print(f"API Key: {api_key[:20]}...")

try:
    # Initialize client
    client = OpenAQ(api_key=api_key)
    print("✅ Client initialized successfully")
    
    # Test locations near New York
    print("\nTesting locations near New York...")
    
    def get_locations():
        return client.locations.list(
            coordinates=[-74.0060, 40.7128],  # NYC coordinates
            radius=25000,
            limit=10
        )
    
    # Run in thread to avoid blocking
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_locations)
        locations = future.result(timeout=30)
    
    if locations and hasattr(locations, 'results'):
        print(f"✅ Found {len(locations.results)} locations")
        
        # Show details of first location
        if locations.results:
            loc = locations.results[0]
            print(f"\nLocation details:")
            print(f"  Name: {getattr(loc, 'name', 'Unknown')}")
            print(f"  ID: {getattr(loc, 'id', 'Unknown')}")
            print(f"  Country: {getattr(loc, 'country', 'Unknown')}")
            
            if hasattr(loc, 'sensors') and loc.sensors:
                print(f"  Sensors: {len(loc.sensors)}")
                
                # Test first sensor
                sensor = loc.sensors[0]
                print(f"\nFirst sensor:")
                print(f"  Sensor ID: {getattr(sensor, 'id', 'Unknown')}")
                print(f"  Parameter: {getattr(sensor, 'parameter', 'Unknown')}")
                
                # Get measurements
                print("\nGetting measurements...")
                
                def get_measurements():
                    return client.measurements.list(
                        sensors_id=sensor.id,
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
                        print(f"    Date: {getattr(measurement, 'date', 'Unknown')}")
                        print(f"    Unit: {getattr(measurement, 'unit', 'Unknown')}")
                else:
                    print("❌ No measurements found")
            else:
                print("  No sensors found")
    else:
        print("❌ No locations found")
        
    client.close()
    print("\n✅ Test completed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()