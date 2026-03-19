"""
Material model representing course materials for specific sections.

Each section maintains its own set of materials with a dedicated
vector store collection for RAG-based grading.
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class MaterialType(str, enum.Enum):
    """Material type enumeration."""
    PDF = "pdf"
    TEXTBOOK = "textbook"
    NOTES = "notes"
    SLIDES = "slides"
    DOCUMENT = "document"
    CODE = "code"
    OTHER = "other"


class Material(Base):
    """
    Course Material model.
    
    Materials are section-specific. Each section has its own knowledge base
    stored in a separate vector store collection.
    """
    
    __tablename__ = "materials"
    
    # Material Information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    material_type = Column(Enum(MaterialType), default=MaterialType.OTHER, nullable=False)
    
    # File Information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Path to stored file
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    
    # Section Association (changed from course_id)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False, index=True)
    
    # Vector Store Reference
    # Documents from this material are stored in the section's vector store collection
    vector_store_document_ids = Column(Text, nullable=True)  # JSON array of document IDs
    is_indexed = Column(Integer, default=0, nullable=False)  # Boolean: 0 = not indexed, 1 = indexed
    chunk_count = Column(Integer, default=0, nullable=False)  # Number of chunks created
    
    # Relationships
    section = relationship("Section", back_populates="materials")
    
    def __repr__(self):
        return f"<Material(id={self.id}, title={self.title}, type={self.material_type}, section_id={self.section_id})>"
