"""
Pydantic schemas for Course API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class CourseBase(BaseModel):
    """Base schema for Course."""
    
    course_code: str = Field(..., min_length=3, max_length=20, description="Course code (e.g., CSC 895)")
    course_name: str = Field(..., min_length=3, max_length=255, description="Course name")
    description: Optional[str] = Field(None, description="Course description")
    semester: str = Field(..., description="Semester (e.g., Spring 2026)")
    year: int = Field(..., ge=2020, le=2100, description="Year")
    is_active: bool = Field(default=True, description="Course active status")


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class CourseCreate(CourseBase):
    """Schema for creating a new course."""
    
    faculty_id: int = Field(..., description="Faculty ID teaching this course")


class CourseUpdate(BaseModel):
    """Schema for updating a course."""
    
    course_code: Optional[str] = Field(None, min_length=3, max_length=20)
    course_name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = Field(None, ge=2020, le=2100)
    faculty_id: Optional[int] = None
    is_active: Optional[bool] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class CourseResponse(CourseBase):
    """Schema for course response."""
    
    id: int
    faculty_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CourseWithDetails(CourseResponse):
    """Schema for course response with additional details."""
    
    faculty_name: Optional[str] = None
    total_assignments: int = 0
    total_materials: int = 0
    total_students: int = 0
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# LIST RESPONSE
# =============================================================================

class CourseListResponse(BaseModel):
    """Schema for paginated course list response."""
    
    total: int
    courses: list[CourseResponse]
    page: int = 1
    page_size: int = 50
