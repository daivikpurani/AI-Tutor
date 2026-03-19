"""
Feedback model for detailed feedback on specific aspects of submissions.
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class FeedbackCategory(str, enum.Enum):
    """Feedback category enumeration."""
    CORRECTNESS = "correctness"
    COMPLETENESS = "completeness"
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    STYLE = "style"
    PERFORMANCE = "performance"
    OTHER = "other"


class Feedback(Base):
    """
    Detailed Feedback model for specific aspects of submissions.
    """
    
    __tablename__ = "feedback"
    
    # Grade Association
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    
    # Feedback Information
    category = Column(Enum(FeedbackCategory), nullable=False)
    title = Column(String(255), nullable=False)
    comment = Column(Text, nullable=False)
    
    # Scoring (optional per-category scoring)
    category_score = Column(Integer, nullable=True)  # Score for this specific category
    category_max_score = Column(Integer, nullable=True)  # Max score for this category
    
    # Line-specific feedback (for code submissions)
    line_start = Column(Integer, nullable=True)
    line_end = Column(Integer, nullable=True)
    
    # Relationships
    grade = relationship("Grade", back_populates="feedback_items")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, grade_id={self.grade_id}, category={self.category}, title={self.title})>"
