"""
Gemini AI Service for AQI-based suggestions and recommendations
Provides personalized health and lifestyle advice based on air quality forecasts
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class GeminiAIService:
    """
    Service for generating AI-powered suggestions based on AQI forecasts
    using Google's Gemini AI model
    """
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    async def get_aqi_suggestions(
        self, 
        city: str, 
        forecast_data: List[Dict[str, Any]], 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized suggestions based on AQI forecast data
        
        Args:
            city: City name
            forecast_data: List of forecast points with AQI, category, time
            user_profile: Optional user profile with health conditions, age, etc.
        
        Returns:
            Dictionary containing AI-generated suggestions
        """
        try:
            # Prepare the context for Gemini
            context = self._prepare_context(city, forecast_data, user_profile)
            
            # Generate suggestions using Gemini AI
            suggestions = await self._call_gemini_api(context)
            
            return {
                "city": city,
                "timestamp": datetime.now().isoformat(),
                "suggestions": suggestions,
                "forecast_summary": self._get_forecast_summary(forecast_data),
                "confidence": "high",
                "source": "Gemini AI + TEMPO Enhanced Forecast"
            }
            
        except Exception as e:
            print(f"Error generating Gemini suggestions: {e}")
            return self._get_fallback_suggestions(city, forecast_data)
    
    def _prepare_context(
        self, 
        city: str, 
        forecast_data: List[Dict[str, Any]], 
        user_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Prepare the context prompt for Gemini AI"""
        
        # Get current and upcoming AQI levels
        current_aqi = forecast_data[0]['aqi'] if forecast_data else 100
        current_category = forecast_data[0]['category'] if forecast_data else 'Moderate'
        
        # Analyze forecast trend
        max_aqi = max([f['aqi'] for f in forecast_data]) if forecast_data else current_aqi
        min_aqi = min([f['aqi'] for f in forecast_data]) if forecast_data else current_aqi
        avg_aqi = sum([f['aqi'] for f in forecast_data]) / len(forecast_data) if forecast_data else current_aqi
        
        # Determine trend
        if len(forecast_data) > 1:
            trend = "improving" if forecast_data[-1]['aqi'] < current_aqi else "worsening" if forecast_data[-1]['aqi'] > current_aqi else "stable"
        else:
            trend = "stable"
        
        # Build user profile context
        profile_context = ""
        if user_profile:
            age_group = user_profile.get('age_group', 'adult')
            health_conditions = user_profile.get('health_conditions', [])
            activity_level = user_profile.get('activity_level', 'moderate')
            
            profile_context = f"""
User Profile:
- Age Group: {age_group}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None specified'}
- Activity Level: {activity_level}
"""
        
        # Create comprehensive context
        context = f"""
You are an expert air quality health advisor powered by NASA TEMPO satellite data and real-time atmospheric measurements. 
Provide personalized, actionable advice based on the following air quality forecast for {city}.

Current Air Quality Data:
- City: {city}
- Current AQI: {current_aqi} ({current_category})
- 24-hour Range: {min_aqi} - {max_aqi} AQI
- Average AQI: {avg_aqi:.0f}
- Trend: {trend}
- Data Source: NASA TEMPO Satellite + OpenWeatherMap

{profile_context}

Forecast Details (Next 6 Hours):
"""
        
        # Add hourly forecast details
        for i, forecast in enumerate(forecast_data[:6]):
            time_str = datetime.fromisoformat(forecast['time'].replace('Z', '+00:00')).strftime('%I:%M %p')
            context += f"- {time_str}: AQI {forecast['aqi']} ({forecast['category']})\n"
        
        context += """
Please provide comprehensive, actionable suggestions in the following categories. Make them specific, practical, and tailored to the current air quality conditions:

1. IMMEDIATE HEALTH RECOMMENDATIONS (next 2-4 hours)
2. OUTDOOR ACTIVITY GUIDANCE (exercise, sports, commuting)  
3. INDOOR AIR QUALITY TIPS (ventilation, air purifiers, windows)
4. VULNERABLE GROUPS ADVICE (children, elderly, asthma/respiratory conditions)
5. COMMUTE & TRAVEL SUGGESTIONS (timing, routes, transportation modes)
6. LONG-TERM HEALTH STRATEGIES (if air quality is persistently poor)

Format your response as practical, easy-to-follow bullet points. Be specific about timing (e.g., "avoid outdoor exercise between 2-5 PM"). Include scientific reasoning where helpful. Consider the trend - if air quality is improving/worsening, mention optimal timing for activities.

Make suggestions actionable and city-specific when relevant. Remember this data comes from NASA satellites and is highly accurate.
"""
        
        return context
    
    async def _call_gemini_api(self, context: str) -> Dict[str, Any]:
        """Make the API call to Gemini AI"""
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": context
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
                "stopSequences": []
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Extract the generated text
                    if 'candidates' in result and len(result['candidates']) > 0:
                        generated_text = result['candidates'][0]['content']['parts'][0]['text']
                        return self._parse_ai_response(generated_text)
                    else:
                        raise Exception("No candidates returned from Gemini API")
                else:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error {response.status}: {error_text}")
    
    def _parse_ai_response(self, generated_text: str) -> Dict[str, Any]:
        """Parse the AI response into structured suggestions"""
        
        suggestions = {
            "immediate_health": [],
            "outdoor_activity": [],
            "indoor_tips": [],
            "vulnerable_groups": [],
            "commute_travel": [],
            "long_term": [],
            "general_advice": []
        }
        
        # Split the response and categorize suggestions
        lines = generated_text.split('\n')
        current_category = "general_advice"
        
        category_mapping = {
            "immediate": "immediate_health",
            "outdoor": "outdoor_activity", 
            "indoor": "indoor_tips",
            "vulnerable": "vulnerable_groups",
            "commute": "commute_travel",
            "travel": "commute_travel",
            "long-term": "long_term",
            "long term": "long_term"
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line indicates a new category
            line_lower = line.lower()
            for keyword, category in category_mapping.items():
                if keyword in line_lower and ("recommendation" in line_lower or "guidance" in line_lower or "advice" in line_lower or "tip" in line_lower):
                    current_category = category
                    break
            
            # Add bullet points to appropriate category
            if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                suggestion_text = line[2:].strip()
                if suggestion_text:
                    suggestions[current_category].append(suggestion_text)
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                # Handle numbered lists
                suggestion_text = line.split('.', 1)[1].strip() if '.' in line else line
                if suggestion_text:
                    suggestions[current_category].append(suggestion_text)
        
        # Add general advice if categories are empty
        if all(len(cat) == 0 for cat in suggestions.values()):
            suggestions["general_advice"] = [generated_text]
        
        return suggestions
    
    def _get_forecast_summary(self, forecast_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of the forecast data"""
        
        if not forecast_data:
            return {"status": "no_data"}
        
        current_aqi = forecast_data[0]['aqi']
        max_aqi = max([f['aqi'] for f in forecast_data])
        min_aqi = min([f['aqi'] for f in forecast_data])
        avg_aqi = sum([f['aqi'] for f in forecast_data]) / len(forecast_data)
        
        # Find peak pollution times
        peak_times = []
        for i, forecast in enumerate(forecast_data):
            if forecast['aqi'] == max_aqi:
                time_str = datetime.fromisoformat(forecast['time'].replace('Z', '+00:00')).strftime('%I:%M %p')
                peak_times.append(time_str)
        
        # Determine overall air quality level
        if avg_aqi <= 50:
            overall_quality = "Good"
        elif avg_aqi <= 100:
            overall_quality = "Moderate"
        elif avg_aqi <= 150:
            overall_quality = "Unhealthy for Sensitive Groups"
        elif avg_aqi <= 200:
            overall_quality = "Unhealthy"
        else:
            overall_quality = "Very Unhealthy"
        
        return {
            "current_aqi": current_aqi,
            "range": {"min": min_aqi, "max": max_aqi},
            "average": round(avg_aqi, 1),
            "overall_quality": overall_quality,
            "peak_pollution_times": peak_times[:3],  # Show up to 3 peak times
            "hours_forecasted": len(forecast_data)
        }
    
    def _get_fallback_suggestions(self, city: str, forecast_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide fallback suggestions if Gemini AI is unavailable"""
        
        current_aqi = forecast_data[0]['aqi'] if forecast_data else 100
        
        # Basic rule-based suggestions
        suggestions = {
            "immediate_health": [],
            "outdoor_activity": [],
            "indoor_tips": [],
            "vulnerable_groups": [],
            "commute_travel": [],
            "long_term": [],
            "general_advice": []
        }
        
        if current_aqi <= 50:  # Good
            suggestions["general_advice"] = [
                "Air quality is excellent! Perfect time for all outdoor activities.",
                "Great conditions for exercise, sports, and outdoor recreation.",
                "Enjoy fresh air - consider opening windows for natural ventilation."
            ]
        elif current_aqi <= 100:  # Moderate
            suggestions["outdoor_activity"] = [
                "Good time for most outdoor activities with normal precautions.",
                "Sensitive individuals should consider reducing prolonged outdoor exertion."
            ]
            suggestions["indoor_tips"] = [
                "Consider using air purifiers if you have respiratory sensitivities."
            ]
        elif current_aqi <= 150:  # Unhealthy for Sensitive Groups
            suggestions["vulnerable_groups"] = [
                "People with asthma, heart disease, or lung conditions should limit outdoor activities.",
                "Children and elderly should reduce time spent outdoors."
            ]
            suggestions["outdoor_activity"] = [
                "Consider postponing intense outdoor exercise.",
                "Limit outdoor activities during peak pollution hours."
            ]
        else:  # Unhealthy or worse
            suggestions["immediate_health"] = [
                "Limit all outdoor activities, especially for sensitive groups.",
                "Keep windows closed and use air purifiers indoors.",
                "Consider wearing N95 masks when going outside."
            ]
        
        return {
            "city": city,
            "timestamp": datetime.now().isoformat(),
            "suggestions": suggestions,
            "forecast_summary": self._get_forecast_summary(forecast_data),
            "confidence": "medium",
            "source": "Rule-based fallback system"
        }

    async def get_health_impact_analysis(
        self, 
        city: str, 
        forecast_data: List[Dict[str, Any]],
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate detailed health impact analysis for the forecast period
        """
        try:
            context = f"""
You are a public health expert analyzing air quality data from NASA TEMPO satellites for {city}.

Forecast Data Analysis:
- Duration: {duration_hours} hours
- Current AQI: {forecast_data[0]['aqi'] if forecast_data else 'Unknown'}
- Data points: {len(forecast_data)}

Hourly AQI Values:
"""
            
            for i, forecast in enumerate(forecast_data[:12]):  # Show 12 hours max
                time_str = datetime.fromisoformat(forecast['time'].replace('Z', '+00:00')).strftime('%I:%M %p')
                context += f"- {time_str}: {forecast['aqi']} AQI ({forecast['category']})\n"
            
            context += """
Please provide a detailed health impact analysis including:

1. POPULATION HEALTH RISKS
   - General population impact
   - High-risk group concerns
   - Severity assessment

2. PHYSIOLOGICAL EFFECTS
   - Respiratory system impact
   - Cardiovascular effects
   - Eye and skin irritation potential

3. ACTIVITY MODIFICATIONS
   - Exercise recommendations
   - Work/school considerations
   - Transportation advice

4. MEDICAL RECOMMENDATIONS
   - When to seek medical attention
   - Medication considerations for asthmatics
   - Emergency indicators

Provide scientific, evidence-based analysis in clear, actionable language.
"""
            
            # Call Gemini API for health analysis
            health_analysis = await self._call_gemini_api(context)
            
            return {
                "city": city,
                "analysis_timestamp": datetime.now().isoformat(),
                "health_impact": health_analysis,
                "forecast_duration_hours": duration_hours,
                "data_source": "NASA TEMPO + Gemini AI Health Analysis"
            }
            
        except Exception as e:
            print(f"Error generating health analysis: {e}")
            return {
                "error": "Health analysis temporarily unavailable",
                "timestamp": datetime.now().isoformat()
            }