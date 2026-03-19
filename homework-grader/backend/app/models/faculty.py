"""
Faculty model representing professors and instructors.
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class Faculty(Base):
    """
    Faculty/Professor model.
    """
    
    __tablename__ = "faculty"
    
    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # SFSU Information
    sfsu_id = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(100), default="Computer Science", nullable=False)
    
    # Account Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    sections = relationship("Section", back_populates="faculty", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Faculty(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})>"
    
    @property
    def full_name(self):
        """Get full name."""
        return f"{self.first_name} {self.last_name}"
