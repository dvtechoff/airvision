import os
from dotenv import load_dotenv
from openaq import OpenAQ
import concurrent.futures

# Load environment
load_dotenv()

print("=== TESTING PISECO LAKE OPENAQ SENSOR ===")

api_key = os.getenv('OPENAQ_API_KEY')

try:
    client = OpenAQ(api_key=api_key)
    print("✅ Client initialized")
    
    # Piseco Lake coordinates (Adirondacks, NY)
    # Piseco Lake is in Hamilton County, New York
    piseco_coords = [-74.5145, 43.4531]  # Approximate coordinates for Piseco Lake, NY
    
    print(f"\n1. Searching for locations near Piseco Lake...")
    print(f"   Coordinates: {piseco_coords}")
    
    def search_piseco():
        # Try different search strategies
        results = {}
        
        # Strategy 1: Coordinate search with maximum radius
        try:
            locations_coord = client.locations.list(
                coordinates=piseco_coords,
                radius=25000,  # 25km max radius
                limit=20
            )
            results['coordinate_search'] = locations_coord
        except Exception as e:
            results['coordinate_search'] = f"Error: {e}"
        
        # Strategy 2: Search by text "Piseco"
        try:
            locations_text = client.locations.list(
                limit=50
            )
            # Filter for Piseco in the results
            piseco_locations = []
            if locations_text and hasattr(locations_text, 'results'):
                for loc in locations_text.results:
                    name = getattr(loc, 'name', '').lower()
                    city = str(getattr(loc, 'city', '')).lower()
                    if 'piseco' in name or 'piseco' in city:
                        piseco_locations.append(loc)
            results['text_search'] = piseco_locations
        except Exception as e:
            results['text_search'] = f"Error: {e}"
            
        # Strategy 3: Look for New York state locations
        try:
            ny_locations = []
            all_locations = client.locations.list(limit=100)
            if all_locations and hasattr(all_locations, 'results'):
                for loc in all_locations.results:
                    country = getattr(loc, 'country', None)
                    name = getattr(loc, 'name', '').lower()
                    
                    # Check if it's US location and might be in NY
                    if country and hasattr(country, 'code') and country.code == 'US':
                        ny_locations.append(loc)
                    elif 'new york' in name or 'ny' in name or 'piseco' in name:
                        ny_locations.append(loc)
                        
            results['ny_locations'] = ny_locations
        except Exception as e:
            results['ny_locations'] = f"Error: {e}"
            
        return results
    
    # Execute search
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(search_piseco)
        search_results = future.result(timeout=60)
    
    # Process results
    print(f"\n2. SEARCH RESULTS:")
    
    # Check coordinate search
    coord_result = search_results.get('coordinate_search')
    if isinstance(coord_result, str):
        print(f"   Coordinate search: {coord_result}")
    elif coord_result and hasattr(coord_result, 'results'):
        print(f"   Coordinate search: Found {len(coord_result.results)} locations within 25km")
        for i, loc in enumerate(coord_result.results[:3]):
            name = getattr(loc, 'name', 'Unknown')
            country = getattr(loc, 'country', 'Unknown')
            coords = getattr(loc, 'coordinates', None)
            print(f"     {i+1}. {name} ({country})")
            if coords:
                print(f"        Coordinates: {coords.latitude}, {coords.longitude}")
    else:
        print(f"   Coordinate search: No results")
    
    # Check text search
    text_result = search_results.get('text_search')
    if isinstance(text_result, str):
        print(f"   Text search: {text_result}")
    elif text_result:
        print(f"   Text search: Found {len(text_result)} Piseco matches")
        for loc in text_result:
            name = getattr(loc, 'name', 'Unknown')
            print(f"     - {name}")
    else:
        print(f"   Text search: No Piseco matches found")
    
    # Check NY locations
    ny_result = search_results.get('ny_locations')
    if isinstance(ny_result, str):
        print(f"   NY locations: {ny_result}")
    elif ny_result:
        print(f"   NY/US locations: Found {len(ny_result)} US locations")
        
        # Look specifically for any that might be Piseco
        piseco_matches = []
        for loc in ny_result:
            name = getattr(loc, 'name', '').lower()
            if 'piseco' in name:
                piseco_matches.append(loc)
        
        if piseco_matches:
            print(f"   🎯 FOUND PISECO MATCHES: {len(piseco_matches)}")
            for loc in piseco_matches:
                print(f"     ✅ {getattr(loc, 'name', 'Unknown')}")
                print(f"        Country: {getattr(loc, 'country', 'Unknown')}")
                coords = getattr(loc, 'coordinates', None)
                if coords:
                    print(f"        Coordinates: {coords.latitude}, {coords.longitude}")
                
                # Get sensors info
                if hasattr(loc, 'sensors') and loc.sensors:
                    print(f"        Sensors: {len(loc.sensors)}")
                    for j, sensor in enumerate(loc.sensors[:3]):
                        param = getattr(sensor, 'parameter', 'Unknown')
                        sensor_id = getattr(sensor, 'id', 'Unknown')
                        print(f"          {j+1}. Parameter: {param}, ID: {sensor_id}")
                        
                        # Try to get measurements from this sensor
                        print(f"        Testing measurements from sensor {sensor_id}...")
                        
                        def get_piseco_measurements():
                            try:
                                return client.measurements.list(
                                    sensors_id=sensor_id,
                                    limit=5
                                )
                            except Exception as e:
                                return f"Error: {e}"
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(get_piseco_measurements)
                            measurements = future.result(timeout=30)
                        
                        if isinstance(measurements, str):
                            print(f"          Measurements: {measurements}")
                        elif measurements and hasattr(measurements, 'results'):
                            print(f"          ✅ Got {len(measurements.results)} measurements!")
                            if measurements.results:
                                latest = measurements.results[0]
                                value = getattr(latest, 'value', 'Unknown')
                                date = getattr(latest, 'date', 'Unknown')
                                unit = getattr(latest, 'unit', 'Unknown')
                                print(f"          Latest: {value} {unit} on {date}")
        else:
            print(f"     No exact Piseco matches in US locations")
            # Show a few US locations for reference
            for i, loc in enumerate(ny_result[:3]):
                name = getattr(loc, 'name', 'Unknown')
                country = getattr(loc, 'country', 'Unknown')
                print(f"       {i+1}. {name} ({country})")
    else:
        print(f"   NY locations: No results")
    
    client.close()
    print("\n✅ Search completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()