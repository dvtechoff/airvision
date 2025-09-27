import openaq

# Test the actual SDK API
print("=== TESTING OPENAQ SDK API ===")

api = openaq.OpenAQ()

# Check what methods are available
print("Available methods on locations:", dir(api.locations))
print("Available methods on measurements:", dir(api.measurements))

# Try to get locations with correct API
try:
    print("\nTesting locations.get():")
    locations = api.locations.get(limit=5)
    print(f"Found {len(locations.results)} locations")
    for loc in locations.results[:3]:
        print(f"- {loc.displayName if hasattr(loc, 'displayName') else loc.name} (ID: {loc.id})")
        print(f"  Coordinates: {getattr(loc, 'coordinates', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")

# Test measurements
try:
    print("\nTesting measurements.get():")
    measurements = api.measurements.get(limit=10)
    print(f"Found {len(measurements.results)} measurements")
    for m in measurements.results[:3]:
        print(f"- {m.parameter}: {m.value} {m.unit} at {m.date}")
        if hasattr(m, 'location'):
            print(f"  Location: {m.location}")
except Exception as e:
    print(f"Error: {e}")