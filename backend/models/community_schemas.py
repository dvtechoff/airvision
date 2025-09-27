from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class FeedbackType(str, Enum):
    general = "general"
    bug_report = "bug_report"
    feature_request = "feature_request"
    data_accuracy = "data_accuracy"
    ui_ux = "ui_ux"

class IncidentSeverity(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"

class IncidentType(str, Enum):
    air_quality_spike = "air_quality_spike"
    industrial_emission = "industrial_emission"
    wildfire_smoke = "wildfire_smoke"
    traffic_pollution = "traffic_pollution"
    construction_dust = "construction_dust"
    chemical_spill = "chemical_spill"
    unusual_odor = "unusual_odor"
    respiratory_irritation = "respiratory_irritation"
    other = "other"

class VerificationStatus(str, Enum):
    pending = "pending"
    under_review = "under_review"
    verified = "verified"
    rejected = "rejected"
    resolved = "resolved"

class UserFeedback(BaseModel):
    id: Optional[str] = None
    feedback_type: FeedbackType
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    location: Optional[str] = None
    priority: str = Field(default="normal")
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="open")
    
    @validator('user_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

class IncidentLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: str
    state: Optional[str] = None
    country: Optional[str] = None

class IncidentReport(BaseModel):
    id: Optional[str] = None
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    location: IncidentLocation
    reporter_name: Optional[str] = None
    reporter_email: Optional[str] = None
    reporter_phone: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    verification_status: VerificationStatus = Field(default=VerificationStatus.pending)
    verification_notes: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    public_visibility: bool = Field(default=False)
    affected_people_count: Optional[int] = Field(None, ge=0)
    environmental_impact: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)  # File URLs/paths
    tags: List[str] = Field(default_factory=list)
    upvotes: int = Field(default=0)
    downvotes: int = Field(default=0)
    community_comments: List[Dict[str, Any]] = Field(default_factory=list)

class IncidentVerification(BaseModel):
    incident_id: str
    verifier_id: str
    verifier_name: str
    verification_status: VerificationStatus
    verification_notes: str = Field(..., min_length=10, max_length=1000)
    evidence_provided: bool = Field(default=False)
    requires_followup: bool = Field(default=False)
    followup_notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class CommunityAlert(BaseModel):
    id: Optional[str] = None
    incident_id: str
    alert_type: str = Field(default="community_incident")
    title: str
    message: str
    severity: IncidentSeverity
    location: IncidentLocation
    affected_radius_km: float = Field(default=5.0)
    active_until: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    source: str = Field(default="community_report")

class FeedbackResponse(BaseModel):
    id: str
    status: str
    message: str
    timestamp: datetime

class IncidentListResponse(BaseModel):
    incidents: List[IncidentReport]
    total_count: int
    verified_count: int
    pending_count: int

class CommunityStats(BaseModel):
    total_reports: int
    verified_reports: int
    active_incidents: int
    total_feedback: int
    response_rate: float
    average_verification_time_hours: float
    top_incident_types: List[Dict[str, Any]]
    community_engagement_score: float