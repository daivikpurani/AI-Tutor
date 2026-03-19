"""
Gemini LLM client for grading and content generation.
"""

from typing import Dict, List, Optional
import google.generativeai as genai
from loguru import logger

from app.config import settings


class GeminiClient:
    """
    Client for interacting with Gemini API for grading.
    """
    
    def __init__(self):
        """Initialize Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"Gemini client initialized with model: {settings.gemini_model}")
    
    def grade_submission(
        self,
        submission_text: str,
        context_chunks: List[str],
        grading_instructions: str,
        rubric_criteria: Optional[Dict] = None,
        max_score: float = 100.0
    ) -> Dict:
        """
        Grade a student submission using Gemini.
        
        Args:
            submission_text: Student's submission content
            context_chunks: Relevant chunks from course materials (RAG)
            grading_instructions: Natural language grading instructions
            rubric_criteria: Optional structured rubric
            max_score: Maximum possible score
            
        Returns:
            Dictionary with grade and feedback
        """
        try:
            # Build the grading prompt
            prompt = self._build_grading_prompt(
                submission_text=submission_text,
                context_chunks=context_chunks,
                grading_instructions=grading_instructions,
                rubric_criteria=rubric_criteria,
                max_score=max_score
            )
            
            logger.info("Sending grading request to Gemini...")
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.llm_temperature,
                    max_output_tokens=settings.llm_max_tokens,
                )
            )
            
            # Parse response
            result = self._parse_grading_response(response.text, max_score)
            
            logger.info(f"Grading complete: {result['score']}/{max_score}")
            return result
        
        except Exception as e:
            logger.error(f"Error grading with Gemini: {e}")
            raise
    
    def _build_grading_prompt(
        self,
        submission_text: str,
        context_chunks: List[str],
        grading_instructions: str,
        rubric_criteria: Optional[Dict],
        max_score: float
    ) -> str:
        """Build the grading prompt for Gemini."""
        
        # Start with role and context
        prompt_parts = [
            "You are an experienced professor grading student homework.",
            "",
            "# COURSE MATERIALS (Context for Grading)",
            "Use the following course materials as reference for grading:",
            ""
        ]
        
        # Add context chunks
        for i, chunk in enumerate(context_chunks[:10], 1):  # Limit to top 10 chunks
            prompt_parts.append(f"## Reference Material {i}")
            prompt_parts.append(chunk)
            prompt_parts.append("")
        
        # Add rubric if available
        if rubric_criteria and isinstance(rubric_criteria, dict):
            prompt_parts.append("# GRADING RUBRIC")
            prompt_parts.append(f"Maximum Score: {max_score}")
            prompt_parts.append("")
            
            categories = rubric_criteria.get("categories", [])
            for category in categories:
                name = category.get("name", "")
                weight = category.get("weight", 0)
                description = category.get("description", "")
                criteria = category.get("criteria", [])
                
                prompt_parts.append(f"## {name} ({weight}%)")
                prompt_parts.append(description)
                if criteria:
                    for criterion in criteria:
                        prompt_parts.append(f"  - {criterion}")
                prompt_parts.append("")
        
        # Add grading instructions
        prompt_parts.append("# GRADING INSTRUCTIONS")
        prompt_parts.append(grading_instructions)
        prompt_parts.append("")
        
        # Add the student submission
        prompt_parts.append("# STUDENT SUBMISSION")
        prompt_parts.append(submission_text)
        prompt_parts.append("")
        
        # Add output format instructions
        prompt_parts.append("# YOUR TASK")
        prompt_parts.append(f"Grade this submission out of {max_score} points.")
        prompt_parts.append("")
        prompt_parts.append("Provide your response in the following format:")
        prompt_parts.append("")
        prompt_parts.append("SCORE: [numerical score]")
        prompt_parts.append("")
        prompt_parts.append("SUMMARY:")
        prompt_parts.append("[2-3 sentence overall assessment]")
        prompt_parts.append("")
        prompt_parts.append("STRENGTHS:")
        prompt_parts.append("[What the student did well]")
        prompt_parts.append("")
        prompt_parts.append("WEAKNESSES:")
        prompt_parts.append("[What needs improvement]")
        prompt_parts.append("")
        prompt_parts.append("SUGGESTIONS:")
        prompt_parts.append("[Specific suggestions for improvement]")
        prompt_parts.append("")
        
        if rubric_criteria:
            prompt_parts.append("CATEGORY BREAKDOWN:")
            for category in rubric_criteria.get("categories", []):
                name = category.get("name", "")
                prompt_parts.append(f"- {name}: [score/percentage]")
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def _parse_grading_response(self, response_text: str, max_score: float) -> Dict:
        """
        Parse Gemini's grading response.
        
        Args:
            response_text: Raw response from Gemini
            max_score: Maximum possible score
            
        Returns:
            Structured grading result
        """
        import re
        
        # Extract score
        score_match = re.search(r'SCORE:\s*(\d+\.?\d*)', response_text, re.IGNORECASE)
        score = float(score_match.group(1)) if score_match else 0.0
        
        # Ensure score doesn't exceed max
        score = min(score, max_score)
        
        # Extract sections
        summary_match = re.search(r'SUMMARY:\s*(.*?)(?=STRENGTHS:|$)', response_text, re.IGNORECASE | re.DOTALL)
        strengths_match = re.search(r'STRENGTHS:\s*(.*?)(?=WEAKNESSES:|$)', response_text, re.IGNORECASE | re.DOTALL)
        weaknesses_match = re.search(r'WEAKNESSES:\s*(.*?)(?=SUGGESTIONS:|$)', response_text, re.IGNORECASE | re.DOTALL)
        suggestions_match = re.search(r'SUGGESTIONS:\s*(.*?)(?=CATEGORY BREAKDOWN:|$)', response_text, re.IGNORECASE | re.DOTALL)
        
        summary = summary_match.group(1).strip() if summary_match else ""
        strengths = strengths_match.group(1).strip() if strengths_match else ""
        weaknesses = weaknesses_match.group(1).strip() if weaknesses_match else ""
        suggestions = suggestions_match.group(1).strip() if suggestions_match else ""
        
        # Calculate percentage
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "raw_response": response_text,
            "ai_confidence": 0.85  # Default confidence (can be improved)
        }


# Singleton instance
gemini_client = GeminiClient()
