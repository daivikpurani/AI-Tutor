"""
Base model class with common fields.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from app.db.session import Base as SQLAlchemyBase


class Base(SQLAlchemyBase):
    """
    Base model class with common fields and functionality.
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        return cls.__name__.lower()
    
    def dict(self):
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
