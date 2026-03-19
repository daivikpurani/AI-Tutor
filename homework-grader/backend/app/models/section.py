"""
Section model representing a specific offering of a course.

A Section is a particular instance of a course taught by a specific professor
at a specific time. For example:
- CSC 895-01 (Spring 2026, Prof. Smith, MW 2:00-3:30)
- CSC 895-02 (Spring 2026, Prof. Jones, TTh 4:00-5:30)

Each section has its own:
- Professor assignment
- Schedule (days and times)
- Students (enrollments)
- Materials (with separate vector store)
- Assignments
- Rubrics
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Time, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class Section(Base):
    """
    Section model representing a specific course offering.
    
    This is the central entity that connects everything:
    - One course can have many sections
    - Each section is taught by one faculty member
    - Students enroll in specific sections
    - Materials and assignments belong to sections
    - Each section has its own vector store for RAG
    """
    
    __tablename__ = "sections"
    
    # Course Association
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    
    # Faculty Assignment
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False, index=True)
    
    # Section Identification
    section_number = Column(String(10), nullable=False)  # e.g., "01", "02", "A", "B"
    
    # Semester Information
    semester = Column(String(20), nullable=False)  # e.g., "Spring", "Fall", "Summer"
    year = Column(Integer, nullable=False)  # e.g., 2026
    
    # Schedule Information
    days_of_week = Column(String(20), nullable=True)  # e.g., "MW", "TTh", "MWF"
    start_time = Column(Time, nullable=True)  # e.g., 14:00:00
    end_time = Column(Time, nullable=True)  # e.g., 15:30:00
    location = Column(String(100), nullable=True)  # e.g., "Thornton Hall 101"
    
    # Capacity
    max_students = Column(Integer, nullable=True, default=30)
    
    # Vector Store for Section-Specific Knowledge Core
    # Each section maintains its own vector store collection for RAG
    vector_store_collection_id = Column(String(255), nullable=True, unique=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="sections")
    faculty = relationship("Faculty", back_populates="sections")
    enrollments = relationship("Enrollment", back_populates="section", cascade="all, delete-orphan")
    materials = relationship("Material", back_populates="section", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="section", cascade="all, delete-orphan")
    rubrics = relationship("Rubric", back_populates="section", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Section(id={self.id}, course_id={self.course_id}, section={self.section_number}, semester={self.semester} {self.year})>"
    
    @property
    def section_code(self):
        """Get full section code (e.g., 'CSC 895-01')."""
        if self.course:
            return f"{self.course.course_code}-{self.section_number}"
        return f"Section {self.section_number}"
    
    @property
    def enrolled_count(self):
        """Get number of enrolled students."""
        return len(self.enrollments)
    
    @property
    def is_full(self):
        """Check if section is at capacity."""
        if self.max_students:
            return self.enrolled_count >= self.max_students
        return False
    
    @property
    def schedule_display(self):
        """Get human-readable schedule."""
        if self.days_of_week and self.start_time and self.end_time:
            return f"{self.days_of_week} {self.start_time.strftime('%I:%M %p')}-{self.end_time.strftime('%I:%M %p')}"
        return "Schedule TBA"
