"""
Dialog Evaluator Module
Implements MathTutorBench methodology (EMNLP 2025) for dialog-based pedagogical evaluation.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class DialogEvaluator:
    """
    Evaluates multi-turn conversations for pedagogical effectiveness.
    
    Based on: MathTutorBench (EMNLP 2025) - "A Benchmark for Measuring Open-ended Pedagogical Capabilities"
    """
    
    def __init__(self):
        # Patterns for learning progression indicators
        self.progression_patterns = [
            r'\b(now that you understand|building on|now we can|next step)\b',
            r'\b(you\'ve learned|you now know|now that you know)\b',
            r'\b(let\'s move on|let\'s explore further|let\'s dive deeper)\b'
        ]
        self.progression_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.progression_patterns]
        
        # Patterns for context retention
        self.context_retention_patterns = [
            r'\b(as we discussed|as mentioned|remember|earlier|previously)\b',
            r'\b(you asked|you mentioned|you said|your question)\b',
            r'\b(going back to|returning to|as we saw)\b'
        ]
        self.context_retention_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.context_retention_patterns]
    
    def evaluate_conversation(
        self,
        conversation: List[Dict[str, Any]],
        student_queries: List[str],
        tutor_responses: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate a multi-turn conversation for dialog-based pedagogical quality.
        
        Args:
            conversation: List of conversation turns with metadata
            student_queries: List of student queries in order
            tutor_responses: List of tutor responses in order
            
        Returns:
            Dictionary with dialog evaluation metrics
        """
        if len(student_queries) != len(tutor_responses):
            raise ValueError("Student queries and tutor responses must have same length")
        
        if len(student_queries) < 2:
            # Single-turn conversation - return basic metrics
            return self._evaluate_single_turn(student_queries[0] if student_queries else "", 
                                             tutor_responses[0] if tutor_responses else "")
        
        metrics = {
            "dialog_coherence": self._score_dialog_coherence(student_queries, tutor_responses),
            "context_retention": self._score_context_retention(student_queries, tutor_responses),
            "learning_progression": self._score_learning_progression(tutor_responses),
            "pedagogical_consistency": self._score_pedagogical_consistency(tutor_responses),
            "student_engagement": self._score_student_engagement(student_queries, tutor_responses),
            "conceptual_understanding": self._score_conceptual_understanding(student_queries, tutor_responses),
            "adaptive_difficulty": self._score_adaptive_difficulty(student_queries, tutor_responses)
        }
        
        # Calculate overall dialog score
        weights = {
            "dialog_coherence": 0.20,
            "context_retention": 0.15,
            "learning_progression": 0.20,
            "pedagogical_consistency": 0.15,
            "student_engagement": 0.15,
            "conceptual_understanding": 0.10,
            "adaptive_difficulty": 0.05
        }
        
        metrics["overall_dialog_score"] = sum(
            metrics[metric] * weights[metric] for metric in weights.keys()
        )
        
        return metrics
    
    def _score_dialog_coherence(
        self,
        student_queries: List[str],
        tutor_responses: List[str]
    ) -> float:
        """
        Score: Dialog Coherence
        Logical flow and coherence across conversation turns.
        """
        if len(tutor_responses) < 2:
            return 0.5  # Neutral for single turn
        
        score = 0.0
        
        # Check for topic continuity
        topic_words = set()
        for i, response in enumerate(tutor_responses):
            response_words = set(response.lower().split())
            if i == 0:
                topic_words = response_words
            else:
                # Check overlap with previous topics
                overlap = len(topic_words.intersection(response_words))
                if overlap > 3:
                    score += 0.2
                topic_words.update(response_words)
        
        # Check for logical connectors between turns
        connector_count = 0
        for i in range(1, len(tutor_responses)):
            response = tutor_responses[i].lower()
            connectors = [
                r'\b(now|next|then|also|furthermore|additionally|building on)\b',
                r'\b(as we discussed|remember|going back)\b'
            ]
            for pattern in connectors:
                if re.search(pattern, response):
                    connector_count += 1
                    break
        
        if connector_count > 0:
            score += min(0.4, connector_count * 0.15)
        
        # Check if responses address student queries
        relevance_count = 0
        for i, (query, response) in enumerate(zip(student_queries, tutor_responses)):
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            overlap = len(query_words.intersection(response_words))
            if overlap > 2:
                relevance_count += 1
        
        if relevance_count > 0:
            score += min(0.4, relevance_count * 0.2)
        
        return min(1.0, score)
    
    def _score_context_retention(
        self,
        student_queries: List[str],
        tutor_responses: List[str]
    ) -> float:
        """
        Score: Context Retention
        How well the tutor remembers and references previous conversation.
        """
        if len(tutor_responses) < 2:
            return 0.5  # Neutral for single turn
        
        score = 0.0
        
        # Check for references to previous turns
        retention_count = 0
        for i in range(1, len(tutor_responses)):
            response = tutor_responses[i].lower()
            
            # Check for context retention patterns
            for pattern in self.context_retention_patterns_compiled:
                if pattern.search(response):
                    retention_count += 1
                    break
            
            # Check for references to previous queries
            prev_query_words = set(student_queries[i-1].lower().split())
            response_words = set(response.lower().split())
            overlap = len(prev_query_words.intersection(response_words))
            if overlap > 2:
                retention_count += 1
        
        if retention_count > 0:
            score = min(1.0, retention_count * 0.3)
        
        return score
    
    def _score_learning_progression(
        self,
        tutor_responses: List[str]
    ) -> float:
        """
        Score: Learning Progression
        Evidence of building understanding across turns.
        """
        if len(tutor_responses) < 2:
            return 0.5
        
        score = 0.0
        
        # Check for progression indicators
        progression_count = 0
        for response in tutor_responses:
            for pattern in self.progression_patterns_compiled:
                if pattern.search(response.lower()):
                    progression_count += 1
                    break
        
        if progression_count > 0:
            score += min(0.5, progression_count * 0.2)
        
        # Check for increasing complexity (simple heuristic)
        complexity_indicators = [
            r'\b(advanced|complex|detailed|deep|sophisticated)\b',
            r'\b(mathematical|theoretical|foundational)\b'
        ]
        complexity_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in complexity_indicators]
        
        complexity_scores = []
        for response in tutor_responses:
            complexity = sum(1 for pattern in complexity_patterns if pattern.search(response.lower()))
            complexity_scores.append(complexity)
        
        # Check if complexity increases (simple progression)
        if len(complexity_scores) > 1:
            increasing = all(complexity_scores[i] <= complexity_scores[i+1] 
                           for i in range(len(complexity_scores)-1))
            if increasing:
                score += 0.3
        
        return min(1.0, score + 0.2)
    
    def _score_pedagogical_consistency(
        self,
        tutor_responses: List[str]
    ) -> float:
        """
        Score: Pedagogical Consistency
        Consistent use of pedagogical strategies across turns.
        """
        if len(tutor_responses) < 2:
            return 0.5
        
        # Check for consistent use of pedagogical elements
        guidance_count = 0
        question_count = 0
        explanation_count = 0
        
        for response in tutor_responses:
            response_lower = response.lower()
            
            # Count guidance patterns
            if re.search(r'\b(hint|think about|consider|try)\b', response_lower):
                guidance_count += 1
            
            # Count questions
            if '?' in response:
                question_count += 1
            
            # Count explanations
            if re.search(r'\b(because|since|this means|in other words)\b', response_lower):
                explanation_count += 1
        
        # Consistency: similar counts across turns
        total_turns = len(tutor_responses)
        guidance_ratio = guidance_count / total_turns
        question_ratio = question_count / total_turns
        explanation_ratio = explanation_count / total_turns
        
        # Score based on consistent presence (not too variable)
        score = (guidance_ratio * 0.3 + question_ratio * 0.3 + explanation_ratio * 0.4)
        
        return min(1.0, score)
    
    def _score_student_engagement(
        self,
        student_queries: List[str],
        tutor_responses: List[str]
    ) -> float:
        """
        Score: Student Engagement
        Maintaining student interest and participation.
        """
        score = 0.0
        
        # Check for follow-up questions in tutor responses
        question_count = sum(1 for response in tutor_responses if '?' in response)
        if question_count > 0:
            score += min(0.4, question_count * 0.15)
        
        # Check for engaging language
        engaging_patterns = [
            r'\b(interesting|fascinating|exciting|curious|wonder)\b',
            r'\b(think about|imagine|consider|what if)\b',
            r'\b(great question|good thinking|nice observation)\b'
        ]
        engaging_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in engaging_patterns]
        
        engaging_count = 0
        for response in tutor_responses:
            for pattern in engaging_patterns_compiled:
                if pattern.search(response.lower()):
                    engaging_count += 1
                    break
        
        if engaging_count > 0:
            score += min(0.4, engaging_count * 0.2)
        
        # Check if student queries get longer/more detailed (engagement indicator)
        if len(student_queries) > 1:
            query_lengths = [len(q.split()) for q in student_queries]
            if query_lengths[-1] > query_lengths[0]:
                score += 0.2
        
        return min(1.0, score + 0.2)
    
    def _score_conceptual_understanding(
        self,
        student_queries: List[str],
        tutor_responses: List[str]
    ) -> float:
        """
        Score: Conceptual Understanding Development
        Evidence of deepening understanding across conversation.
        """
        if len(tutor_responses) < 2:
            return 0.5
        
        score = 0.0
        
        # Check for conceptual depth indicators
        depth_indicators = [
            r'\b(understand|grasp|comprehend|see|realize)\b',
            r'\b(concept|principle|idea|notion|theory)\b',
            r'\b(why|how|what|explain|clarify)\b'
        ]
        depth_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in depth_indicators]
        
        depth_scores = []
        for response in tutor_responses:
            depth = sum(1 for pattern in depth_patterns if pattern.search(response.lower()))
            depth_scores.append(depth)
        
        # Check if depth increases (understanding develops)
        if len(depth_scores) > 1:
            increasing = all(depth_scores[i] <= depth_scores[i+1] 
                           for i in range(len(depth_scores)-1))
            if increasing:
                score += 0.5
        
        # Check for synthesis (connecting concepts)
        synthesis_patterns = [
            r'\b(together|combine|integrate|connect|link)\b',
            r'\b(relate|relationship|connection|similar|different)\b'
        ]
        synthesis_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in synthesis_patterns]
        
        synthesis_count = sum(
            1 for response in tutor_responses
            for pattern in synthesis_patterns_compiled
            if pattern.search(response.lower())
        )
        
        if synthesis_count > 0:
            score += min(0.5, synthesis_count * 0.2)
        
        return min(1.0, score)
    
    def _score_adaptive_difficulty(
        self,
        student_queries: List[str],
        tutor_responses: List[str]
    ) -> float:
        """
        Score: Adaptive Difficulty
        Adjusting complexity based on student responses.
        """
        if len(tutor_responses) < 2:
            return 0.5
        
        # Simple heuristic: check if responses adapt to student query complexity
        query_complexities = []
        response_complexities = []
        
        for query, response in zip(student_queries, tutor_responses):
            # Simple complexity: word count + technical terms
            query_words = len(query.split())
            response_words = len(response.split())
            
            technical_terms_query = len(re.findall(r'\b(RAG|embedding|vector|transformer|neural|algorithm)\b', query, re.IGNORECASE))
            technical_terms_response = len(re.findall(r'\b(RAG|embedding|vector|transformer|neural|algorithm)\b', response, re.IGNORECASE))
            
            query_complexities.append(query_words + technical_terms_query * 3)
            response_complexities.append(response_words + technical_terms_response * 3)
        
        # Check if response complexity matches query complexity
        matches = sum(1 for qc, rc in zip(query_complexities, response_complexities) 
                     if abs(qc - rc) < max(qc, rc) * 0.5)
        
        match_ratio = matches / len(query_complexities) if query_complexities else 0.0
        
        return match_ratio
    
    def _evaluate_single_turn(
        self,
        student_query: str,
        tutor_response: str
    ) -> Dict[str, float]:
        """Evaluate single-turn conversation (basic metrics)."""
        return {
            "dialog_coherence": 0.5,
            "context_retention": 0.5,
            "learning_progression": 0.5,
            "pedagogical_consistency": 0.5,
            "student_engagement": 0.5,
            "conceptual_understanding": 0.5,
            "adaptive_difficulty": 0.5,
            "overall_dialog_score": 0.5
        }


# Global evaluator instance
dialog_evaluator = DialogEvaluator()

