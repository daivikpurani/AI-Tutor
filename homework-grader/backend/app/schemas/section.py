"""
Pydantic schemas for Section API.
"""

from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class SectionBase(BaseModel):
    """Base schema for Section."""
    
    section_number: str = Field(..., min_length=1, max_length=10, description="Section number (e.g., '01', 'A')")
    semester: str = Field(..., description="Semester (e.g., 'Spring', 'Fall')")
    year: int = Field(..., ge=2020, le=2100, description="Year")
    days_of_week: Optional[str] = Field(None, description="Days (e.g., 'MW', 'TTh')")
    start_time: Optional[time] = Field(None, description="Class start time")
    end_time: Optional[time] = Field(None, description="Class end time")
    location: Optional[str] = Field(None, max_length=100, description="Room/location")
    max_students: Optional[int] = Field(30, ge=1, le=500, description="Maximum students")
    is_active: bool = Field(default=True, description="Section active status")


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class SectionCreate(SectionBase):
    """Schema for creating a new section."""
    
    course_id: int = Field(..., description="Course ID")
    faculty_id: int = Field(..., description="Faculty ID")
    vector_store_collection_id: Optional[str] = Field(None, description="Vector store collection ID")


class SectionUpdate(BaseModel):
    """Schema for updating a section."""
    
    section_number: Optional[str] = Field(None, min_length=1, max_length=10)
    faculty_id: Optional[int] = None
    semester: Optional[str] = None
    year: Optional[int] = Field(None, ge=2020, le=2100)
    days_of_week: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None
    max_students: Optional[int] = Field(None, ge=1, le=500)
    is_active: Optional[bool] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class SectionResponse(SectionBase):
    """Schema for section response."""
    
    id: int
    course_id: int
    faculty_id: int
    vector_store_collection_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SectionWithDetails(SectionResponse):
    """Schema for section response with additional details."""
    
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    faculty_name: Optional[str] = None
    enrolled_count: int = 0
    total_assignments: int = 0
    total_materials: int = 0
    is_full: bool = False
    section_code: Optional[str] = None
    schedule_display: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# LIST RESPONSE
# =============================================================================

class SectionListResponse(BaseModel):
    """Schema for paginated section list response."""
    
    total: int
    sections: list[SectionResponse]
    page: int = 1
    page_size: int = 50
