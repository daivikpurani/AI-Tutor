"""
Rubric model for professor-defined grading criteria.

Rubrics define how assignments should be graded for a specific section.
Professors can create multiple rubrics for different types of assignments.
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base


class Rubric(Base):
    """
    Rubric model for customized grading criteria.
    
    Professors can define section-specific rubrics that specify:
    - Grading categories and weights
    - Point allocation
    - Evaluation criteria
    - Natural language instructions for AI grader
    """
    
    __tablename__ = "rubrics"
    
    # Section Association
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False, index=True)
    
    # Rubric Information
    rubric_name = Column(String(255), nullable=False)  # e.g., "Programming Assignment Rubric"
    description = Column(Text, nullable=True)
    
    # Grading Criteria (Structured)
    # JSON structure example:
    # {
    #   "categories": [
    #     {
    #       "name": "Correctness",
    #       "weight": 40,
    #       "description": "Does the code produce correct output?",
    #       "criteria": ["All test cases pass", "Edge cases handled", ...]
    #     },
    #     {
    #       "name": "Code Quality",
    #       "weight": 30,
    #       "description": "Is the code well-written and maintainable?",
    #       "criteria": ["Proper naming", "Comments", "DRY principle", ...]
    #     },
    #     ...
    #   ]
    # }
    criteria = Column(JSON, nullable=False)
    
    # Natural Language Instructions for AI
    # This provides context to the LLM on how to interpret the rubric
    grading_instructions = Column(Text, nullable=False)
    
    # Scoring
    max_score = Column(Float, default=100.0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # Default rubric for section
    
    # Relationships
    section = relationship("Section", back_populates="rubrics")
    assignments = relationship("Assignment", back_populates="rubric")
    
    def __repr__(self):
        return f"<Rubric(id={self.id}, name={self.rubric_name}, section_id={self.section_id})>"
    
    @property
    def category_count(self):
        """Get number of grading categories."""
        if self.criteria and isinstance(self.criteria, dict):
            return len(self.criteria.get("categories", []))
        return 0
    
    def validate_criteria(self):
        """Validate rubric criteria structure."""
        if not isinstance(self.criteria, dict):
            return False, "Criteria must be a dictionary"
        
        if "categories" not in self.criteria:
            return False, "Criteria must contain 'categories' key"
        
        categories = self.criteria["categories"]
        if not isinstance(categories, list) or len(categories) == 0:
            return False, "Categories must be a non-empty list"
        
        total_weight = 0
        for category in categories:
            if not isinstance(category, dict):
                return False, "Each category must be a dictionary"
            
            required_keys = ["name", "weight", "description"]
            for key in required_keys:
                if key not in category:
                    return False, f"Category missing required key: {key}"
            
            total_weight += category["weight"]
        
        # Allow some tolerance for floating point
        if abs(total_weight - 100.0) > 0.01:
            return False, f"Category weights must sum to 100 (got {total_weight})"
        
        return True, "Valid"
