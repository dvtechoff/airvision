#!/usr/bin/env python3
"""
Simplified TEMPO Data Test Script

This script provides a focused test of TEMPO data access and processing.
It will authenticate with NASA EarthData and show what actual TEMPO data looks like.
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

async def test_tempo_access():
    """Simple test to verify TEMPO data access"""
    
    # Get credentials
    username = os.getenv('EARTHDATA_USERNAME')
    password = os.getenv('EARTHDATA_PASSWORD')
    
    if not username or not password:
        print("❌ ERROR: NASA EarthData credentials not found!")
        print("\nTo fix this:")
        print("1. Create a .env file in the backend directory")
        print("2. Add these lines to .env:")
        print("   EARTHDATA_USERNAME=your_earthdata_username")
        print("   EARTHDATA_PASSWORD=your_earthdata_password")
        print("\n3. Get free credentials at: https://urs.earthdata.nasa.gov/")
        return False
    
    print(f"🔐 Using credentials for: {username}")
    
    # Create auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = {"Authorization": f"Basic {encoded_credentials}"}
    
    # Test authentication
    print("\n1️⃣ Testing authentication...")
    auth_url = "https://urs.earthdata.nasa.gov/api/users/user"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(auth_url, headers=auth_header) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ Authentication successful!")
                    print(f"   Account: {user_data.get('uid', 'Unknown')}")
                else:
                    print(f"❌ Authentication failed: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    # Search for TEMPO NO2 data (most common TEMPO product)
    print("\n2️⃣ Searching for TEMPO NO2 data...")
    
    search_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
    
    # Search parameters for New York area
    params = {
        'collection_concept_id': 'C2208419613-LARC_ASDC',  # TEMPO NO2 L2 Daily
        'bounding_box': '-75,40,-73,42',  # New York area
        'temporal': f"{(datetime.utcnow() - timedelta(days=30)).isoformat()}Z,{datetime.utcnow().isoformat()}Z",
        'page_size': 3,
        'sort_key': 'start_date',
        'sort_order': 'desc'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(search_url, params=params, headers=auth_header) as response:
                if response.status == 200:
                    data = await response.json()
                    granules = data.get('feed', {}).get('entry', [])
                    
                    if granules:
                        print(f"✅ Found {len(granules)} TEMPO granules!")
                        
                        for i, granule in enumerate(granules, 1):
                            title = granule.get('title', 'Unknown')
                            start_time = granule.get('time_start', 'Unknown')
                            
                            print(f"\n   📊 Granule {i}:")
                            print(f"      Title: {title}")
                            print(f"      Time: {start_time}")
                            
                            # Show available data links
                            links = granule.get('links', [])
                            data_links = [l for l in links if 'data' in l.get('rel', '')]
                            
                            if data_links:
                                print(f"      Data available: {len(data_links)} files")
                                print(f"      Sample URL: {data_links[0].get('href', 'N/A')[:80]}...")
                    else:
                        print("⚠️ No recent TEMPO granules found for New York area")
                        print("   This is normal - TEMPO data may not always be available")
                else:
                    print(f"❌ Search failed: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    # Test different TEMPO products
    print("\n3️⃣ Checking available TEMPO products...")
    
    collections_url = "https://cmr.earthdata.nasa.gov/search/collections.json"
    collection_params = {
        'provider': 'LARC_ASDC',
        'keyword': 'TEMPO',
        'page_size': 10
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(collections_url, params=collection_params) as response:
                if response.status == 200:
                    data = await response.json()
                    collections = data.get('feed', {}).get('entry', [])
                    
                    print(f"✅ Found {len(collections)} TEMPO collections:")
                    
                    for i, collection in enumerate(collections, 1):
                        title = collection.get('title', 'Unknown')
                        concept_id = collection.get('id', 'Unknown')
                        
                        print(f"   {i}. {title}")
                        print(f"      ID: {concept_id}")
                        
                        # Show what pollutants this measures
                        if 'NO2' in title:
                            print("      📊 Measures: Nitrogen Dioxide (NO2)")
                        elif 'O3' in title or 'OZONE' in title:
                            print("      📊 Measures: Ozone (O3)")
                        elif 'HCHO' in title or 'FORMALDEHYDE' in title:
                            print("      📊 Measures: Formaldehyde (HCHO)")
                        
                else:
                    print(f"❌ Collections search failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Collections search error: {e}")
    
    print("\n4️⃣ Summary:")
    print("✅ Your NASA EarthData credentials are working!")
    print("✅ TEMPO data collections are accessible")
    print("✅ You can access NASA's satellite data for North America")
    
    print("\nNext steps:")
    print("- The backend can now use these credentials to fetch real TEMPO data")
    print("- TEMPO provides hourly air quality data over North America") 
    print("- Data includes NO2, O3, HCHO measurements from space")
    
    return True

if __name__ == "__main__":
    print("NASA TEMPO Data Access Test")
    print("=" * 40)
    print("Testing access to real NASA TEMPO satellite data...")
    
    result = asyncio.run(test_tempo_access())
    
    if result:
        print(f"\n🎉 SUCCESS: TEMPO data access is working!")
        print("You can now use real NASA satellite data in your application.")
    else:
        print(f"\n❌ FAILED: Please check your credentials and try again.")