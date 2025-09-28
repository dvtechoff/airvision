"""
Test script for Gemini AI integration
"""

import asyncio
import json
from services.gemini_ai_service import GeminiAIService

async def test_gemini_suggestions():
    """Test the Gemini AI suggestions functionality"""
    
    # Sample forecast data
    sample_forecast = [
        {
            "time": "2024-01-10T15:00:00Z",
            "aqi": 85,
            "category": "Moderate"
        },
        {
            "time": "2024-01-10T16:00:00Z",
            "aqi": 95,
            "category": "Moderate"
        },
        {
            "time": "2024-01-10T17:00:00Z",
            "aqi": 110,
            "category": "Unhealthy for Sensitive Groups"
        },
        {
            "time": "2024-01-10T18:00:00Z",
            "aqi": 125,
            "category": "Unhealthy for Sensitive Groups"
        }
    ]
    
    # Sample user profile
    user_profile = {
        "age_group": "adult",
        "health_conditions": ["asthma"],
        "activity_level": "moderate"
    }
    
    try:
        print("🔬 Testing Gemini AI Service...")
        
        # Initialize service
        service = GeminiAIService()
        print(f"✅ Service initialized with API key: {service.api_key[:10]}...")
        
        # Test AI suggestions
        print("🧠 Requesting AI suggestions...")
        suggestions = await service.get_aqi_suggestions(
            city="New York",
            forecast_data=sample_forecast,
            user_profile=user_profile
        )
        
        print("✅ AI Suggestions received!")
        print(f"📍 City: {suggestions['city']}")
        print(f"🎯 Confidence: {suggestions['confidence']}")
        print(f"📊 Source: {suggestions['source']}")
        print(f"📋 Categories with suggestions: {list(suggestions['suggestions'].keys())}")
        
        # Print a few sample suggestions
        for category, items in suggestions['suggestions'].items():
            if items:  # Only show categories with actual suggestions
                print(f"\n💡 {category.replace('_', ' ').title()}:")
                for i, item in enumerate(items[:2], 1):  # Show first 2 items
                    print(f"   {i}. {item}")
                if len(items) > 2:
                    print(f"   ... and {len(items) - 2} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini_suggestions())
    if result:
        print("\n🎉 Gemini AI integration test PASSED!")
    else:
        print("\n💥 Gemini AI integration test FAILED!")