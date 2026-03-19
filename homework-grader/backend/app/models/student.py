"""
Student model representing students enrolled in courses.
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class Student(Base):
    """
    Student model.
    """
    
    __tablename__ = "students"
    
    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # SFSU Information
    sfsu_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Account Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})>"
    
    @property
    def full_name(self):
        """Get full name."""
        return f"{self.first_name} {self.last_name}"
