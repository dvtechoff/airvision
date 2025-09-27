"""
Database setup script for the enhanced air quality system
"""

import os
import sys
import asyncio
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config import db_manager
from services.enhanced_air_quality_service import EnhancedAirQualityService

def create_env_template():
    """Create a template .env file with database configuration"""
    env_content = """
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airvision
DB_USER=postgres
DB_PASSWORD=your_password_here

# Alternative: Full database URL (overrides individual settings above)
# DATABASE_URL=postgresql://postgres:password@localhost:5432/airvision

# OpenAQ API Configuration (optional - for real data)
# OPENAQ_API_KEY=your_openaq_api_key_here

# NASA EarthData Configuration (optional - for TEMPO data)
# EARTHDATA_USERNAME=your_username
# EARTHDATA_PASSWORD=your_password
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content.strip())
    
    print("📄 Created .env.template - copy to .env and configure your database settings")

async def setup_database():
    """
    Setup the database and optionally fetch initial location data
    """
    print("🚀 Starting Enhanced Air Quality System Setup")
    print("=" * 60)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found")
        create_env_template()
        print("\n🔧 Please configure your .env file and run this script again")
        return
    
    try:
        # Test database connection
        print("1. Testing database connection...")
        if db_manager.test_connection():
            print("   ✅ Database connection successful")
        else:
            print("   ❌ Database connection failed")
            print("   Please check your database settings in .env")
            return
        
        # Create tables
        print("\n2. Creating database tables...")
        db_manager.create_tables()
        print("   ✅ Database tables created successfully")
        
        # Initialize services
        print("\n3. Initializing services...")
        service = EnhancedAirQualityService()
        await service.initialize()
        print("   ✅ Services initialized")
        
        # Get current database stats
        print("\n4. Checking current database status...")
        stats = await service.location_service.get_database_stats()
        
        if stats.get('database_available'):
            total_locations = stats.get('total_locations', 0)
            print(f"   📊 Current locations in database: {total_locations}")
            
            if total_locations == 0:
                print("\n5. Database is empty - would you like to fetch OpenAQ locations?")
                print("   This requires an OpenAQ API key (free from https://openaq.org)")
                print("   You can:")
                print("   a) Add OPENAQ_API_KEY to your .env file and run: python setup_database.py --fetch-locations")
                print("   b) Skip for now and use fallback geocoding")
                
                choice = input("   Fetch locations now? (y/N): ").strip().lower()
                if choice == 'y':
                    api_key = os.getenv('OPENAQ_API_KEY')
                    if not api_key:
                        api_key = input("   Enter OpenAQ API key (or press Enter to skip): ").strip()
                    
                    if api_key:
                        print(f"\n   🌍 Fetching OpenAQ locations (this may take a few minutes)...")
                        setup_result = await service.setup_database_and_fetch_locations(api_key)
                        
                        if setup_result.get('success'):
                            fetch_stats = setup_result.get('stats', {})
                            print(f"   ✅ Fetched {fetch_stats.get('total_fetched', 0)} locations")
                            print(f"   📍 Stored {fetch_stats.get('stored_in_db', 0)} new locations")
                            print(f"   🌎 Found {len(fetch_stats.get('countries', []))} countries")
                        else:
                            print(f"   ⚠️  Location fetch had issues: {setup_result.get('error', 'Unknown error')}")
                    else:
                        print("   ⏭️  Skipping location fetch - system will use fallback geocoding")
            else:
                print(f"   ✅ Database already has {total_locations} locations")
        
        print("\n6. Testing the enhanced system...")
        
        # Test with a known location
        test_result = await service.get_comprehensive_air_quality("Piseco Lake", include_tempo=False)
        
        if test_result.get('location_found'):
            location_info = test_result['location_info']
            print(f"   ✅ System working! Found: {location_info['name']}")
            print(f"      Distance: {location_info['distance_km']:.2f} km")
            print(f"      Data sources: {', '.join(test_result.get('data_sources', ['None']))}")
        else:
            print("   ⚠️  Location search test failed - check your configuration")
        
        print("\n" + "=" * 60)
        print("🎉 Database setup completed successfully!")
        print("\n📚 Next steps:")
        print("   1. Start the backend server: python main.py")
        print("   2. Test the enhanced endpoints:")
        print("      • GET /api/enhanced/aqi?city=Piseco Lake")
        print("      • GET /api/enhanced/status")
        print("      • GET /api/enhanced/location/search?query=New York")
        
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup the Enhanced Air Quality System database")
    parser.add_argument("--fetch-locations", action="store_true", help="Fetch OpenAQ locations during setup")
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(setup_database())