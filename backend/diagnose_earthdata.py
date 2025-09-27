#!/usr/bin/env python3
"""
NASA EarthData Credential Diagnostic Tool
"""

import os
import asyncio
import aiohttp
import base64
from dotenv import load_dotenv

load_dotenv()

async def diagnose_credentials():
    username = os.getenv('EARTHDATA_USERNAME')
    password = os.getenv('EARTHDATA_PASSWORD')
    
    print("NASA EarthData Credential Diagnostics")
    print("=" * 50)
    
    print(f"Username from .env: '{username}'")
    print(f"Password length: {len(password) if password else 0} characters")
    print(f"Password starts with: '{password[:4]}...' (first 4 chars)")
    print(f"Password ends with: '...{password[-4:]}' (last 4 chars)")
    
    if '@' in password:
        print(f"⚠️  Password contains @ symbols: {password.count('@')} found")
    
    # Test different authentication methods
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    print(f"\nBase64 encoded credentials: {encoded_credentials[:20]}...")
    
    # Test authentication
    urls_to_test = [
        ("URS Profile", "https://urs.earthdata.nasa.gov/api/users/user"),
        ("URS OAuth", "https://urs.earthdata.nasa.gov/oauth/authorize?client_id=test"),
        ("CMR Echo", "https://cmr.earthdata.nasa.gov/legacy-services/rest/tokens"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in urls_to_test:
            print(f"\nTesting {name}...")
            print(f"URL: {url}")
            
            headers = {"Authorization": f"Basic {encoded_credentials}"}
            
            try:
                async with session.get(url, headers=headers) as response:
                    print(f"Status: {response.status}")
                    
                    if response.status == 200:
                        print("✅ SUCCESS!")
                        try:
                            data = await response.json()
                            if 'uid' in data:
                                print(f"Account ID: {data.get('uid')}")
                            if 'email_address' in data:
                                print(f"Email: {data.get('email_address')}")
                        except:
                            text = await response.text()
                            print(f"Response: {text[:100]}...")
                    elif response.status == 401:
                        print("❌ UNAUTHORIZED - Invalid credentials")
                    elif response.status == 403:
                        print("❌ FORBIDDEN - Account may need approval")
                    else:
                        print(f"❌ ERROR: HTTP {response.status}")
                        
                    response_text = await response.text()
                    if "error" in response_text.lower():
                        print(f"Error details: {response_text[:200]}...")
                        
            except Exception as e:
                print(f"❌ Connection error: {e}")

    print(f"\n" + "=" * 50)
    print("TROUBLESHOOTING:")
    print("1. Verify your NASA EarthData account at: https://urs.earthdata.nasa.gov/")
    print("2. Check if email is verified (check spam folder)")
    print("3. Try logging into the website manually")
    print("4. Some services require additional application approval")
    print("5. Password special characters might need different escaping")

if __name__ == "__main__":
    asyncio.run(diagnose_credentials())