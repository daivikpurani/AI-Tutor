"""
Database models package.
Import all models here to ensure proper registration with SQLAlchemy.
"""

# Import base first
from app.models.base import Base

# Import models in dependency order
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.course import Course
from app.models.section import Section
from app.models.enrollment import Enrollment
from app.models.rubric import Rubric
from app.models.assignment import Assignment
from app.models.material import Material
from app.models.submission import Submission
from app.models.grade import Grade
from app.models.feedback import Feedback
from app.models.test_feedback import TestFeedback


__all__ = [
    "Base",
    "Faculty",
    "Student",
    "Course",
    "Section",
    "Enrollment",
    "Rubric",
    "Assignment",
    "Material",
    "Submission",
    "Grade",
    "Feedback",
    "TestFeedback",
]
