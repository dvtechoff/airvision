from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime

from models.community_schemas import (
    UserFeedback, IncidentReport, IncidentVerification, CommunityAlert,
    CommunityStats, IncidentListResponse, FeedbackResponse
)
from services.community_service import CommunityService

router = APIRouter()

# Initialize community service
community_service = CommunityService()

@router.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(feedback: UserFeedback):
    """
    Submit user feedback about the application or air quality data.
    
    Allows users to provide general feedback, report bugs, request features,
    or report data accuracy issues.
    """
    try:
        result = await community_service.submit_feedback(feedback)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@router.post("/incidents", response_model=Dict[str, Any])
async def report_incident(incident: IncidentReport):
    """
    Report an air quality incident that may not be detected by sensors.
    
    Users can report pollution incidents, unusual odors, health impacts,
    or other air quality related events in their area.
    """
    try:
        result = await community_service.submit_incident_report(incident)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to report incident: {str(e)}")

@router.get("/incidents", response_model=IncidentListResponse)
async def get_incidents(
    city: Optional[str] = Query(None, description="Filter incidents by city"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of incidents to return")
):
    """
    Get list of verified public incidents.
    
    Returns community-reported incidents that have been verified by moderators.
    These incidents are visible to all users for community awareness.
    """
    try:
        return await community_service.get_public_incidents(city=city, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get incidents: {str(e)}")

@router.get("/incidents/{incident_id}")
async def get_incident_details(incident_id: str):
    """
    Get detailed information about a specific incident.
    """
    try:
        incident = community_service.incident_storage.get(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        if not incident.public_visibility:
            raise HTTPException(status_code=403, detail="Incident not public")
        
        # Include verification history
        verifications = community_service.verification_storage.get(incident_id, [])
        
        return {
            "incident": incident,
            "verification_history": verifications,
            "community_engagement": {
                "upvotes": incident.upvotes,
                "downvotes": incident.downvotes,
                "comments_count": len(incident.community_comments)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get incident details: {str(e)}")

@router.post("/incidents/{incident_id}/vote")
async def vote_on_incident(
    incident_id: str,
    vote_type: str = Query(..., regex="^(upvote|downvote|remove)$"),
    user_id: str = Query(..., description="User identifier for voting")
):
    """
    Vote on an incident (upvote, downvote, or remove vote).
    
    Community voting helps validate the accuracy and relevance of reported incidents.
    """
    try:
        result = await community_service.vote_on_incident(incident_id, user_id, vote_type)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to vote: {str(e)}")

@router.get("/alerts", response_model=List[CommunityAlert])
async def get_community_alerts(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude of location"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude of location"),
    radius_km: float = Query(25.0, ge=1, le=100, description="Search radius in kilometers")
):
    """
    Get active community alerts near a location.
    
    Returns verified incident alerts that may affect air quality in the specified area.
    """
    try:
        alerts = await community_service.get_community_alerts(latitude, longitude, radius_km)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.get("/stats", response_model=CommunityStats)
async def get_community_stats():
    """
    Get community engagement statistics and metrics.
    
    Provides insights into community participation, incident reports,
    verification rates, and overall engagement.
    """
    try:
        return await community_service.get_community_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/admin/verify")
async def verify_incident_admin(verification: IncidentVerification):
    """
    Admin/Moderator endpoint to verify incident reports.
    
    This endpoint would typically require authentication and proper authorization.
    """
    try:
        result = await community_service.verify_incident(verification)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify incident: {str(e)}")

@router.get("/admin/pending-incidents")
async def get_pending_incidents():
    """
    Admin endpoint to get incidents pending verification.
    """
    try:
        pending_incidents = []
        for incident in community_service.incident_storage.values():
            if incident.verification_status == "pending":
                pending_incidents.append(incident)
        
        # Sort by timestamp (oldest first for review priority)
        pending_incidents.sort(key=lambda x: x.timestamp)
        
        return {
            "pending_incidents": pending_incidents,
            "count": len(pending_incidents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending incidents: {str(e)}")

@router.get("/feedback/summary")
async def get_feedback_summary():
    """
    Get summary of user feedback for admin review.
    """
    try:
        from collections import Counter
        
        feedback_list = list(community_service.feedback_storage.values())
        
        # Categorize feedback
        feedback_by_type = Counter(f.feedback_type for f in feedback_list)
        feedback_by_status = Counter(f.status for f in feedback_list)
        
        # Recent feedback
        recent_feedback = sorted(feedback_list, key=lambda x: x.timestamp, reverse=True)[:10]
        
        return {
            "total_feedback": len(feedback_list),
            "by_type": dict(feedback_by_type),
            "by_status": dict(feedback_by_status),
            "recent_feedback": recent_feedback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback summary: {str(e)}")