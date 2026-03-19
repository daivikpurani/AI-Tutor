"""
Course model representing CS courses at SF State.

This is the course catalog entry (e.g., CSC 895, CSC 667).
Actual course offerings are represented by Section model.
"""

from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class Course(Base):
    """
    Course model for CS Department course catalog.
    
    Represents the general course information (catalog entry).
    Specific offerings of this course are represented by Section model.
    """
    
    __tablename__ = "courses"
    
    # Course Information
    course_code = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "CSC 895"
    course_name = Column(String(255), nullable=False)  # e.g., "Advanced Topics in AI"
    description = Column(Text, nullable=True)
    department = Column(String(100), default="Computer Science", nullable=False)
    
    # Prerequisites (optional - can be added later)
    prerequisites = Column(Text, nullable=True)  # e.g., "CSC 600 or equivalent"
    
    # Course Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(id={self.id}, code={self.course_code}, name={self.course_name})>"
    
    @property
    def active_sections_count(self):
        """Get count of active sections."""
        return sum(1 for section in self.sections if section.is_active)
