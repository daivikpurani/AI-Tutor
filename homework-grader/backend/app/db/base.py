"""
Base database configuration.
Imports all models to ensure they are registered with SQLAlchemy.
"""

from app.db.session import Base

# Import all models here to ensure they are registered
# This allows Base.metadata.create_all() to work properly
# from app.models.course import Course
# from app.models.faculty import Faculty
# from app.models.student import Student
# from app.models.assignment import Assignment
# from app.models.submission import Submission
# from app.models.grade import Grade
# from app.models.material import Material
# from app.models.feedback import Feedback


__all__ = ["Base"]
