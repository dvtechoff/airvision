import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from collections import defaultdict, Counter

from models.community_schemas import (
    UserFeedback, IncidentReport, IncidentVerification, CommunityAlert,
    VerificationStatus, IncidentSeverity, IncidentType, CommunityStats,
    IncidentListResponse
)

logger = logging.getLogger(__name__)

class CommunityService:
    """
    Service for handling user feedback, incident reports, and community engagement.
    """
    
    def __init__(self):
        # In-memory storage (in production, use a database)
        self.feedback_storage: Dict[str, UserFeedback] = {}
        self.incident_storage: Dict[str, IncidentReport] = {}
        self.verification_storage: Dict[str, List[IncidentVerification]] = {}
        self.community_alerts: Dict[str, CommunityAlert] = {}
        self.user_votes: Dict[str, Dict[str, str]] = {}  # user_id -> incident_id -> vote_type
        
        # Initialize with some sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample verified incidents"""
        sample_incidents = [
            {
                "incident_type": "air_quality_spike",
                "severity": "moderate",
                "title": "Unusual Air Quality Reading Downtown",
                "description": "Noticed increased air pollution readings near the industrial district. Multiple residents reporting respiratory irritation.",
                "location": {
                    "latitude": 40.7589,
                    "longitude": -73.9851,
                    "address": "Times Square, New York, NY",
                    "city": "New York",
                    "state": "NY",
                    "country": "USA"
                },
                "verification_status": "verified",
                "public_visibility": True,
                "affected_people_count": 25,
                "upvotes": 12,
                "tags": ["industrial", "downtown", "verified"]
            },
            {
                "incident_type": "wildfire_smoke",
                "severity": "high",
                "title": "Wildfire Smoke Affecting Air Quality",
                "description": "Smoke from nearby wildfires is significantly impacting air quality. Visibility reduced and AQI readings elevated.",
                "location": {
                    "latitude": 34.0522,
                    "longitude": -118.2437,
                    "address": "Los Angeles, CA",
                    "city": "Los Angeles",
                    "state": "CA",
                    "country": "USA"
                },
                "verification_status": "verified",
                "public_visibility": True,
                "affected_people_count": 500,
                "upvotes": 45,
                "tags": ["wildfire", "smoke", "verified", "emergency"]
            }
        ]
        
        for i, sample in enumerate(sample_incidents):
            incident_id = f"incident_{i+1:03d}"
            incident = IncidentReport(
                id=incident_id,
                timestamp=datetime.now() - timedelta(hours=i*2),
                verified_at=datetime.now() - timedelta(hours=i*2-1),
                **sample
            )
            self.incident_storage[incident_id] = incident
            
            # Create community alert for verified high-severity incidents
            if incident.severity == "high" and incident.verification_status == "verified":
                alert_id = f"alert_{incident_id}"
                alert = CommunityAlert(
                    id=alert_id,
                    incident_id=incident_id,
                    title=f"⚠️ {incident.title}",
                    message=f"Verified incident reported: {incident.description[:100]}...",
                    severity=incident.severity,
                    location=incident.location,
                    affected_radius_km=10.0
                )
                self.community_alerts[alert_id] = alert
    
    async def submit_feedback(self, feedback: UserFeedback) -> Dict[str, Any]:
        """Submit user feedback"""
        try:
            feedback_id = str(uuid.uuid4())
            feedback.id = feedback_id
            feedback.timestamp = datetime.now()
            
            self.feedback_storage[feedback_id] = feedback
            
            logger.info(f"Feedback submitted: {feedback_id} - {feedback.feedback_type}")
            
            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Thank you for your feedback! We'll review it and get back to you.",
                "estimated_response_time": "24-48 hours"
            }
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return {
                "success": False,
                "message": "Failed to submit feedback. Please try again."
            }
    
    async def submit_incident_report(self, incident: IncidentReport) -> Dict[str, Any]:
        """Submit an incident report"""
        try:
            incident_id = str(uuid.uuid4())
            incident.id = incident_id
            incident.timestamp = datetime.now()
            
            self.incident_storage[incident_id] = incident
            
            logger.info(f"Incident reported: {incident_id} - {incident.incident_type}")
            
            # Auto-create alert for critical incidents
            if incident.severity == "critical":
                await self._create_immediate_alert(incident)
            
            return {
                "success": True,
                "incident_id": incident_id,
                "message": "Incident report submitted successfully. It will be reviewed for verification.",
                "verification_timeline": "Reports are typically reviewed within 2-6 hours."
            }
            
        except Exception as e:
            logger.error(f"Error submitting incident: {e}")
            return {
                "success": False,
                "message": "Failed to submit incident report. Please try again."
            }
    
    async def verify_incident(self, verification: IncidentVerification) -> Dict[str, Any]:
        """Verify an incident report (admin/moderator function)"""
        try:
            incident_id = verification.incident_id
            
            if incident_id not in self.incident_storage:
                return {"success": False, "message": "Incident not found"}
            
            incident = self.incident_storage[incident_id]
            incident.verification_status = verification.verification_status
            incident.verification_notes = verification.verification_notes
            incident.verified_by = verification.verifier_name
            incident.verified_at = datetime.now()
            
            # Make public if verified
            if verification.verification_status == "verified":
                incident.public_visibility = True
                
                # Create community alert for verified incidents
                if incident.severity in ["high", "critical"]:
                    await self._create_community_alert(incident)
            
            # Store verification record
            if incident_id not in self.verification_storage:
                self.verification_storage[incident_id] = []
            self.verification_storage[incident_id].append(verification)
            
            logger.info(f"Incident {incident_id} verification: {verification.verification_status}")
            
            return {
                "success": True,
                "message": f"Incident {verification.verification_status.value} successfully"
            }
            
        except Exception as e:
            logger.error(f"Error verifying incident: {e}")
            return {"success": False, "message": "Verification failed"}
    
    async def get_public_incidents(self, city: Optional[str] = None, limit: int = 50) -> IncidentListResponse:
        """Get public (verified) incidents"""
        try:
            incidents = []
            
            for incident in self.incident_storage.values():
                if incident.public_visibility and incident.verification_status == "verified":
                    if city is None or incident.location.city.lower() == city.lower():
                        incidents.append(incident)
            
            # Sort by timestamp (newest first)
            incidents.sort(key=lambda x: x.timestamp, reverse=True)
            incidents = incidents[:limit]
            
            # Count statistics
            total_count = len(incidents)
            verified_count = sum(1 for i in incidents if i.verification_status == "verified")
            pending_count = sum(1 for i in self.incident_storage.values() if i.verification_status == "pending")
            
            return IncidentListResponse(
                incidents=incidents,
                total_count=total_count,
                verified_count=verified_count,
                pending_count=pending_count
            )
            
        except Exception as e:
            logger.error(f"Error getting incidents: {e}")
            return IncidentListResponse(incidents=[], total_count=0, verified_count=0, pending_count=0)
    
    async def get_community_alerts(self, latitude: float, longitude: float, radius_km: float = 50.0) -> List[CommunityAlert]:
        """Get active community alerts near a location"""
        try:
            nearby_alerts = []
            
            for alert in self.community_alerts.values():
                if not alert.is_active:
                    continue
                
                # Simple distance calculation (in production, use proper geospatial calculation)
                lat_diff = abs(alert.location.latitude - latitude)
                lon_diff = abs(alert.location.longitude - longitude)
                estimated_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough km conversion
                
                if estimated_distance <= radius_km:
                    nearby_alerts.append(alert)
            
            # Sort by severity and creation time
            severity_order = {"critical": 4, "high": 3, "moderate": 2, "low": 1}
            nearby_alerts.sort(key=lambda x: (severity_order[x.severity], x.created_at), reverse=True)
            
            return nearby_alerts
            
        except Exception as e:
            logger.error(f"Error getting community alerts: {e}")
            return []
    
    async def vote_on_incident(self, incident_id: str, user_id: str, vote_type: str) -> Dict[str, Any]:
        """Allow users to vote on incidents (upvote/downvote)"""
        try:
            if incident_id not in self.incident_storage:
                return {"success": False, "message": "Incident not found"}
            
            incident = self.incident_storage[incident_id]
            
            if not incident.public_visibility:
                return {"success": False, "message": "Cannot vote on non-public incidents"}
            
            # Check if user has already voted
            if user_id not in self.user_votes:
                self.user_votes[user_id] = {}
            
            previous_vote = self.user_votes[user_id].get(incident_id)
            
            # Remove previous vote
            if previous_vote == "upvote":
                incident.upvotes -= 1
            elif previous_vote == "downvote":
                incident.downvotes -= 1
            
            # Add new vote
            if vote_type == "upvote":
                incident.upvotes += 1
                self.user_votes[user_id][incident_id] = "upvote"
            elif vote_type == "downvote":
                incident.downvotes += 1
                self.user_votes[user_id][incident_id] = "downvote"
            else:
                # Remove vote
                if incident_id in self.user_votes[user_id]:
                    del self.user_votes[user_id][incident_id]
            
            return {
                "success": True,
                "upvotes": incident.upvotes,
                "downvotes": incident.downvotes
            }
            
        except Exception as e:
            logger.error(f"Error voting on incident: {e}")
            return {"success": False, "message": "Vote failed"}
    
    async def get_community_stats(self) -> CommunityStats:
        """Get community engagement statistics"""
        try:
            total_reports = len(self.incident_storage)
            verified_reports = sum(1 for i in self.incident_storage.values() if i.verification_status == "verified")
            active_incidents = sum(1 for i in self.incident_storage.values() 
                                 if i.public_visibility and i.verification_status == "verified")
            total_feedback = len(self.feedback_storage)
            
            # Calculate response rate
            response_rate = (verified_reports / total_reports * 100) if total_reports > 0 else 0
            
            # Average verification time
            verification_times = []
            for incident in self.incident_storage.values():
                if incident.verified_at:
                    hours_to_verify = (incident.verified_at - incident.timestamp).total_seconds() / 3600
                    verification_times.append(hours_to_verify)
            
            avg_verification_time = sum(verification_times) / len(verification_times) if verification_times else 0
            
            # Top incident types
            incident_types = Counter(i.incident_type for i in self.incident_storage.values())
            top_incident_types = [{"type": k, "count": v} for k, v in incident_types.most_common(5)]
            
            # Community engagement score (based on votes, reports, feedback)
            total_votes = sum(i.upvotes + i.downvotes for i in self.incident_storage.values())
            engagement_score = min(100, (total_votes + total_feedback) / max(1, total_reports) * 10)
            
            return CommunityStats(
                total_reports=total_reports,
                verified_reports=verified_reports,
                active_incidents=active_incidents,
                total_feedback=total_feedback,
                response_rate=round(response_rate, 1),
                average_verification_time_hours=round(avg_verification_time, 1),
                top_incident_types=top_incident_types,
                community_engagement_score=round(engagement_score, 1)
            )
            
        except Exception as e:
            logger.error(f"Error getting community stats: {e}")
            return CommunityStats(
                total_reports=0, verified_reports=0, active_incidents=0,
                total_feedback=0, response_rate=0.0, average_verification_time_hours=0.0,
                top_incident_types=[], community_engagement_score=0.0
            )
    
    async def _create_community_alert(self, incident: IncidentReport):
        """Create a community alert for a verified incident"""
        alert_id = f"alert_{incident.id}"
        alert = CommunityAlert(
            id=alert_id,
            incident_id=incident.id,
            title=f"🚨 {incident.title}",
            message=f"Verified incident: {incident.description[:150]}...",
            severity=incident.severity,
            location=incident.location,
            affected_radius_km=15.0 if incident.severity == "critical" else 8.0
        )
        self.community_alerts[alert_id] = alert
    
    async def _create_immediate_alert(self, incident: IncidentReport):
        """Create immediate alert for critical incidents (pending verification)"""
        alert_id = f"urgent_{incident.id}"
        alert = CommunityAlert(
            id=alert_id,
            incident_id=incident.id,
            title=f"⚠️ URGENT: {incident.title}",
            message=f"Critical incident reported - Under verification: {incident.description[:100]}...",
            severity=incident.severity,
            location=incident.location,
            affected_radius_km=20.0,
            source="urgent_report"
        )
        self.community_alerts[alert_id] = alert