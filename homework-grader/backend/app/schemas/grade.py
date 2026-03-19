"""
Pydantic schemas for Grade and Feedback API.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.feedback import FeedbackCategory


# =============================================================================
# FEEDBACK SCHEMAS
# =============================================================================

class FeedbackBase(BaseModel):
    """Base schema for Feedback."""
    
    category: FeedbackCategory
    title: str = Field(..., min_length=3, max_length=255)
    comment: str = Field(..., min_length=3)
    category_score: Optional[int] = Field(None, ge=0)
    category_max_score: Optional[int] = Field(None, ge=0)
    line_start: Optional[int] = Field(None, ge=1)
    line_end: Optional[int] = Field(None, ge=1)


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback."""
    pass


class FeedbackResponse(FeedbackBase):
    """Schema for feedback response."""
    
    id: int
    grade_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# GRADE SCHEMAS
# =============================================================================

class GradeBase(BaseModel):
    """Base schema for Grade."""
    
    score: float = Field(..., ge=0, description="Score received")
    max_score: float = Field(..., gt=0, description="Maximum possible score")
    summary: Optional[str] = Field(None, description="Overall summary")
    strengths: Optional[str] = Field(None, description="What was done well")
    weaknesses: Optional[str] = Field(None, description="What needs improvement")
    suggestions: Optional[str] = Field(None, description="Suggestions for improvement")
    grading_criteria: Optional[Dict[str, Any]] = Field(None, description="Structured grading breakdown")
    ai_confidence: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")


class GradeCreate(GradeBase):
    """Schema for creating a grade."""
    
    submission_id: int = Field(..., description="Submission ID")
    feedback_items: Optional[List[FeedbackCreate]] = Field(default=[], description="Detailed feedback items")


class GradeUpdate(BaseModel):
    """Schema for updating a grade."""
    
    score: Optional[float] = Field(None, ge=0)
    max_score: Optional[float] = Field(None, gt=0)
    summary: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    suggestions: Optional[str] = None
    grading_criteria: Optional[Dict[str, Any]] = None
    ai_confidence: Optional[float] = Field(None, ge=0, le=1)


class GradeResponse(GradeBase):
    """Schema for grade response."""
    
    id: int
    submission_id: int
    percentage: float
    letter_grade: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GradeWithFeedback(GradeResponse):
    """Schema for grade response with feedback items."""
    
    feedback_items: List[FeedbackResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# GRADING REQUEST SCHEMA
# =============================================================================

class GradingRequest(BaseModel):
    """Schema for grading request."""
    
    submission_id: int = Field(..., description="Submission ID to grade")
    use_rag: bool = Field(default=True, description="Use RAG for context from course materials")
    custom_instructions: Optional[str] = Field(None, description="Additional grading instructions")


class BatchGradingRequest(BaseModel):
    """Schema for batch grading request."""
    
    assignment_id: int = Field(..., description="Assignment ID")
    submission_ids: Optional[List[int]] = Field(None, description="Specific submission IDs (empty = all)")
    use_rag: bool = Field(default=True, description="Use RAG for context")


# =============================================================================
# GRADING RESPONSE SCHEMA
# =============================================================================

class GradingResponse(BaseModel):
    """Schema for grading response."""
    
    success: bool
    message: str
    grade: Optional[GradeWithFeedback] = None
    error: Optional[str] = None
