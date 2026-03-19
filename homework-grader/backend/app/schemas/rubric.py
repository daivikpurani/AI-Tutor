"""
Pydantic schemas for Rubric API.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


# =============================================================================
# RUBRIC CATEGORY SCHEMA
# =============================================================================

class RubricCategory(BaseModel):
    """Schema for a single rubric category."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    weight: float = Field(..., ge=0, le=100, description="Weight/percentage")
    description: str = Field(..., min_length=1, description="Category description")
    criteria: Optional[List[str]] = Field(default=[], description="List of criteria")


class RubricCriteria(BaseModel):
    """Schema for complete rubric criteria."""
    
    categories: List[RubricCategory] = Field(..., min_items=1, description="Grading categories")
    
    @field_validator('categories')
    @classmethod
    def validate_weights_sum_to_100(cls, v):
        """Ensure category weights sum to 100."""
        total = sum(cat.weight for cat in v)
        if abs(total - 100.0) > 0.01:
            raise ValueError(f'Category weights must sum to 100 (got {total})')
        return v


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class RubricBase(BaseModel):
    """Base schema for Rubric."""
    
    rubric_name: str = Field(..., min_length=3, max_length=255, description="Rubric name")
    description: Optional[str] = Field(None, description="Rubric description")
    criteria: Dict[str, Any] = Field(..., description="Grading criteria (structured)")
    grading_instructions: str = Field(..., min_length=10, description="Natural language instructions for AI")
    max_score: float = Field(default=100.0, gt=0, description="Maximum score")
    is_active: bool = Field(default=True, description="Rubric active status")
    is_default: bool = Field(default=False, description="Default rubric for section")


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class RubricCreate(RubricBase):
    """Schema for creating a new rubric."""
    
    section_id: int = Field(..., description="Section ID")


class RubricUpdate(BaseModel):
    """Schema for updating a rubric."""
    
    rubric_name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    grading_instructions: Optional[str] = Field(None, min_length=10)
    max_score: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class RubricResponse(RubricBase):
    """Schema for rubric response."""
    
    id: int
    section_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RubricWithDetails(RubricResponse):
    """Schema for rubric response with additional details."""
    
    section_code: Optional[str] = None
    category_count: int = 0
    assignments_using_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# LIST RESPONSE
# =============================================================================

class RubricListResponse(BaseModel):
    """Schema for paginated rubric list response."""
    
    total: int
    rubrics: list[RubricResponse]
    page: int = 1
    page_size: int = 50


# =============================================================================
# HELPER SCHEMAS
# =============================================================================

class RubricValidationResponse(BaseModel):
    """Schema for rubric validation response."""
    
    is_valid: bool
    message: str
    errors: Optional[List[str]] = None
