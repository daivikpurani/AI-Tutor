"""
Pydantic schemas for Assignment API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class AssignmentBase(BaseModel):
    """Base schema for Assignment."""
    
    title: str = Field(..., min_length=3, max_length=255, description="Assignment title")
    description: Optional[str] = Field(None, description="Assignment description")
    grading_instructions: str = Field(..., min_length=10, description="Natural language grading instructions")
    max_score: float = Field(default=100.0, gt=0, description="Maximum score")
    due_date: datetime = Field(..., description="Due date and time")
    late_submission_allowed: bool = Field(default=False, description="Allow late submissions")
    late_penalty_percent: float = Field(default=0.0, ge=0, le=100, description="Late penalty per day (%)")
    is_published: bool = Field(default=False, description="Published status")
    is_active: bool = Field(default=True, description="Active status")


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class AssignmentCreate(AssignmentBase):
    """Schema for creating a new assignment."""
    
    course_id: int = Field(..., description="Course ID")


class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment."""
    
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    grading_instructions: Optional[str] = Field(None, min_length=10)
    max_score: Optional[float] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    late_submission_allowed: Optional[bool] = None
    late_penalty_percent: Optional[float] = Field(None, ge=0, le=100)
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class AssignmentResponse(AssignmentBase):
    """Schema for assignment response."""
    
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    is_overdue: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class AssignmentWithDetails(AssignmentResponse):
    """Schema for assignment response with additional details."""
    
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    total_submissions: int = 0
    graded_submissions: int = 0
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# LIST RESPONSE
# =============================================================================

class AssignmentListResponse(BaseModel):
    """Schema for paginated assignment list response."""
    
    total: int
    assignments: list[AssignmentResponse]
    page: int = 1
    page_size: int = 50
