"""
Submissions API endpoints for student homework submissions.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from loguru import logger

from app.db.session import get_db
from app.models import Submission, Assignment, Student, Section, TestFeedback
from app.models.submission import SubmissionStatus
from app.utils.file_handler import file_handler


router = APIRouter()


@router.post("/upload")
async def upload_submission(
    file: UploadFile = File(...),
    assignment_id: int = Form(...),
    student_id: int = Form(...),
    submission_text: Optional[str] = Form(None),
    pre_submission_feedback: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload student homework submission.
    
    This endpoint:
    1. Validates assignment and student
    2. Saves submission file to disk
    3. Creates submission record
    4. (Grading happens in separate endpoint)
    """
    try:
        logger.info(f"Uploading submission for assignment {assignment_id}, student {student_id}")
        
        # Validate assignment
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")
        
        # Validate student
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        # Check if student is enrolled in the section
        section = db.query(Section).filter(Section.id == assignment.section_id).first()
        is_enrolled = any(e.student_id == student_id for e in section.enrollments)
        if not is_enrolled:
            raise HTTPException(
                status_code=403,
                detail=f"Student {student_id} is not enrolled in section {assignment.section_id}"
            )
        
        # Check deadline (optional - for now just warn)
        if assignment.is_overdue():
            logger.warning(f"Assignment {assignment_id} is overdue")
            if not assignment.late_submission_allowed:
                raise HTTPException(
                    status_code=400,
                    detail="Assignment is past due date and late submissions are not allowed"
                )
        
        # Count existing submissions for attempt number
        existing_submissions = db.query(Submission).filter(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student_id
        ).count()
        attempt_number = existing_submissions + 1
        
        # Initialize submission data
        file_path = None
        saved_filename = None
        file_size = None
        
        # Save file if provided
        if file:
            # Validate file type
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files are supported")
            
            # Read file content
            file_content = await file.read()
            
            # Save file
            file_path, saved_filename, file_size = file_handler.save_submission(
                file_content=file_content,
                filename=file.filename,
                assignment_id=assignment_id,
                student_id=student_id
            )
        
        # Copy last test feedback if not provided in form (fetch from TestFeedback)
        if pre_submission_feedback is None:
            tf = db.query(TestFeedback).filter(
                TestFeedback.assignment_id == assignment_id,
                TestFeedback.student_id == student_id
            ).first()
            if tf:
                pre_submission_feedback = tf.feedback_json
                db.delete(tf)
                db.flush()
        
        # Create submission record
        submission = Submission(
            assignment_id=assignment_id,
            student_id=student_id,
            submission_text=submission_text,
            file_name=saved_filename,
            file_path=file_path,
            file_size=file_size,
            submission_date=datetime.utcnow(),
            attempt_number=attempt_number,
            status=SubmissionStatus.SUBMITTED,
            pre_submission_feedback=pre_submission_feedback
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        logger.info(f"Submission uploaded successfully: {submission.id}")
        
        return {
            "success": True,
            "message": "Submission uploaded successfully",
            "submission": {
                "id": submission.id,
                "assignment_id": assignment_id,
                "student_id": student_id,
                "file_name": saved_filename,
                "submission_date": submission.submission_date,
                "attempt_number": attempt_number,
                "status": submission.status.value,
                "file_size": file_size
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading submission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading submission: {str(e)}")


@router.get("/assignment/{assignment_id}")
async def list_submissions(assignment_id: int, db: Session = Depends(get_db)):
    """
    List all submissions for an assignment.
    """
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")
    
    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).all()
    
    return {
        "assignment_id": assignment_id,
        "assignment_title": assignment.title,
        "total_submissions": len(submissions),
            "submissions": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "student_name": f"{s.student.first_name} {s.student.last_name}" if s.student else None,
                "file_name": s.file_name,
                "submission_date": s.submission_date,
                "attempt_number": s.attempt_number,
                "status": s.status.value,
                "pre_submission_feedback": s.pre_submission_feedback,
                "has_grade_released": s.grade.is_released if s.grade else False,
            }
            for s in submissions
        ]
    }


@router.get("/my/{student_id}")
async def list_my_submissions(student_id: int, db: Session = Depends(get_db)):
    """List submissions for a student (SV)."""
    submissions = db.query(Submission).filter(
        Submission.student_id == student_id
    ).order_by(Submission.submission_date.desc()).all()
    
    return {
        "submissions": [
            {
                "id": s.id,
                "assignment_id": s.assignment_id,
                "assignment_title": s.assignment.title if s.assignment else None,
                "section_code": s.assignment.section.section_code if s.assignment and s.assignment.section else None,
                "file_name": s.file_name,
                "submission_date": s.submission_date,
                "status": s.status.value,
                "pre_submission_feedback": s.pre_submission_feedback,
                "grade_released": s.grade.is_released if s.grade else False,
                "professor_feedback": s.grade.professor_feedback if s.grade and s.grade.is_released else None,
                "score": s.grade.score if s.grade and s.grade.is_released else None,
                "max_score": s.grade.max_score if s.grade and s.grade.is_released else None,
            }
            for s in submissions
        ]
    }


@router.get("/{submission_id}")
async def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """Get submission details (includes pre_submission_feedback, grade if released)."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    grade_data = None
    if submission.grade:
        grade_data = {
            "score": submission.grade.score,
            "max_score": submission.grade.max_score,
            "percentage": submission.grade.percentage,
            "professor_feedback": submission.grade.professor_feedback,
            "is_released": submission.grade.is_released,
        }
    
    return {
        "id": submission.id,
        "assignment_id": submission.assignment_id,
        "assignment_title": submission.assignment.title if submission.assignment else None,
        "student_id": submission.student_id,
        "student_name": f"{submission.student.first_name} {submission.student.last_name}" if submission.student else None,
        "submission_text": submission.submission_text,
        "file_name": submission.file_name,
        "file_path": submission.file_path,
        "file_size": submission.file_size,
        "submission_date": submission.submission_date,
        "attempt_number": submission.attempt_number,
        "status": submission.status.value,
        "pre_submission_feedback": submission.pre_submission_feedback,
        "grade": grade_data,
        "created_at": submission.created_at,
    }
