"""
TestFeedback model - stores latest AI test feedback per (assignment_id, student_id).
Overwritten on each test; copied to submission.pre_submission_feedback when student submits.
"""

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class TestFeedback(Base):
    """
    Latest AI test feedback before submit.
    One row per (assignment_id, student_id) - overwritten on each test.
    """
    
    __tablename__ = "test_feedback"
    __table_args__ = (UniqueConstraint("assignment_id", "student_id", name="uq_test_feedback_assignment_student"),)
    
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    feedback_json = Column(Text, nullable=False)  # JSON: score, summary, strengths, weaknesses, suggestions
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    assignment = relationship("Assignment", backref="test_feedbacks")
    student = relationship("Student", backref="test_feedbacks")
    
    def __repr__(self):
        return f"<TestFeedback(assignment_id={self.assignment_id}, student_id={self.student_id})>"
