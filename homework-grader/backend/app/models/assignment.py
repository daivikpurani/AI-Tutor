"""
Assignment model representing homework/assignments for course sections.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class Assignment(Base):
    """
    Assignment/Homework model.
    
    Assignments belong to specific sections and can optionally
    reference a rubric for grading.
    """
    
    __tablename__ = "assignments"
    
    # Assignment Information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    questions_content = Column(Text, nullable=True)  # Homework questions (HTML/Markdown), visible to students
    
    # Section Association
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False, index=True)
    
    # Rubric Association (Optional)
    # If set, this rubric will be used for grading
    # If null, use grading_instructions (natural language)
    rubric_id = Column(Integer, ForeignKey("rubrics.id"), nullable=True)
    
    # Grading Instructions (Natural Language fallback)
    # Used when no rubric is specified, or as additional context
    grading_instructions = Column(Text, nullable=True)
    max_score = Column(Float, default=100.0, nullable=False)
    
    # Deadlines & Release
    release_at = Column(DateTime, nullable=False)  # When assignment becomes visible to students
    due_date = Column(DateTime, nullable=False)
    late_submission_allowed = Column(Boolean, default=False, nullable=False)
    late_penalty_percent = Column(Float, default=0.0, nullable=False)  # Penalty per day
    
    # Assignment Files (Optional - for providing starter code, etc.)
    attachment_file_name = Column(String(255), nullable=True)
    attachment_file_path = Column(String(500), nullable=True)
    
    # Status
    is_published = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    section = relationship("Section", back_populates="assignments")
    rubric = relationship("Rubric", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assignment(id={self.id}, title={self.title}, section_id={self.section_id})>"
    
    def is_overdue(self):
        """Check if assignment is past due date."""
        return datetime.utcnow() > self.due_date
    
    @property
    def submission_count(self):
        """Get number of submissions."""
        return len(self.submissions)
    
    @property
    def graded_count(self):
        """Get number of graded submissions."""
        return sum(1 for sub in self.submissions if sub.status == "graded")
