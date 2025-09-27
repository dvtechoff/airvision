import asyncio
import requests
import time

async def test_backend():
    """Test if the backend is working properly"""
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend connectivity...")
    time.sleep(2)  # Give server time to start
    result = asyncio.run(test_backend())
    
    if result:
        try:
            # Test root endpoint
            response = requests.get("http://localhost:8000/", timeout=5)
            print(f"✅ Root endpoint working: {response.json()}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")