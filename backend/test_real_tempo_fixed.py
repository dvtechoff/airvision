#!/usr/bin/env python3
"""
Test Real TEMPO Data Access
"""

import asyncio
from services.tempo_service_earthaccess import tempo_service_earthaccess
import json

async def test_real_tempo():
    print('🛰️  TESTING REAL TEMPO DATA ACCESS')
    print('=' * 50)
    
    # Test New York with the corrected service
    result = await tempo_service_earthaccess.get_tempo_data('New York')
    
    print('📊 TEMPO DATA RESULT:')
    print('-' * 30)
    print(f'Source: {result.get("source", "N/A")}')
    print(f'Data Type: {result.get("data_type", "N/A")}')
    print(f'Success: {result.get("success", False)}')
    print(f'Real Data: {result.get("real_data", False)}')
    
    if 'granule_file' in result:
        print(f'Real File: {result["granule_file"]}')
        print(f'File Size: {result.get("file_size_mb", 0)} MB')
        
    aqi_data = result.get('air_quality', {})
    print(f'\n🌪️  AQI: {aqi_data.get("aqi", "N/A")}')
    print(f'Category: {aqi_data.get("category", "N/A")}')
    
    measurements = result.get('measurements', {})
    if measurements:
        print(f'\n📏 NO2 Column: {measurements.get("no2_column", 0):.2e} molecules/cm²')
        print(f'O3 Column: {measurements.get("o3_column", 0):.1f} DU')
    
    quality = result.get('quality_flags', {})
    print(f'\n🔍 Data Quality: {quality.get("data_quality", "N/A")}')
    print(f'Processing Level: {quality.get("processing_level", "N/A")}')
    
    if result.get('real_data'):
        print('\n🎉 SUCCESS: REAL TEMPO DATA ACCESSED!')
        print('Your AirVision app now has access to actual NASA satellite files!')
    else:
        print('\n⚠️  Using simulated data (real files may not be available for today)')
        
    # Show the complete data structure
    print(f'\n📋 COMPLETE DATA STRUCTURE:')
    print('-' * 40)
    formatted_data = json.dumps(result, indent=2, default=str)
    print(formatted_data[:1500] + "..." if len(formatted_data) > 1500 else formatted_data)

if __name__ == "__main__":
    asyncio.run(test_real_tempo())