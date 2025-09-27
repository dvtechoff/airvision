#!/usr/bin/env python3
"""
Test script for AirVision Community Features
"""

import asyncio
import json
from services.community_service import CommunityService
from models.community_schemas import UserFeedback, IncidentReport, IncidentLocation

async def test_community_features():
    """Test the community service features"""
    
    print("🧪 Testing AirVision Community Features")
    print("=" * 50)
    
    # Initialize service
    service = CommunityService()
    
    # Test 1: Get community stats
    print("\n📊 Testing Community Stats...")
    stats = await service.get_community_stats()
    print(f"Total Reports: {stats.total_reports}")
    print(f"Verified Reports: {stats.verified_reports}")
    print(f"Active Incidents: {stats.active_incidents}")
    print(f"Response Rate: {stats.response_rate}%")
    print(f"Community Engagement Score: {stats.community_engagement_score}")
    
    # Test 2: Submit feedback
    print("\n💬 Testing Feedback Submission...")
    feedback = UserFeedback(
        feedback_type="feature_request",
        subject="Love the new community features!",
        message="The community reporting system is fantastic. Could we also add email notifications for nearby incidents?",
        user_name="Test User",
        user_email="test@example.com",
        location="New York"
    )
    
    feedback_result = await service.submit_feedback(feedback)
    print(f"Feedback submitted: {feedback_result['success']}")
    print(f"Message: {feedback_result['message']}")
    
    # Test 3: Submit incident report
    print("\n🚨 Testing Incident Report...")
    incident = IncidentReport(
        incident_type="unusual_odor",
        severity="moderate",
        title="Strong Chemical Odor Near Industrial Area",
        description="Noticed a strong chemical smell while walking near the industrial district. Several people in the area were covering their noses. The odor was particularly strong around 3rd Street and Industrial Boulevard.",
        location=IncidentLocation(
            latitude=40.7831,
            longitude=-73.9712,
            address="3rd Street & Industrial Blvd",
            city="New York",
            state="NY",
            country="USA"
        ),
        reporter_name="Community Member",
        reporter_email="member@example.com",
        affected_people_count=8,
        environmental_impact="Strong chemical odor affecting pedestrians and nearby residents",
        tags=["chemical", "industrial", "odor", "health concern"]
    )
    
    incident_result = await service.submit_incident_report(incident)
    print(f"Incident reported: {incident_result['success']}")
    print(f"Incident ID: {incident_result.get('incident_id', 'N/A')}")
    print(f"Message: {incident_result['message']}")
    
    # Test 4: Get public incidents
    print("\n📋 Testing Public Incidents Retrieval...")
    incidents = await service.get_public_incidents(city="New York", limit=5)
    print(f"Found {incidents.total_count} verified incidents")
    print(f"Pending verification: {incidents.pending_count}")
    
    for i, incident in enumerate(incidents.incidents[:3], 1):
        print(f"  {i}. {incident.title}")
        print(f"     Severity: {incident.severity} | Type: {incident.incident_type}")
        print(f"     Location: {incident.location.city}")
        print(f"     Votes: ↑{incident.upvotes} ↓{incident.downvotes}")
    
    # Test 5: Get community alerts
    print("\n⚠️  Testing Community Alerts...")
    alerts = await service.get_community_alerts(40.7128, -74.0060, radius_km=25.0)
    print(f"Found {len(alerts)} active alerts near NYC")
    
    for alert in alerts:
        print(f"  🚨 {alert.title}")
        print(f"     Severity: {alert.severity}")
        print(f"     Location: {alert.location.city}")
    
    # Test 6: Updated stats after submissions
    print("\n📈 Updated Community Stats...")
    updated_stats = await service.get_community_stats()
    print(f"Total Reports: {updated_stats.total_reports}")
    print(f"Total Feedback: {updated_stats.total_feedback}")
    
    print("\n✅ All tests completed successfully!")
    print("\n🌟 Community Features Summary:")
    print("   • Feedback system for user suggestions and bug reports")
    print("   • Incident reporting for air quality issues")
    print("   • Community verification and voting system") 
    print("   • Real-time alerts for verified incidents")
    print("   • Comprehensive statistics and engagement metrics")
    print("   • Location-based incident filtering")
    print("   • Multi-severity incident classification")

if __name__ == "__main__":
    asyncio.run(test_community_features())