import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_complete_integration():
    """Test complete integration with NASA TEMPO data."""
    
    print("🚀 Testing NASA TEMPO Data Integration")
    print("=" * 50)
    
    # Test 1: Environment variables
    print("1. Checking environment variables...")
    username = os.getenv('EARTHDATA_USERNAME')
    password = os.getenv('EARTHDATA_PASSWORD')
    
    if username and password:
        print(f"✅ EarthData credentials found for: {username}")
    else:
        print("❌ EarthData credentials not found")
        return
    
    # Test 2: Import and initialize service
    print("\n2. Initializing TEMPO service...")
    try:
        from services.tempo_service import TEMPOService
        tempo_service = TEMPOService()
        print("✅ TEMPO service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize TEMPO service: {e}")
        return
    
    # Test 3: Test data retrieval for North American cities
    test_cities = ['New York', 'Los Angeles', 'Toronto', 'Chicago']
    
    print(f"\n3. Testing data retrieval for {len(test_cities)} cities...")
    
    for i, city in enumerate(test_cities, 1):
        print(f"\n--- Testing {i}/{len(test_cities)}: {city} ---")
        
        try:
            start_time = datetime.now()
            data = await tempo_service.get_tempo_data(city)
            end_time = datetime.now()
            
            if data:
                print(f"✅ {city}: Data retrieved successfully")
                print(f"   - Source: {data.get('source', 'Unknown')}")
                print(f"   - AQI: {data.get('air_quality', {}).get('aqi', 'N/A')}")
                print(f"   - Category: {data.get('air_quality', {}).get('category', 'N/A')}")
                print(f"   - NO2: {data.get('surface_estimates', {}).get('no2', 'N/A'):.1f} µg/m³")
                print(f"   - PM2.5: {data.get('surface_estimates', {}).get('pm25', 'N/A'):.1f} µg/m³")
                print(f"   - Response time: {(end_time - start_time).total_seconds():.2f}s")
                
                # Check if using real NASA data
                if 'earthaccess' in data.get('source', '').lower() or 'nasa tempo satellite' in data.get('source', '').lower():
                    print("   🛰️  Using real NASA TEMPO data!")
                else:
                    print("   📊  Using enhanced mock data")
                    
                # Check cache
                if city.lower() in tempo_service.tempo_data_cache:
                    print("   💾  Data cached for future requests")
                    
            else:
                print(f"❌ {city}: No data returned")
                
        except Exception as e:
            print(f"❌ {city}: Error - {e}")
    
    # Test 4: Test caching performance
    print(f"\n4. Testing cache performance...")
    try:
        print("   First request (should be slow)...")
        start_time = datetime.now()
        data1 = await tempo_service.get_tempo_data('New York')
        time1 = (datetime.now() - start_time).total_seconds()
        
        print("   Second request (should use cache)...")
        start_time = datetime.now()
        data2 = await tempo_service.get_tempo_data('New York')
        time2 = (datetime.now() - start_time).total_seconds()
        
        print(f"   First request: {time1:.2f}s")
        print(f"   Cached request: {time2:.2f}s")
        
        if time2 < time1:
            print("   ✅ Cache is working - second request was faster!")
        else:
            print("   ⚠️  Cache might not be working as expected")
            
    except Exception as e:
        print(f"   ❌ Cache test failed: {e}")
    
    # Test 5: Test API endpoint
    print(f"\n5. Testing complete API endpoint...")
    try:
        from routes.current import get_current_aqi
        
        start_time = datetime.now()
        response = await get_current_aqi('New York', include_tempo=True)
        end_time = datetime.now()
        
        print(f"✅ API endpoint working")
        print(f"   - City: {response.city}")
        print(f"   - AQI: {response.aqi}")
        print(f"   - Category: {response.category}")
        print(f"   - Source: {response.source}")
        print(f"   - Response time: {(end_time - start_time).total_seconds():.2f}s")
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
    
    print(f"\n" + "=" * 50)
    print("🎯 Integration test completed!")
    print("\n💡 Next steps:")
    print("   1. Start the backend server: uvicorn main:app --reload")
    print("   2. Test the API: curl 'http://localhost:8000/api/current?city=New York'")
    print("   3. Start the frontend: cd frontend && npm run dev")
    print("   4. Visit http://localhost:3000 to see the full application")

if __name__ == "__main__":
    asyncio.run(test_complete_integration())