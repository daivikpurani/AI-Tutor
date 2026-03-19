"""
Grading API endpoints.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from loguru import logger

from app.db.session import get_db
from app.models import Grade, Submission, Assignment
from app.models.submission import SubmissionStatus
from app.services.grading import grading_service


router = APIRouter()


# Request schema
class GradeSubmissionRequest(BaseModel):
    """Request to grade a submission."""
    submission_id: int
    use_rag: bool = True
    custom_instructions: Optional[str] = None


class ReleaseGradeRequest(BaseModel):
    """Request for professor to release grade to student."""
    submission_id: int
    score: float
    professor_feedback: str


@router.post("/grade")
async def grade_submission(
    request: GradeSubmissionRequest,
    db: Session = Depends(get_db)
):
    """
    Grade a student submission using AI.
    
    This endpoint:
    1. Retrieves relevant context from course materials (RAG)
    2. Gets assignment rubric and grading instructions
    3. Sends to Gemini for grading
    4. Saves grade and feedback to database
    """
    try:
        logger.info(f"Grading request for submission {request.submission_id}")
        
        # Grade the submission
        result = grading_service.grade_submission(
            submission_id=request.submission_id,
            db=db,
            use_rag=request.use_rag,
            custom_instructions=request.custom_instructions
        )
        
        return {
            "success": True,
            "message": "Submission graded successfully",
            "result": result
        }
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error grading submission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error grading submission: {str(e)}")


@router.post("/test")
async def test_solution(
    file: UploadFile = File(...),
    assignment_id: int = Form(...),
    student_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Test-grade solution without submitting. Overwrites test_feedback for (assignment_id, student_id).
    Returns AI feedback. Does NOT create a submission.
    """
    try:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        file_content = await file.read()
        result = grading_service.grade_test_only(
            assignment_id=assignment_id,
            student_id=student_id,
            file_content=file_content,
            filename=file.filename,
            db=db,
        )
        return {"success": True, "feedback": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Test grading failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/release")
async def release_grade(request: ReleaseGradeRequest, db: Session = Depends(get_db)):
    """
    Professor releases grade and feedback to student.
    """
    submission = db.query(Submission).filter(Submission.id == request.submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    max_score = assignment.max_score
    percentage = (request.score / max_score * 100) if max_score > 0 else 0
    
    grade = db.query(Grade).filter(Grade.submission_id == submission.id).first()
    if grade:
        grade.score = request.score
        grade.max_score = max_score
        grade.percentage = percentage
        grade.professor_feedback = request.professor_feedback
        grade.is_released = True
    else:
        grade = Grade(
            submission_id=submission.id,
            score=request.score,
            max_score=max_score,
            percentage=percentage,
            professor_feedback=request.professor_feedback,
            is_released=True,
        )
        db.add(grade)
    
    submission.status = SubmissionStatus.RETURNED
    db.commit()
    db.refresh(grade)
    return {
        "success": True,
        "message": "Grade released to student",
        "grade": {
            "id": grade.id,
            "submission_id": submission.id,
            "score": grade.score,
            "max_score": grade.max_score,
            "percentage": grade.percentage,
            "professor_feedback": grade.professor_feedback,
            "is_released": grade.is_released,
        },
    }


@router.get("/grade/{submission_id}")
async def get_grade(submission_id: int, db: Session = Depends(get_db)):
    """Get grade for a submission."""
    grade = db.query(Grade).filter(Grade.submission_id == submission_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    return {
        "id": grade.id,
        "submission_id": grade.submission_id,
        "score": grade.score,
        "max_score": grade.max_score,
        "percentage": grade.percentage,
        "letter_grade": grade.letter_grade,
        "professor_feedback": grade.professor_feedback,
        "is_released": grade.is_released,
        "summary": grade.summary,
        "strengths": grade.strengths,
        "weaknesses": grade.weaknesses,
        "suggestions": grade.suggestions,
        "ai_confidence": grade.ai_confidence,
        "created_at": grade.created_at
    }
