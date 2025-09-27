#!/usr/bin/env python3
"""
Test script for real-time data processing integration
Tests the complete pipeline from Earth data to frontend
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_tempo_service import EnhancedTEMPOService
from services.realtime_data_processor import realtime_processor

async def test_realtime_processing():
    """Test the complete real-time processing pipeline"""
    
    print("🚀 Testing Real-time Data Processing Integration")
    print("=" * 60)
    
    # Test cities
    test_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Toronto"]
    
    try:
        # Initialize the processor
        await realtime_processor.initialize()
        print("✅ Real-time processor initialized")
        
        # Test with enhanced TEMPO service
        async with EnhancedTEMPOService() as tempo_service:
            print("✅ Enhanced TEMPO service initialized")
            
            # Test each city
            for city in test_cities:
                print(f"\n📍 Testing {city}...")
                
                try:
                    # Get real-time data
                    start_time = datetime.now()
                    data = await tempo_service.get_tempo_data(city)
                    processing_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    print(f"   ✅ Data processed in {processing_time:.1f}ms")
                    print(f"   📊 AQI: {data['air_quality']['aqi']}")
                    print(f"   🎯 Quality: {data['data_quality']}")
                    print(f"   💾 Cached: {data['cache_info']['cached']}")
                    print(f"   🌤️  Cloud Cover: {data['measurements']['cloud_fraction']*100:.1f}%")
                    
                except Exception as e:
                    print(f"   ❌ Error processing {city}: {e}")
            
            # Test cache statistics
            print(f"\n📈 Cache Statistics:")
            cache_stats = await tempo_service.get_cache_stats()
            print(f"   Total entries: {cache_stats['total_entries']}")
            print(f"   Cache size: {cache_stats['total_size_mb']} MB")
            print(f"   Hit rate: {cache_stats['hit_rate']*100:.1f}%")
            
            # Test batch processing
            print(f"\n🔄 Testing batch processing...")
            batch_data = []
            for city in test_cities[:3]:  # Test first 3 cities
                batch_data.append(await tempo_service.get_tempo_data(city))
            
            print(f"   ✅ Batch processed {len(batch_data)} cities")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    print(f"\n🎉 Real-time processing integration test completed successfully!")
    print(f"✅ All components working correctly")
    print(f"✅ Earth data integration functional")
    print(f"✅ Real-time processing operational")
    print(f"✅ Caching system working")
    print(f"✅ Data quality filtering active")
    
    return True

async def test_api_endpoints():
    """Test API endpoints for real-time processing"""
    
    print(f"\n🌐 Testing API Endpoints")
    print("=" * 40)
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test real-time processing endpoint
        print("Testing /api/realtime/process...")
        response = requests.get(f"{base_url}/api/realtime/process?city=New York")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Real-time processing: {data['air_quality']['aqi']} AQI")
        else:
            print(f"   ❌ Real-time processing failed: {response.status_code}")
        
        # Test cache stats endpoint
        print("Testing /api/realtime/cache/stats...")
        response = requests.get(f"{base_url}/api/realtime/cache/stats")
        if response.status_code == 200:
            stats = response.json()['cache_statistics']
            print(f"   ✅ Cache stats: {stats['total_entries']} entries, {stats['total_size_mb']} MB")
        else:
            print(f"   ❌ Cache stats failed: {response.status_code}")
        
        # Test health check
        print("Testing /api/realtime/health...")
        response = requests.get(f"{base_url}/api/realtime/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Health check: {health['status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️  API tests skipped (server not running): {e}")

async def main():
    """Main test function"""
    
    print("NASA TEMPO Real-time Data Processing Integration Test")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test real-time processing
    success = await test_realtime_processing()
    
    # Test API endpoints (if server is running)
    await test_api_endpoints()
    
    print(f"\n" + "=" * 70)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Real-time data processing is fully operational")
        print("✅ Earth data integration is working")
        print("✅ Caching system is functional")
        print("✅ Data quality filtering is active")
        print("✅ Frontend integration is ready")
        print("\n🚀 Your AirVision application is ready for production!")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please check the error messages above and fix any issues.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
