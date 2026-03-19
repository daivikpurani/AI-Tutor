"""
Assignments API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db
from app.models import Assignment, Section, Enrollment
from app.services.document_processor.pdf_extractor import pdf_extractor


router = APIRouter()


class AssignmentCreate(BaseModel):
    section_id: int
    title: str
    description: Optional[str] = None
    questions_content: Optional[str] = None
    grading_instructions: Optional[str] = None
    max_score: float = 100.0


@router.post("/extract-questions-pdf")
async def extract_questions_from_pdf(file: UploadFile = File(...)):
    """
    Extract text from a homework questions PDF. Returns extracted text for use in questions_content.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    try:
        content = await file.read()
        result = pdf_extractor.extract_text_from_bytes(content)
        return {"text": result["full_text"], "num_pages": result["num_pages"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract PDF text: {str(e)}")


@router.post("/")
async def create_assignment(
    body: AssignmentCreate,
    db: Session = Depends(get_db)
):
    """Create assignment. Visible to enrolled students immediately."""
    section = db.query(Section).filter(Section.id == body.section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    now = datetime.utcnow()
    assignment = Assignment(
        section_id=body.section_id,
        title=body.title,
        description=body.description,
        questions_content=body.questions_content,
        grading_instructions=body.grading_instructions,
        max_score=body.max_score,
        release_at=now,
        due_date=now + timedelta(days=14),
        late_submission_allowed=False,
        late_penalty_percent=0.0,
        is_published=True,
        is_active=True,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {
        "success": True,
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "section_id": assignment.section_id,
            "release_at": assignment.release_at.isoformat(),
            "due_date": assignment.due_date.isoformat(),
        },
    }


@router.get("/section/{section_id}")
async def list_assignments_for_section(section_id: int, db: Session = Depends(get_db)):
    """List assignments for a section (PV)."""
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    assignments = db.query(Assignment).filter(
        Assignment.section_id == section_id,
        Assignment.is_active == True
    ).order_by(Assignment.release_at.desc()).all()
    
    return {
        "assignments": [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "questions_content": a.questions_content,
                "release_at": a.release_at.isoformat() if a.release_at else None,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "max_score": a.max_score,
                "submission_count": len(a.submissions),
            }
            for a in assignments
        ]
    }


@router.get("/student/{student_id}")
async def list_released_assignments_for_student(student_id: int, db: Session = Depends(get_db)):
    """List assignments visible to a student: enrolled sections (SV)."""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.status == "active"
    ).all()
    section_ids = [e.section_id for e in enrollments]
    if not section_ids:
        return {"assignments": []}

    assignments = db.query(Assignment).filter(
        Assignment.section_id.in_(section_ids),
        Assignment.is_active == True,
        Assignment.is_published == True,
    ).order_by(Assignment.id.desc()).all()
    
    return {
        "assignments": [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "questions_content": a.questions_content,
                "section_id": a.section_id,
                "section_code": a.section.section_code if a.section else None,
                "release_at": a.release_at.isoformat() if a.release_at else None,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "max_score": a.max_score,
                "late_submission_allowed": a.late_submission_allowed,
            }
            for a in assignments
        ]
    }


@router.get("/{assignment_id}")
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Get assignment detail."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "questions_content": assignment.questions_content,
        "section_id": assignment.section_id,
        "section_code": assignment.section.section_code if assignment.section else None,
        "release_at": assignment.release_at.isoformat() if assignment.release_at else None,
        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
        "max_score": assignment.max_score,
        "grading_instructions": assignment.grading_instructions,
        "late_submission_allowed": assignment.late_submission_allowed,
    }
