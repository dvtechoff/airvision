import asyncio
from services.openaq_service_http import OpenAQService

async def test_http_service():
    """Test the HTTP-based OpenAQ service"""
    print("=== TESTING HTTP-BASED OPENAQ SERVICE ===\n")
    
    service = OpenAQService()
    
    # Test Piseco Lake
    print("1. Testing Piseco Lake:")
    result = await service.get_aqi_data("Piseco Lake")
    print(f"   Source: {result['source']}")
    print(f"   AQI: {result['aqi']} ({result['category']})")
    if 'parameters_found' in result:
        print(f"   Parameters found: {result['parameters_found']}")
        print(f"   Measurements processed: {result['measurements_processed']}")
    print(f"   Pollutants: {result['pollutants']}")
    
    # Test New York (mapped to Piseco Lake)
    print("\n2. Testing New York:")
    result2 = await service.get_aqi_data("New York")
    print(f"   Source: {result2['source']}")
    print(f"   AQI: {result2['aqi']} ({result2['category']})")
    if 'parameters_found' in result2:
        print(f"   Parameters found: {result2['parameters_found']}")
        print(f"   Measurements processed: {result2['measurements_processed']}")
    print(f"   Pollutants: {result2['pollutants']}")
    
    # Check if we got real data
    if result['source'] == "OpenAQ Real Data":
        print("\n🎉 SUCCESS: Getting real OpenAQ data!")
    else:
        print(f"\n⚠️  Still using mock data: {result['source']}")

if __name__ == "__main__":
    asyncio.run(test_http_service())