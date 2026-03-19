"""
Enrollment model representing student registration in course sections.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Enrollment(Base):
    """
    Enrollment model linking students to specific course sections.
    
    Students enroll in sections, not courses.
    """
    
    __tablename__ = "enrollments"
    
    # Foreign Keys
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False, index=True)
    
    # Enrollment Metadata
    enrollment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, dropped, completed
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    section = relationship("Section", back_populates="enrollments")
    
    def __repr__(self):
        return f"<Enrollment(id={self.id}, student_id={self.student_id}, section_id={self.section_id}, status={self.status})>"
