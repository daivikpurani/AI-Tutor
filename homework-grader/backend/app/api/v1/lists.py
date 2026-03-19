"""
List endpoints for demo: sections, assignments, students.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Section, Assignment, Student

router = APIRouter()


@router.get("/sections")
async def list_sections(db: Session = Depends(get_db)):
    """List all sections for dropdowns (e.g. material upload)."""
    sections = db.query(Section).filter(Section.is_active == True).order_by(Section.id).all()
    return {
        "sections": [
            {
                "id": s.id,
                "section_number": s.section_number,
                "semester": s.semester,
                "year": s.year,
                "section_code": s.section_code,
                "course_code": s.course.course_code if s.course else None,
                "course_name": s.course.course_name if s.course else None,
            }
            for s in sections
        ]
    }


@router.get("/assignments")
async def list_assignments(db: Session = Depends(get_db)):
    """List all published assignments for dropdowns (e.g. submission upload)."""
    assignments = (
        db.query(Assignment)
        .filter(Assignment.is_active == True, Assignment.is_published == True)
        .order_by(Assignment.id)
        .all()
    )
    return {
        "assignments": [
            {
                "id": a.id,
                "title": a.title,
                "section_id": a.section_id,
                "section_code": a.section.section_code if a.section else None,
                "max_score": a.max_score,
                "due_date": a.due_date.isoformat() if a.due_date else None,
            }
            for a in assignments
        ]
    }


@router.get("/students")
async def list_students(db: Session = Depends(get_db)):
    """List all active students for dropdowns (e.g. submission upload)."""
    students = db.query(Student).filter(Student.is_active == True).order_by(Student.id).all()
    return {
        "students": [
            {
                "id": s.id,
                "first_name": s.first_name,
                "last_name": s.last_name,
                "full_name": s.full_name,
                "email": s.email,
                "sfsu_id": s.sfsu_id,
            }
            for s in students
        ]
    }
