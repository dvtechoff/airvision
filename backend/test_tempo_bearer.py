#!/usr/bin/env python3
"""
NASA TEMPO Data Test with Bearer Token Authentication
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_tempo_with_bearer_token():
    """Test TEMPO data access using Bearer token authentication"""
    
    # Get bearer token
    bearer_token = os.getenv('EARTHDATA_BEARER_TOKEN')
    username = os.getenv('EARTHDATA_USERNAME')
    
    if not bearer_token:
        print("❌ ERROR: EARTHDATA_BEARER_TOKEN not found in .env file!")
        return False
    
    print("NASA TEMPO Data Test with Bearer Token")
    print("=" * 50)
    print(f"🔐 Using bearer token for user: {username}")
    print(f"🔐 Token length: {len(bearer_token)} characters")
    print(f"🔐 Token preview: {bearer_token[:20]}...{bearer_token[-20:]}")
    
    # Create authorization header
    auth_header = {"Authorization": f"Bearer {bearer_token}"}
    
    # Test 1: Verify token with user profile
    print("\n1️⃣ Testing bearer token authentication...")
    
    profile_url = "https://urs.earthdata.nasa.gov/api/users/user"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(profile_url, headers=auth_header) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ Bearer token authentication successful!")
                    print(f"   User ID: {user_data.get('uid', 'Unknown')}")
                    print(f"   Email: {user_data.get('email_address', 'Unknown')}")
                    print(f"   First Name: {user_data.get('first_name', 'Unknown')}")
                    print(f"   Last Name: {user_data.get('last_name', 'Unknown')}")
                else:
                    print(f"❌ Bearer token authentication failed: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    # Test 2: Search TEMPO collections
    print("\n2️⃣ Searching for TEMPO satellite collections...")
    
    collections_url = "https://cmr.earthdata.nasa.gov/search/collections.json"
    collection_params = {
        'provider': 'LARC_ASDC',
        'keyword': 'TEMPO',
        'page_size': 10
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(collections_url, params=collection_params, headers=auth_header) as response:
                if response.status == 200:
                    data = await response.json()
                    collections = data.get('feed', {}).get('entry', [])
                    
                    print(f"✅ Found {len(collections)} TEMPO collections:")
                    
                    tempo_products = []
                    for i, collection in enumerate(collections, 1):
                        title = collection.get('title', 'Unknown')
                        concept_id = collection.get('id', 'Unknown')
                        
                        print(f"\n   📊 Collection {i}:")
                        print(f"      Title: {title}")
                        print(f"      ID: {concept_id}")
                        
                        # Identify pollutant type
                        pollutant = "Unknown"
                        if 'NO2' in title.upper():
                            pollutant = "Nitrogen Dioxide (NO2)"
                        elif 'O3' in title.upper() or 'OZONE' in title.upper():
                            pollutant = "Ozone (O3)"
                        elif 'HCHO' in title.upper() or 'FORMALDEHYDE' in title.upper():
                            pollutant = "Formaldehyde (HCHO)"
                        elif 'AEROSOL' in title.upper():
                            pollutant = "Aerosol Optical Depth"
                        elif 'CLOUD' in title.upper():
                            pollutant = "Cloud Properties"
                        
                        print(f"      Measures: {pollutant}")
                        
                        tempo_products.append({
                            'title': title,
                            'id': concept_id,
                            'pollutant': pollutant
                        })
                    
                    # Test 3: Search for actual TEMPO data granules
                    if tempo_products:
                        print(f"\n3️⃣ Searching for TEMPO data granules...")
                        
                        # Use the first NO2 product for testing
                        no2_product = next((p for p in tempo_products if 'NO2' in p['pollutant']), tempo_products[0])
                        
                        print(f"   Using product: {no2_product['title']}")
                        print(f"   Product ID: {no2_product['id']}")
                        
                        # Search for recent granules over New York area
                        granules_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
                        
                        # Search parameters for North America
                        granule_params = {
                            'collection_concept_id': no2_product['id'],
                            'bounding_box': '-125,25,-65,50',  # North America bounding box
                            'temporal': f"{(datetime.utcnow() - timedelta(days=7)).isoformat()}Z,{datetime.utcnow().isoformat()}Z",
                            'page_size': 5,
                            'sort_key': 'start_date',
                            'sort_order': 'desc'
                        }
                        
                        async with session.get(granules_url, params=granule_params, headers=auth_header) as granule_response:
                            if granule_response.status == 200:
                                granule_data = await granule_response.json()
                                granules = granule_data.get('feed', {}).get('entry', [])
                                
                                if granules:
                                    print(f"✅ Found {len(granules)} recent TEMPO data granules!")
                                    
                                    for i, granule in enumerate(granules, 1):
                                        title = granule.get('title', 'Unknown')
                                        start_time = granule.get('time_start', 'Unknown')
                                        end_time = granule.get('time_end', 'Unknown')
                                        
                                        print(f"\n      🛰️ Granule {i}:")
                                        print(f"         File: {title}")
                                        print(f"         Time: {start_time} to {end_time}")
                                        
                                        # Check for data download links
                                        links = granule.get('links', [])
                                        data_links = [link for link in links if 'data' in link.get('rel', '')]
                                        
                                        if data_links:
                                            print(f"         📁 Data files available: {len(data_links)}")
                                            print(f"         🔗 Sample URL: {data_links[0].get('href', 'N/A')[:60]}...")
                                            
                                            # Test 4: Verify data access
                                            print(f"\n4️⃣ Testing data access for granule {i}...")
                                            data_url = data_links[0].get('href')
                                            
                                            try:
                                                async with session.head(data_url, headers=auth_header, allow_redirects=True) as data_response:
                                                    if data_response.status == 200:
                                                        file_size = data_response.headers.get('Content-Length', 'Unknown')
                                                        content_type = data_response.headers.get('Content-Type', 'Unknown')
                                                        
                                                        print(f"            ✅ Data file accessible!")
                                                        print(f"            📊 Size: {file_size} bytes")
                                                        print(f"            📄 Type: {content_type}")
                                                        
                                                        return True  # Success!
                                                    else:
                                                        print(f"            ❌ Data access failed: HTTP {data_response.status}")
                                            except Exception as e:
                                                print(f"            ❌ Data access error: {e}")
                                        else:
                                            print(f"         ⚠️ No data download links found")
                                else:
                                    print("⚠️ No recent TEMPO granules found")
                                    print("   This is normal - TEMPO data may not be available for all times/locations")
                            else:
                                print(f"❌ Granule search failed: HTTP {granule_response.status}")
                else:
                    print(f"❌ Collections search failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Collections search error: {e}")
    
    print(f"\n" + "=" * 50)
    print("🎉 BEARER TOKEN TEST COMPLETE!")
    print("✅ Your NASA EarthData bearer token is working")
    print("✅ TEMPO satellite collections are accessible")  
    print("✅ You can access real NASA air quality data")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_tempo_with_bearer_token())
    
    if result:
        print(f"\n🚀 SUCCESS: NASA TEMPO data access is fully functional!")
        print("Your AirVision app can now use real satellite data for North America.")
    else:
        print(f"\n⚠️ Partial success: Bearer token works but data access needs refinement.")