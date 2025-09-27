#!/usr/bin/env python3
"""
NASA EarthData API Test Script for TEMPO Satellite Data

This script tests real TEMPO data retrieval using your NASA EarthData credentials.
Make sure to create a .env file with your EARTHDATA_USERNAME and EARTHDATA_PASSWORD.

Usage:
1. Copy env.example to .env
2. Fill in your NASA EarthData credentials in .env
3. Run: python test_earthdata_tempo.py
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

class EarthDataTEMPOTest:
    def __init__(self):
        self.username = os.getenv('EARTHDATA_USERNAME')
        self.password = os.getenv('EARTHDATA_PASSWORD')
        self.cmr_base_url = "https://cmr.earthdata.nasa.gov/search"
        self.larc_base_url = "https://asdc.larc.nasa.gov/data/TEMPO"
        
        if not self.username or not self.password:
            raise ValueError(
                "NASA EarthData credentials not found!\n"
                "Please create a .env file with:\n"
                "EARTHDATA_USERNAME=your_username\n"
                "EARTHDATA_PASSWORD=your_password\n\n"
                "Get credentials at: https://urs.earthdata.nasa.gov/"
            )
    
    def get_auth_header(self):
        """Create basic auth header for NASA EarthData"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}"}
    
    async def test_authentication(self):
        """Test if credentials work with NASA EarthData"""
        print("🔐 Testing NASA EarthData authentication...")
        
        auth_url = "https://urs.earthdata.nasa.gov/api/users/user"
        headers = self.get_auth_header()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(auth_url, headers=headers) as response:
                    if response.status == 200:
                        user_info = await response.json()
                        print(f"✅ Authentication successful!")
                        print(f"   Username: {user_info.get('uid', 'N/A')}")
                        print(f"   Email: {user_info.get('email_address', 'N/A')}")
                        return True
                    else:
                        print(f"❌ Authentication failed: HTTP {response.status}")
                        print(f"   Response: {await response.text()}")
                        return False
            except Exception as e:
                print(f"❌ Authentication error: {e}")
                return False
    
    async def search_tempo_collections(self):
        """Search for available TEMPO collections"""
        print("\n🛰️ Searching for TEMPO collections...")
        
        search_url = f"{self.cmr_base_url}/collections.json"
        params = {
            'provider': 'LARC_ASDC',
            'keyword': 'TEMPO',
            'page_size': 10
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        collections = data.get('feed', {}).get('entry', [])
                        
                        print(f"✅ Found {len(collections)} TEMPO collections:")
                        for i, collection in enumerate(collections, 1):
                            title = collection.get('title', 'Unknown')
                            concept_id = collection.get('id', 'Unknown')
                            print(f"   {i}. {title}")
                            print(f"      ID: {concept_id}")
                        
                        return collections
                    else:
                        print(f"❌ Collection search failed: HTTP {response.status}")
                        return []
            except Exception as e:
                print(f"❌ Collection search error: {e}")
                return []
    
    async def search_tempo_granules(self, collection_concept_id=None, lat=40.7128, lon=-74.0060):
        """Search for TEMPO data granules for a specific location"""
        print(f"\n📊 Searching for TEMPO data near coordinates ({lat}, {lon})...")
        
        # If no collection specified, use the main TEMPO NO2 product
        if not collection_concept_id:
            collection_concept_id = "C2208419613-LARC_ASDC"  # TEMPO NO2 L2 product
        
        search_url = f"{self.cmr_base_url}/granules.json"
        
        # Search for recent data (last 7 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'collection_concept_id': collection_concept_id,
            'bounding_box': f"{lon-1},{lat-1},{lon+1},{lat+1}",  # 2-degree box around location
            'temporal': f"{start_date.isoformat()}Z,{end_date.isoformat()}Z",
            'page_size': 5,
            'sort_key': 'start_date',
            'sort_order': 'desc'
        }
        
        headers = self.get_auth_header()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        granules = data.get('feed', {}).get('entry', [])
                        
                        print(f"✅ Found {len(granules)} recent TEMPO granules:")
                        
                        for i, granule in enumerate(granules, 1):
                            title = granule.get('title', 'Unknown')
                            start_date = granule.get('time_start', 'Unknown')
                            end_date = granule.get('time_end', 'Unknown')
                            
                            print(f"   {i}. {title}")
                            print(f"      Time: {start_date} to {end_date}")
                            
                            # Get download links
                            links = granule.get('links', [])
                            data_links = [link for link in links if link.get('rel') == 'http://esipfed.org/ns/fedsearch/1.1/data#']
                            
                            if data_links:
                                print(f"      Data URL: {data_links[0].get('href', 'N/A')}")
                            
                        return granules
                    else:
                        print(f"❌ Granule search failed: HTTP {response.status}")
                        error_text = await response.text()
                        print(f"   Response: {error_text[:200]}...")
                        return []
            except Exception as e:
                print(f"❌ Granule search error: {e}")
                return []
    
    async def test_data_download(self, granule):
        """Test downloading a TEMPO data file"""
        print(f"\n⬇️ Testing data download for: {granule.get('title', 'Unknown')}")
        
        # Get data download links
        links = granule.get('links', [])
        data_links = [link for link in links if link.get('rel') == 'http://esipfed.org/ns/fedsearch/1.1/data#']
        
        if not data_links:
            print("❌ No data download links found")
            return None
        
        download_url = data_links[0].get('href')
        headers = self.get_auth_header()
        
        async with aiohttp.ClientSession() as session:
            try:
                # Just test if we can access the file (don't download the full file)
                async with session.head(download_url, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        file_size = response.headers.get('Content-Length', 'Unknown')
                        content_type = response.headers.get('Content-Type', 'Unknown')
                        
                        print(f"✅ Data file accessible!")
                        print(f"   URL: {download_url}")
                        print(f"   Size: {file_size} bytes")
                        print(f"   Type: {content_type}")
                        return True
                    else:
                        print(f"❌ Data access failed: HTTP {response.status}")
                        print(f"   URL: {download_url}")
                        return False
            except Exception as e:
                print(f"❌ Data access error: {e}")
                return False
    
    async def get_tempo_data_for_location(self, city="New York", lat=40.7128, lon=-74.0060):
        """Complete test to get TEMPO data for a specific location"""
        print(f"\n🌍 Getting TEMPO data for {city} ({lat}, {lon})")
        print("=" * 60)
        
        # Test authentication
        auth_success = await self.test_authentication()
        if not auth_success:
            return None
        
        # Search collections
        collections = await self.search_tempo_collections()
        if not collections:
            print("❌ No TEMPO collections found")
            return None
        
        # Use the first available collection
        main_collection = collections[0]
        collection_id = main_collection.get('id')
        print(f"\n📋 Using collection: {main_collection.get('title')}")
        
        # Search for granules
        granules = await self.search_tempo_granules(collection_id, lat, lon)
        if not granules:
            print("❌ No TEMPO granules found for this location/time")
            return None
        
        # Test data access for the most recent granule
        if granules:
            recent_granule = granules[0]
            download_success = await self.test_data_download(recent_granule)
            
            if download_success:
                print(f"\n🎉 SUCCESS: TEMPO data is accessible for {city}!")
                return {
                    'city': city,
                    'coordinates': {'lat': lat, 'lon': lon},
                    'collection': main_collection.get('title'),
                    'granule': recent_granule.get('title'),
                    'time_range': f"{recent_granule.get('time_start')} to {recent_granule.get('time_end')}",
                    'status': 'accessible'
                }
            else:
                print(f"\n⚠️ TEMPO data found but not accessible for {city}")
                return None
        
        return None

async def main():
    """Main test function"""
    print("NASA EarthData TEMPO API Test")
    print("=" * 40)
    
    try:
        tester = EarthDataTEMPOTest()
        
        # Test multiple North American cities
        test_cities = [
            ("New York", 40.7128, -74.0060),
            ("Los Angeles", 34.0522, -118.2437),
            ("Chicago", 41.8781, -87.6298),
            ("Houston", 29.7604, -95.3698),
            ("Toronto", 43.6532, -79.3832)
        ]
        
        results = []
        for city, lat, lon in test_cities:
            result = await tester.get_tempo_data_for_location(city, lat, lon)
            results.append(result)
            
            # Add a small delay between requests
            await asyncio.sleep(1)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        successful = [r for r in results if r is not None]
        print(f"✅ Successful: {len(successful)}/{len(test_cities)} cities")
        
        for result in successful:
            print(f"   • {result['city']}: {result['status']}")
        
        if successful:
            print(f"\n🎉 TEMPO data is working with your credentials!")
            print(f"   Collection: {successful[0].get('collection', 'Unknown')}")
            print(f"   Latest data: {successful[0].get('time_range', 'Unknown')}")
        else:
            print(f"\n❌ No TEMPO data could be accessed")
            print("   This might be due to:")
            print("   - Temporary server issues")
            print("   - No recent data available")
            print("   - Access permissions")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Before running this test:")
    print("1. Create a .env file in the backend directory")
    print("2. Add your NASA EarthData credentials:")
    print("   EARTHDATA_USERNAME=your_username")
    print("   EARTHDATA_PASSWORD=your_password")
    print("3. Get credentials at: https://urs.earthdata.nasa.gov/")
    print("\nStarting test in 3 seconds...")
    
    import time
    time.sleep(3)
    
    asyncio.run(main())