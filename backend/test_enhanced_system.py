"""
Test script for the enhanced air quality system
Demonstrates database-backed location search and real-time data integration
"""

import asyncio
import json
from services.enhanced_air_quality_service import EnhancedAirQualityService

async def test_enhanced_system():
    """
    Test the complete enhanced air quality system
    """
    print("=== TESTING ENHANCED AIR QUALITY SYSTEM ===\n")
    
    service = EnhancedAirQualityService()
    
    # Test 1: Service Status
    print("1. Checking Service Status:")
    try:
        status = await service.get_service_status()
        print(f"   Overall Status: {status.get('overall_status', 'unknown')}")
        print(f"   Database Available: {status.get('database', {}).get('database_available', False)}")
        print(f"   Total Locations: {status.get('database', {}).get('total_locations', 'N/A')}")
        print(f"   OpenAQ API: {status.get('services', {}).get('openaq_api', 'unknown')}")
        print(f"   TEMPO API: {status.get('services', {}).get('tempo_api', 'unknown')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Location Search (works with or without database)
    print("2. Testing Location Search:")
    test_locations = ["Piseco Lake", "New York", "Los Angeles", "Chicago"]
    
    for location in test_locations:
        try:
            print(f"\n   Searching for: {location}")
            closest = await service.location_service.find_closest_location(location)
            
            if closest:
                print(f"   ✅ Found: {closest['name']}")
                print(f"      ID: {closest['openaq_id']}")
                print(f"      Coordinates: ({closest['latitude']:.4f}, {closest['longitude']:.4f})")
                print(f"      Distance: {closest['distance_km']:.2f} km")
                print(f"      Parameters: {closest['parameters']}")
            else:
                print(f"   ❌ No location found")
                
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: Comprehensive Air Quality Data
    print("3. Testing Comprehensive Air Quality Data:")
    test_cities = ["Piseco Lake", "New York"]
    
    for city in test_cities:
        try:
            print(f"\n   Getting comprehensive data for: {city}")
            result = await service.get_comprehensive_air_quality(city, include_tempo=True)
            
            print(f"   Location Found: {result['location_found']}")
            
            if result['location_found']:
                location_info = result['location_info']
                print(f"   Monitoring Station: {location_info['name']}")
                print(f"   Distance: {location_info['distance_km']:.2f} km")
                
                # Show data sources
                print(f"   Data Sources: {', '.join(result['data_sources'])}")
                
                # Show combined AQI
                combined_aqi = result.get('combined_aqi')
                if combined_aqi:
                    print(f"   AQI: {combined_aqi['aqi']} ({combined_aqi['category']})")
                    print(f"   Primary Source: {combined_aqi['primary_source']}")
                    print(f"   Confidence: {combined_aqi['confidence']}")
                    
                    if combined_aqi.get('data_freshness'):
                        print(f"   Data Freshness: {combined_aqi['data_freshness']}")
                    
                    if combined_aqi.get('pollutants'):
                        print(f"   Key Pollutants: {list(combined_aqi['pollutants'].keys())}")
            
            # Show errors if any
            if result['errors']:
                print(f"   Warnings: {'; '.join(result['errors'])}")
                
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 4: Compare with old service (fallback behavior)
    print("4. Testing Fallback Behavior:")
    try:
        print("   Testing location with no nearby stations...")
        result = await service.get_comprehensive_air_quality("Middle of Pacific Ocean")
        
        if result.get('fallback_data'):
            fallback = result['fallback_data']
            print(f"   ✅ Fallback activated")
            print(f"   Estimated AQI: {fallback['aqi']} ({fallback['category']})")
            print(f"   Note: {fallback['note']}")
        else:
            print(f"   Location search still found something: {result.get('location_found')}")
            
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 5: Database Statistics
    print("5. Database Statistics:")
    try:
        stats = await service.location_service.get_database_stats()
        
        if stats.get('database_available'):
            print(f"   Total Locations: {stats.get('total_locations', 'N/A')}")
            print(f"   Active Locations: {stats.get('active_locations', 'N/A')}")
            print(f"   Countries: {stats.get('countries', 'N/A')}")
            print(f"   Last Update: {stats.get('latest_update', 'N/A')}")
        else:
            print(f"   Database not available - using fallback cache")
            print(f"   Cache size: {stats.get('cache_size', 0)} locations")
            
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    print("\n" + "="*60 + "\n")
    print("✅ Enhanced system test completed!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_system())