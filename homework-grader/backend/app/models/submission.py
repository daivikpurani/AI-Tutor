"""
Submission model representing student homework submissions.
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class SubmissionStatus(str, enum.Enum):
    """Submission status enumeration."""
    SUBMITTED = "submitted"
    GRADING = "grading"
    GRADED = "graded"
    RETURNED = "returned"


class Submission(Base):
    """
    Student Submission model.
    """
    
    __tablename__ = "submissions"
    
    # Submission Information
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Submission Content
    submission_text = Column(Text, nullable=True)  # Text-based submissions
    file_name = Column(String(255), nullable=True)  # Uploaded file name
    file_path = Column(String(500), nullable=True)  # Path to stored file
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Submission Metadata
    submission_date = Column(DateTime, nullable=False)
    attempt_number = Column(Integer, default=1, nullable=False)
    
    # Status
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.SUBMITTED, nullable=False)
    
    # Last AI test feedback before submit (shown to professor when grading)
    pre_submission_feedback = Column(Text, nullable=True)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")
    grade = relationship("Grade", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Submission(id={self.id}, assignment_id={self.assignment_id}, student_id={self.student_id}, status={self.status})>"
