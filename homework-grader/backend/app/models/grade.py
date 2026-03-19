"""
Grade model representing grading results for submissions.
"""

from sqlalchemy import Column, Integer, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class Grade(Base):
    """
    Grade model for storing grading results.
    """
    
    __tablename__ = "grades"
    
    # Submission Association
    submission_id = Column(Integer, ForeignKey("submissions.id"), unique=True, nullable=False)
    
    # Grading Results
    score = Column(Float, nullable=False)  # Actual score received
    max_score = Column(Float, nullable=False)  # Maximum possible score
    percentage = Column(Float, nullable=False)  # Percentage score
    
    # Grading Details
    grading_criteria = Column(JSON, nullable=True)  # Structured grading breakdown
    ai_confidence = Column(Float, nullable=True)  # Confidence score from AI (0-1)
    
    # Professor feedback (when released to student)
    professor_feedback = Column(Text, nullable=True)
    is_released = Column(Boolean, default=False, nullable=False)
    
    # Comments (AI-generated, for professor reference)
    summary = Column(Text, nullable=True)  # Overall grading summary
    strengths = Column(Text, nullable=True)  # What was done well
    weaknesses = Column(Text, nullable=True)  # What needs improvement
    suggestions = Column(Text, nullable=True)  # Improvement suggestions
    
    # Relationships
    submission = relationship("Submission", back_populates="grade")
    feedback_items = relationship("Feedback", back_populates="grade", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Grade(id={self.id}, submission_id={self.submission_id}, score={self.score}/{self.max_score})>"
    
    @property
    def letter_grade(self):
        """Convert percentage to letter grade."""
        if self.percentage >= 93:
            return "A"
        elif self.percentage >= 90:
            return "A-"
        elif self.percentage >= 87:
            return "B+"
        elif self.percentage >= 83:
            return "B"
        elif self.percentage >= 80:
            return "B-"
        elif self.percentage >= 77:
            return "C+"
        elif self.percentage >= 73:
            return "C"
        elif self.percentage >= 70:
            return "C-"
        elif self.percentage >= 67:
            return "D+"
        elif self.percentage >= 63:
            return "D"
        elif self.percentage >= 60:
            return "D-"
        else:
            return "F"
