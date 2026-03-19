"""
Main grading service that orchestrates the grading process.
"""

from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from app.models import Submission, Assignment, Section, Grade, Rubric, TestFeedback
from app.models.submission import SubmissionStatus
from app.services.llm import gemini_client
from app.services.rag import rag_service
from app.services.document_processor import document_processor


class GradingService:
    """
    Main grading service that orchestrates the entire grading process.
    
    Process:
    1. Get submission and assignment details
    2. Retrieve relevant context from section's vector store (RAG)
    3. Get rubric if available
    4. Send to Gemini for grading
    5. Parse and save results
    """
    
    def __init__(self):
        self.gemini = gemini_client
        self.rag = rag_service
        self.doc_processor = document_processor
    
    def grade_submission(
        self,
        submission_id: int,
        db: Session,
        use_rag: bool = True,
        custom_instructions: Optional[str] = None
    ) -> Dict:
        """
        Grade a student submission.
        
        Args:
            submission_id: ID of submission to grade
            db: Database session
            use_rag: Whether to use RAG for context
            custom_instructions: Additional grading instructions
            
        Returns:
            Grading result dictionary
        """
        try:
            logger.info(f"Starting grading for submission {submission_id}")
            
            # 1. Get submission
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            if not submission:
                raise ValueError(f"Submission {submission_id} not found")
            
            # Update status
            submission.status = SubmissionStatus.GRADING
            db.commit()
            
            # 2. Get assignment and section
            assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
            if not assignment:
                raise ValueError(f"Assignment {submission.assignment_id} not found")
            
            section = db.query(Section).filter(Section.id == assignment.section_id).first()
            if not section:
                raise ValueError(f"Section {assignment.section_id} not found")
            
            # 3. Get submission text
            submission_text = self._get_submission_text(submission)
            if not submission_text:
                raise ValueError("Submission has no content to grade")
            
            # 4. Retrieve context from RAG (if enabled and collection exists)
            context_chunks = []
            if use_rag and section.vector_store_collection_id:
                rag_context = self.rag.build_grading_context(
                    submission_text=submission_text,
                    collection_name=section.vector_store_collection_id,
                    n_chunks=5
                )
                context_chunks = rag_context.get('chunks', [])
                logger.info(f"Retrieved {len(context_chunks)} context chunks for grading")
            else:
                logger.info("Grading without RAG context (no materials uploaded)")
            
            # 5. Get rubric if assigned
            rubric = None
            rubric_criteria = None
            if assignment.rubric_id:
                rubric = db.query(Rubric).filter(Rubric.id == assignment.rubric_id).first()
                if rubric:
                    rubric_criteria = rubric.criteria
            
            # 6. Get grading instructions (user-provided only; no hardcoded fallback)
            grading_instructions = (assignment.grading_instructions or "").strip()
            if not grading_instructions:
                grading_instructions = (
                    "Grade based on the provided course materials and homework context. "
                    "Provide constructive feedback on correctness, completeness, and clarity."
                )
            if custom_instructions:
                grading_instructions += f"\n\nAdditional Instructions: {custom_instructions}"
            
            # 7. Grade with Gemini
            grading_result = self.gemini.grade_submission(
                submission_text=submission_text,
                context_chunks=context_chunks,
                grading_instructions=grading_instructions,
                rubric_criteria=rubric_criteria,
                max_score=assignment.max_score
            )
            
            # 8. Save grade to database
            grade = Grade(
                submission_id=submission.id,
                score=grading_result['score'],
                max_score=grading_result['max_score'],
                percentage=grading_result['percentage'],
                summary=grading_result['summary'],
                strengths=grading_result['strengths'],
                weaknesses=grading_result['weaknesses'],
                suggestions=grading_result['suggestions'],
                ai_confidence=grading_result.get('ai_confidence', 0.85),
                grading_criteria=rubric_criteria
            )
            
            db.add(grade)
            
            # Update submission status
            submission.status = SubmissionStatus.GRADED
            
            db.commit()
            db.refresh(grade)
            
            logger.info(f"Grade saved: {grade.id} (Score: {grade.score}/{grade.max_score})")
            
            return {
                "success": True,
                "grade_id": grade.id,
                "submission_id": submission.id,
                "score": grade.score,
                "max_score": grade.max_score,
                "percentage": grade.percentage,
                "letter_grade": grade.letter_grade,
                "summary": grade.summary,
                "strengths": grade.strengths,
                "weaknesses": grade.weaknesses,
                "suggestions": grade.suggestions,
                "context_used": len(context_chunks),
                "rubric_used": rubric is not None
            }
        
        except Exception as e:
            logger.error(f"Error grading submission: {e}", exc_info=True)
            
            # Reset submission status on error
            if submission:
                submission.status = SubmissionStatus.SUBMITTED
                db.commit()
            
            raise
    
    def _get_submission_text(self, submission: Submission) -> str:
        """
        Get submission text from database or extract from file.
        
        Args:
            submission: Submission object
            
        Returns:
            Submission text content
        """
        # If submission has text field, use it
        if submission.submission_text:
            return submission.submission_text
        
        # If submission has file, extract text from it
        if submission.file_path:
            try:
                result = self.doc_processor.process_pdf(
                    pdf_path=submission.file_path,
                    metadata={"submission_id": submission.id}
                )
                return result['full_text']
            except Exception as e:
                logger.error(f"Error extracting text from submission file: {e}")
                raise
        
        return ""
    
    def grade_test_only(
        self,
        assignment_id: int,
        student_id: int,
        file_content: bytes,
        filename: str,
        db: Session,
    ) -> Dict:
        """
        Test-grade without creating submission. Overwrites test_feedback for (assignment_id, student_id).
        """
        import json
        
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")
        
        section = db.query(Section).filter(Section.id == assignment.section_id).first()
        if not section:
            raise ValueError(f"Section {assignment.section_id} not found")
        
        # Extract text from PDF
        result = self.doc_processor.process_pdf_bytes(
            pdf_bytes=file_content,
            filename=filename,
            metadata={"assignment_id": assignment_id, "student_id": student_id}
        )
        submission_text = result.get("full_text", "")
        if not submission_text:
            raise ValueError("Could not extract text from PDF")
        
        # RAG context
        context_chunks = []
        if section.vector_store_collection_id:
            rag_context = self.rag.build_grading_context(
                submission_text=submission_text,
                collection_name=section.vector_store_collection_id,
                n_chunks=5
            )
            context_chunks = rag_context.get("chunks", [])
        
        rubric = None
        rubric_criteria = None
        if assignment.rubric_id:
            rubric = db.query(Rubric).filter(Rubric.id == assignment.rubric_id).first()
            if rubric:
                rubric_criteria = rubric.criteria
        
        grading_instructions = (assignment.grading_instructions or "").strip()
        if not grading_instructions:
            grading_instructions = (
                "Grade based on the provided materials and homework context. "
                "Provide constructive feedback."
            )
        
        grading_result = self.gemini.grade_submission(
            submission_text=submission_text,
            context_chunks=context_chunks,
            grading_instructions=grading_instructions,
            rubric_criteria=rubric_criteria,
            max_score=assignment.max_score
        )
        
        feedback_dict = {
            "score": grading_result["score"],
            "max_score": grading_result["max_score"],
            "percentage": grading_result["percentage"],
            "summary": grading_result["summary"],
            "strengths": grading_result["strengths"],
            "weaknesses": grading_result["weaknesses"],
            "suggestions": grading_result["suggestions"],
        }
        feedback_json = json.dumps(feedback_dict)
        
        # Upsert test_feedback
        existing = db.query(TestFeedback).filter(
            TestFeedback.assignment_id == assignment_id,
            TestFeedback.student_id == student_id
        ).first()
        if existing:
            existing.feedback_json = feedback_json
            existing.created_at = datetime.utcnow()
        else:
            tf = TestFeedback(
                assignment_id=assignment_id,
                student_id=student_id,
                feedback_json=feedback_json
            )
            db.add(tf)
        db.commit()
        
        return feedback_dict


# Singleton instance
grading_service = GradingService()
