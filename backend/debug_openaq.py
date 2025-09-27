#!/usr/bin/env python3
"""
Debug test for OpenAQ API with detailed logging
"""
import sys
import asyncio
import logging
import os
sys.path.append('.')

from openaq import OpenAQ

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_openaq():
    print("=== DEBUG OPENAQ API ===\n")
    
    # Check API key
    api_key = os.getenv("OPENAQ_API_KEY")
    print(f"API Key configured: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key (first 10 chars): {api_key[:10]}...")
    print()
    
    # Test direct OpenAQ client
    client = None
    try:
        print("1. Testing OpenAQ client initialization...")
        client = OpenAQ(api_key=api_key)
        print("✅ Client initialized successfully")
        
        print("\n2. Testing locations.list() near New York...")
        # New York coordinates
        lat, lon = 40.7128, -74.0060
        
        def test_locations():
            try:
                locations = client.locations.list(
                    coordinates=[lon, lat], 
                    radius=25000, 
                    limit=10
                )
                return locations
            except Exception as e:
                logger.error(f"Error in locations.list: {e}")
                return None
        
        # Run in thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(test_locations)
            locations = future.result(timeout=30)
        
        if locations and hasattr(locations, 'results'):
            print(f"✅ Found {len(locations.results)} locations")
            
            # Show first location details
            if locations.results:
                loc = locations.results[0]
                print(f"\nFirst location:")
                print(f"  Name: {getattr(loc, 'name', 'Unknown')}")
                print(f"  ID: {getattr(loc, 'id', 'Unknown')}")
                print(f"  Sensors: {len(getattr(loc, 'sensors', []))}")
                
                # Try to get measurements from first sensor
                if hasattr(loc, 'sensors') and loc.sensors:
                    sensor = loc.sensors[0]
                    print(f"\nFirst sensor:")
                    print(f"  ID: {getattr(sensor, 'id', 'Unknown')}")
                    print(f"  Parameter: {getattr(sensor, 'parameter', 'Unknown')}")
                    
                    def test_measurements():
                        try:
                            measurements = client.measurements.list(
                                sensors_id=sensor.id,
                                limit=5
                            )
                            return measurements
                        except Exception as e:
                            logger.error(f"Error getting measurements: {e}")
                            return None
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(test_measurements)
                        measurements = future.result(timeout=30)
                    
                    if measurements and hasattr(measurements, 'results'):
                        print(f"  ✅ Got {len(measurements.results)} measurements")
                        if measurements.results:
                            first_measurement = measurements.results[0]
                            print(f"  Latest value: {getattr(first_measurement, 'value', 'Unknown')}")
                            print(f"  Date: {getattr(first_measurement, 'date', 'Unknown')}")
                    else:
                        print("  ❌ No measurements found")
        else:
            print("❌ No locations found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if client:
            client.close()
            print("\n✅ Client closed")

if __name__ == "__main__":
    asyncio.run(debug_openaq())