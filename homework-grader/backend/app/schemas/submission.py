"""
Pydantic schemas for Submission API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.submission import SubmissionStatus


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class SubmissionBase(BaseModel):
    """Base schema for Submission."""
    
    submission_text: Optional[str] = Field(None, description="Text-based submission content")
    attempt_number: int = Field(default=1, ge=1, description="Attempt number")


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class SubmissionCreate(SubmissionBase):
    """Schema for creating a new submission."""
    
    assignment_id: int = Field(..., description="Assignment ID")
    student_id: int = Field(..., description="Student ID")
    submission_date: Optional[datetime] = Field(default_factory=datetime.utcnow)


class SubmissionUpdate(BaseModel):
    """Schema for updating a submission."""
    
    submission_text: Optional[str] = None
    status: Optional[SubmissionStatus] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class SubmissionResponse(SubmissionBase):
    """Schema for submission response."""
    
    id: int
    assignment_id: int
    student_id: int
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    submission_date: datetime
    status: SubmissionStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionWithDetails(SubmissionResponse):
    """Schema for submission response with additional details."""
    
    assignment_title: Optional[str] = None
    student_name: Optional[str] = None
    course_code: Optional[str] = None
    has_grade: bool = False
    grade_score: Optional[float] = None
    grade_percentage: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# LIST RESPONSE
# =============================================================================

class SubmissionListResponse(BaseModel):
    """Schema for paginated submission list response."""
    
    total: int
    submissions: list[SubmissionResponse]
    page: int = 1
    page_size: int = 50
