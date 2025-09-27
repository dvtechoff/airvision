import os
from dotenv import load_dotenv
from openaq import OpenAQ
import concurrent.futures

# Load environment
load_dotenv()

print("=== COMPREHENSIVE US LOCATIONS SEARCH ===")

api_key = os.getenv('OPENAQ_API_KEY')

try:
    client = OpenAQ(api_key=api_key)
    print("✅ Client initialized")
    
    print(f"\n1. Getting ALL available locations to find US stations...")
    
    def get_all_locations():
        all_locations = []
        page = 1
        
        try:
            while len(all_locations) < 1000:  # Limit to prevent infinite loop
                print(f"   Fetching page {page}...")
                
                locations = client.locations.list(
                    limit=100,  # Max per page
                    page=page
                )
                
                if not locations or not hasattr(locations, 'results') or not locations.results:
                    break
                    
                all_locations.extend(locations.results)
                
                if len(locations.results) < 100:  # Last page
                    break
                    
                page += 1
                
                if page > 10:  # Safety limit
                    break
                    
        except Exception as e:
            print(f"   Error on page {page}: {e}")
            
        return all_locations
    
    # Get all locations
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_all_locations)
        all_locations = future.result(timeout=120)
    
    print(f"\n2. ANALYSIS OF {len(all_locations)} TOTAL LOCATIONS:")
    
    # Group by country
    by_country = {}
    us_locations = []
    
    for loc in all_locations:
        country = getattr(loc, 'country', None)
        if country and hasattr(country, 'name'):
            country_name = country.name
            if country_name not in by_country:
                by_country[country_name] = []
            by_country[country_name].append(loc)
            
            if country.code == 'US':
                us_locations.append(loc)
    
    print(f"\n   Countries with monitoring locations:")
    for country, locations in sorted(by_country.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"     {country}: {len(locations)} locations")
    
    print(f"\n3. US LOCATIONS DETAILED ANALYSIS ({len(us_locations)} total):")
    
    if us_locations:
        piseco_candidates = []
        
        for i, loc in enumerate(us_locations):
            name = getattr(loc, 'name', 'Unknown')
            coordinates = getattr(loc, 'coordinates', None)
            sensors_count = len(getattr(loc, 'sensors', []))
            
            print(f"   {i+1}. {name}")
            if coordinates:
                print(f"      Coordinates: {coordinates.latitude}, {coordinates.longitude}")
            print(f"      Sensors: {sensors_count}")
            
            # Check if this could be Piseco Lake
            name_lower = name.lower()
            if ('piseco' in name_lower or 
                'lake' in name_lower or 
                'adirondack' in name_lower or
                'hamilton' in name_lower or
                'ny' in name_lower or
                'new york' in name_lower):
                piseco_candidates.append(loc)
                print(f"      🎯 POTENTIAL MATCH!")
            
            # Show sensor details for all US locations
            if hasattr(loc, 'sensors') and loc.sensors:
                for j, sensor in enumerate(loc.sensors[:3]):
                    sensor_id = getattr(sensor, 'id', 'Unknown')
                    param = getattr(sensor, 'parameter', 'Unknown')
                    if hasattr(param, 'name'):
                        param_name = param.name
                    else:
                        param_name = str(param)
                    print(f"        Sensor {j+1}: {param_name} (ID: {sensor_id})")
        
        if piseco_candidates:
            print(f"\n4. POTENTIAL PISECO MATCHES ({len(piseco_candidates)}):")
            
            for i, loc in enumerate(piseco_candidates):
                name = getattr(loc, 'name', 'Unknown')
                print(f"\n   Match {i+1}: {name}")
                
                # Test this location's sensors
                if hasattr(loc, 'sensors') and loc.sensors:
                    sensor = loc.sensors[0]
                    sensor_id = getattr(sensor, 'id', None)
                    
                    if sensor_id:
                        print(f"   Testing measurements from sensor {sensor_id}...")
                        
                        def get_test_measurements():
                            try:
                                return client.measurements.list(
                                    sensors_id=sensor_id,
                                    limit=3
                                )
                            except Exception as e:
                                return f"Error: {e}"
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(get_test_measurements)
                            measurements = future.result(timeout=30)
                        
                        if isinstance(measurements, str):
                            print(f"   ❌ {measurements}")
                        elif measurements and hasattr(measurements, 'results'):
                            print(f"   ✅ SUCCESS! Got {len(measurements.results)} measurements")
                            
                            if measurements.results:
                                latest = measurements.results[0]
                                value = getattr(latest, 'value', 'Unknown')
                                unit = getattr(latest, 'unit', 'Unknown')
                                date = getattr(latest, 'date', 'Unknown')
                                param = getattr(sensor, 'parameter', 'Unknown')
                                
                                print(f"   📊 Latest Data:")
                                print(f"      Parameter: {param}")
                                print(f"      Value: {value} {unit}")
                                print(f"      Date: {date}")
                                
                                # This is real data! Update our service to use this location
                                print(f"   🎉 FOUND REAL US DATA SOURCE!")
        else:
            print(f"\n4. No obvious Piseco matches, but found {len(us_locations)} US locations")
            
            # Test the first US location anyway
            if us_locations:
                test_loc = us_locations[0]
                name = getattr(test_loc, 'name', 'Unknown')
                print(f"\n   Testing first US location: {name}")
                
                if hasattr(test_loc, 'sensors') and test_loc.sensors:
                    sensor = test_loc.sensors[0]
                    sensor_id = getattr(sensor, 'id', None)
                    
                    if sensor_id:
                        def get_test_measurements():
                            try:
                                return client.measurements.list(
                                    sensors_id=sensor_id,
                                    limit=3
                                )
                            except Exception as e:
                                return f"Error: {e}"
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(get_test_measurements)
                            measurements = future.result(timeout=30)
                        
                        if not isinstance(measurements, str) and measurements and hasattr(measurements, 'results'):
                            print(f"   ✅ This US location has real data too!")
    else:
        print("   No US locations found in OpenAQ database")
    
    client.close()
    print("\n✅ Comprehensive search completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()