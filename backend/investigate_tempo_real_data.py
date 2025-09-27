#!/usr/bin/env python3
"""
Deep TEMPO Granule Investigation
Debug why real TEMPO granules are not being found
"""

import earthaccess
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def investigate_tempo_collections():
    """Investigate available TEMPO collections and parameters"""
    
    print("🔍 DEEP TEMPO GRANULE INVESTIGATION")
    print("=" * 60)
    
    # Set credentials
    username = os.getenv('EARTHDATA_USERNAME')
    password = os.getenv('EARTHDATA_PASSWORD')
    
    print(f"🔑 Using credentials: {username}")
    
    # Authenticate
    os.environ['EARTHDATA_USERNAME'] = username
    os.environ['EARTHDATA_PASSWORD'] = password
    auth = earthaccess.login(persist=False)
    
    if not auth:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test different TEMPO collection names and parameters
    tempo_collections = [
        "TEMPO_NO2_L2",
        "TEMPO_NO2_L3", 
        "TEMPO_O3_L2",
        "TEMPO_O3_L3",
        "TEMPO_HCHO_L2",
        "TEMPO_HCHO_L3",
        "TEMPO_NO2_L3_V03",
        "TEMPO_O3_L3_V03",
        "TEMPO_HCHO_L3_V03"
    ]
    
    # Different time ranges to test
    time_ranges = [
        ("2024-01-01", "2024-12-31"),  # Full 2024
        ("2024-06-01", "2024-08-31"),  # Summer 2024 
        ("2024-08-01", "2024-08-31"),  # August 2024
        ("2024-07-01", "2024-07-31"),  # July 2024
        ("2023-08-01", "2023-12-31"),  # Late 2023
        ("2023-01-01", "2023-12-31"),  # Full 2023
    ]
    
    # Test locations
    test_locations = [
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
        {"name": "Houston", "lat": 29.7604, "lon": -95.3698},
    ]
    
    results_found = False
    
    for collection in tempo_collections:
        print(f"\n🛰️ Testing Collection: {collection}")
        print("-" * 40)
        
        for start_date, end_date in time_ranges:
            for location in test_locations:
                try:
                    print(f"  📍 {location['name']} ({start_date} to {end_date})")
                    
                    # Search with different parameters
                    results = earthaccess.search_data(
                        short_name=collection,
                        temporal=(start_date, end_date),
                        point=(location['lon'], location['lat']),
                    )
                    
                    if results:
                        print(f"    ✅ FOUND {len(results)} granules!")
                        results_found = True
                        
                        # Show first result details
                        result = results[0]
                        print(f"    📄 Sample file: {result.data_links()[0].split('/')[-1]}")
                        print(f"    📊 Size: {result.size / (1024*1024):.1f} MB")
                        print(f"    🌍 Cloud hosted: {result.cloud_hosted}")
                        
                        # Try to get more details
                        try:
                            print(f"    📅 Temporal: {result.temporal}")
                            print(f"    🌐 Spatial: {result.spatial}")
                        except:
                            pass
                        
                        return True  # Found data, stop searching
                    else:
                        print(f"    ❌ No granules found")
                        
                except Exception as e:
                    print(f"    💥 Error: {e}")
    
    if not results_found:
        print("\n❌ NO TEMPO GRANULES FOUND IN ANY COLLECTION OR TIME RANGE")
        print("This suggests either:")
        print("1. TEMPO data is not yet available in earthaccess")
        print("2. Collection names are different")
        print("3. Data is restricted or not public yet")
        print("4. TEMPO mission started later than expected")
    
    return results_found

def check_tempo_mission_status():
    """Check if TEMPO mission data is actually available"""
    
    print(f"\n🚀 TEMPO MISSION STATUS CHECK")
    print("=" * 40)
    
    # Try to search for any TEMPO-related data
    auth = earthaccess.login(persist=False)
    
    try:
        # Search for any datasets with "TEMPO" in the name
        print("🔍 Searching for any TEMPO datasets...")
        
        # This searches collections/datasets, not granules
        collections = earthaccess.search_datasets(
            keyword="TEMPO"
        )
        
        if collections:
            print(f"✅ Found {len(collections)} TEMPO-related collections:")
            for i, collection in enumerate(collections[:10]):  # Show first 10
                try:
                    print(f"  {i+1}. {collection.concept_id()} - {collection.title()}")
                    print(f"     Short name: {collection.short_name()}")
                    print(f"     Version: {collection.version()}")
                    print(f"     Abstract: {collection.abstract()[:100]}...")
                    print()
                except Exception as e:
                    print(f"  {i+1}. Collection info unavailable: {e}")
        else:
            print("❌ No TEMPO collections found")
            
    except Exception as e:
        print(f"💥 Error searching collections: {e}")

def check_alternative_no2_data():
    """Check for alternative NO2 satellite data sources"""
    
    print(f"\n🌍 ALTERNATIVE SATELLITE DATA SOURCES")
    print("=" * 40)
    
    auth = earthaccess.login(persist=False)
    
    # Try other satellite missions that provide NO2 data
    alternative_collections = [
        "OMI_L2_NO2",           # OMI (Ozone Monitoring Instrument)
        "OMNO2_L2",             # OMI NO2
        "TROPOMI_L2_NO2",       # TROPOMI NO2
        "S5P_L2_NO2___",        # Sentinel-5P NO2
        "MOD04_L2",             # MODIS Aerosol
        "MYD04_L2",             # MODIS Aqua Aerosol
    ]
    
    for collection in alternative_collections:
        try:
            print(f"🛰️ Testing {collection}...")
            
            results = earthaccess.search_data(
                short_name=collection,
                temporal=("2024-08-01", "2024-08-05"),
                point=(-74.0060, 40.7128),  # New York
            )
            
            if results:
                print(f"  ✅ Found {len(results)} granules for {collection}")
                result = results[0]
                print(f"  📄 Sample: {result.data_links()[0].split('/')[-1]}")
            else:
                print(f"  ❌ No data found for {collection}")
                
        except Exception as e:
            print(f"  💥 Error with {collection}: {e}")

def main():
    print("NASA TEMPO REAL DATA INVESTIGATION")
    print("Investigating why TEMPO granules are not found")
    print("=" * 70)
    
    # Step 1: Deep collection investigation
    found_tempo = investigate_tempo_collections()
    
    # Step 2: Check mission status
    check_tempo_mission_status()
    
    # Step 3: Check alternatives
    if not found_tempo:
        check_alternative_no2_data()
    
    print(f"\n" + "="*70)
    print("INVESTIGATION COMPLETE")
    print("="*70)
    
    if found_tempo:
        print("🎉 SUCCESS: Real TEMPO data found and accessible!")
    else:
        print("⚠️ TEMPO data not currently available through earthaccess")
        print("💡 Recommendations:")
        print("1. TEMPO mission may not have public data yet")
        print("2. Use alternative satellite data (OMI, TROPOMI)")
        print("3. Continue with simulation until TEMPO data is released")

if __name__ == "__main__":
    main()