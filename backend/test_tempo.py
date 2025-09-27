#!/usr/bin/env python3

import asyncio
import sys
import traceback

async def test_tempo_service():
    try:
        from services.tempo_service import TEMPOService
        
        service = TEMPOService()
        print("TEMPOService imported successfully")
        
        # Test getting data for New York
        data = await service.get_tempo_data("New York")
        print(f"Data for New York: {data}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return False

async def test_current_route():
    try:
        from routes.current import get_current_aqi
        print("Current route imported successfully")
        
        # Test the route function directly
        result = await get_current_aqi("New York", True)
        print(f"Route result: {result}")
        
        return True
        
    except Exception as e:
        print(f"Error in route: {e}")
        traceback.print_exc()
        return False

async def main():
    print("Testing TEMPO service...")
    await test_tempo_service()
    
    print("\nTesting current route...")
    await test_current_route()

if __name__ == "__main__":
    asyncio.run(main())