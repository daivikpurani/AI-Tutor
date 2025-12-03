"""
Pedagogical Evaluator Module
Implements 8 pedagogical dimensions from Maurya et al. (NAACL 2025)
"Unifying AI Tutor Evaluation: An Evaluation Taxonomy for Pedagogical Ability Assessment"
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class PedagogicalEvaluator:
    """
    Evaluates tutor responses across 8 pedagogical dimensions.
    
    Based on: Maurya et al. (NAACL 2025) - "Unifying AI Tutor Evaluation"
    """
    
    def __init__(self):
        # Patterns for mistake identification
        self.mistake_patterns = [
            r'\b(error|mistake|wrong|incorrect|not quite|not exactly|not quite right)\b',
            r'\b(that\'s not|that isn\'t|that\'s incorrect)\b',
            r'\b(let me correct|let me clarify|actually)\b',
            r'\b(common misconception|misunderstanding)\b'
        ]
        self.mistake_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.mistake_patterns]
        
        # Patterns for guidance (hints without giving answers)
        self.guidance_patterns = [
            r'\b(hint|think about|consider|try|what if|suppose)\b',
            r'\b(remember that|recall|think back to)\b',
            r'\b(what do you think|can you explain|how would you)\b',
            r'\b(guide|lead|suggest|recommend)\b',
            r'\b(step by step|first|then|next)\b'
        ]
        self.guidance_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.guidance_patterns]
        
        # Patterns for actionability
        self.actionable_patterns = [
            r'\b(do|try|practice|work on|focus on|review)\b',
            r'\b(step \d+|first|second|third|next step)\b',
            r'\b(you should|you can|you might want to)\b',
            r'\b(action|approach|method|strategy)\b'
        ]
        self.actionable_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.actionable_patterns]
        
        # Patterns for encouraging tone
        self.encouraging_patterns = [
            r'\b(great|good|excellent|well done|nice|fantastic)\b',
            r'\b(you\'re on the right track|you\'re doing well|keep going)\b',
            r'\b(that\'s a good question|good thinking|nice work)\b',
            r'\b(don\'t worry|no problem|that\'s okay)\b',
            r'\b(keep trying|you can do it|you\'ve got this)\b'
        ]
        self.encouraging_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.encouraging_patterns]
        
        # Patterns for human-likeness (natural conversation)
        self.human_like_patterns = [
            r'\b(you know|I mean|basically|essentially|sort of|kind of)\b',
            r'\b(let\'s|we\'ll|we can|we should)\b',
            r'\b(does that make sense|does this help|is that clear)\b',
            r'\b(think of it|imagine|picture this)\b'
        ]
        self.human_like_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.human_like_patterns]
        
        # Patterns that indicate robotic/unnatural language
        self.robotic_patterns = [
            r'\b(according to the data|based on the information provided|as per)\b',
            r'\b(please note that|it is important to note|it should be noted)\b',
            r'\b(in conclusion|to summarize|in summary)\b'
        ]
        self.robotic_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.robotic_patterns]
    
    def evaluate_response(
        self,
        response: str,
        student_query: str,
        student_mistakes: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        retrieved_context: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a tutor response across 8 pedagogical dimensions.
        
        Args:
            response: Tutor's response text
            student_query: Student's question/input
            student_mistakes: List of mistakes student made (if any)
            conversation_history: Previous conversation turns
            retrieved_context: Context chunks retrieved from documents
            
        Returns:
            Dictionary with scores for all 8 dimensions
        """
        if not response or len(response.strip()) < 10:
            return self._empty_scores()
        
        scores = {
            "mistake_identification": self._score_mistake_identification(
                response, student_query, student_mistakes
            ),
            "mistake_location": self._score_mistake_location(
                response, student_query, student_mistakes
            ),
            "revealing_answer": self._score_revealing_answer(
                response, student_query, student_mistakes
            ),
            "providing_guidance": self._score_providing_guidance(
                response, student_query
            ),
            "actionability": self._score_actionability(response),
            "coherence": self._score_coherence(response, student_query),
            "tutor_tone": self._score_tutor_tone(response),
            "human_likeness": self._score_human_likeness(response)
        }
        
        # Calculate overall pedagogical score (weighted average)
        weights = {
            "mistake_identification": 0.15,
            "mistake_location": 0.10,
            "revealing_answer": 0.15,
            "providing_guidance": 0.20,
            "actionability": 0.15,
            "coherence": 0.10,
            "tutor_tone": 0.10,
            "human_likeness": 0.05
        }
        
        scores["overall_pedagogical_score"] = sum(
            scores[dim] * weights[dim] for dim in scores.keys() if dim != "overall_pedagogical_score"
        )
        
        return scores
    
    def _score_mistake_identification(
        self,
        response: str,
        student_query: str,
        student_mistakes: Optional[List[str]]
    ) -> float:
        """
        Score: Mistake Identification
        Detecting student errors accurately.
        """
        if not student_mistakes:
            # If no mistakes expected, check if response incorrectly identifies mistakes
            mistake_indicators = sum(
                1 for pattern in self.mistake_patterns_compiled
                if pattern.search(response)
            )
            if mistake_indicators > 0:
                return 0.7  # Partial score - identified something, but no mistake existed
            return 1.0  # No mistakes to identify, response doesn't claim mistakes
        
        # If mistakes exist, check if they're identified
        response_lower = response.lower()
        identified_count = 0
        
        for mistake in student_mistakes:
            mistake_lower = mistake.lower()
            # Check if mistake is mentioned or addressed
            if mistake_lower in response_lower:
                identified_count += 1
            # Check for mistake patterns near mistake content
            for pattern in self.mistake_patterns_compiled:
                if pattern.search(response):
                    # Check if mistake-related content is nearby
                    mistake_words = mistake_lower.split()
                    if any(word in response_lower for word in mistake_words if len(word) > 3):
                        identified_count += 1
                        break
        
        if identified_count == 0:
            return 0.0
        
        return min(1.0, identified_count / len(student_mistakes))
    
    def _score_mistake_location(
        self,
        response: str,
        student_query: str,
        student_mistakes: Optional[List[str]]
    ) -> float:
        """
        Score: Mistake Location
        Pinpointing where errors occurred.
        """
        if not student_mistakes:
            return 0.5  # Neutral score when no mistakes exist
        
        response_lower = response.lower()
        location_indicators = [
            r'\b(in|at|on|where|here|there)\b.*\b(error|mistake|wrong|incorrect)\b',
            r'\b(the (first|second|third|last) (step|part|section|line))\b',
            r'\b(when you|when it|where you|where it)\b',
            r'\b(specifically|particularly|exactly)\b'
        ]
        
        location_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in location_indicators]
        
        location_found = any(pattern.search(response) for pattern in location_patterns)
        
        if location_found:
            return 0.8
        elif any(pattern.search(response) for pattern in self.mistake_patterns_compiled):
            return 0.5  # Mistake identified but location not specified
        else:
            return 0.2
    
    def _score_revealing_answer(
        self,
        response: str,
        student_query: str,
        student_mistakes: Optional[List[str]]
    ) -> float:
        """
        Score: Revealing of the Answer
        Appropriate timing for providing correct answers.
        """
        response_lower = response.lower()
        
        # Check if answer is given directly
        direct_answer_indicators = [
            r'\b(the answer is|the correct answer|the solution is)\b',
            r'\b(it is|it\'s|that is|that\'s)\b.*\b(correct|right|answer)\b',
            r'^[A-Z][^.!?]*\.\s*(That\'s|It\'s|This is)',
        ]
        
        direct_answer_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in direct_answer_indicators]
        
        has_direct_answer = any(pattern.search(response) for pattern in direct_answer_patterns)
        
        # Check for guidance/hints before answer
        guidance_before_answer = False
        if has_direct_answer:
            # Check if guidance appears before direct answer
            guidance_positions = []
            answer_positions = []
            
            for i, pattern in enumerate(self.guidance_patterns_compiled):
                matches = list(pattern.finditer(response_lower))
                if matches:
                    guidance_positions.extend([m.start() for m in matches])
            
            for pattern in direct_answer_patterns:
                matches = list(pattern.finditer(response_lower))
                if matches:
                    answer_positions.extend([m.start() for m in matches])
            
            if guidance_positions and answer_positions:
                guidance_before_answer = min(guidance_positions) < min(answer_positions)
        
        # Scoring logic
        if student_mistakes:
            # If student made mistakes, should provide guidance first, then answer
            if guidance_before_answer and has_direct_answer:
                return 0.9
            elif has_direct_answer:
                return 0.6  # Answer given but no guidance first
            else:
                return 0.8  # Guidance without direct answer (good for mistakes)
        else:
            # No mistakes - direct answer is appropriate
            if has_direct_answer:
                return 1.0
            elif any(pattern.search(response) for pattern in self.guidance_patterns_compiled):
                return 0.7  # Only guidance, no direct answer (might be too indirect)
            else:
                return 0.5
    
    def _score_providing_guidance(
        self,
        response: str,
        student_query: str
    ) -> float:
        """
        Score: Providing Guidance
        Offering hints/scaffolding without giving away answers.
        """
        response_lower = response.lower()
        
        # Count guidance patterns
        guidance_count = sum(
            1 for pattern in self.guidance_patterns_compiled
            if pattern.search(response)
        )
        
        # Check for scaffolding (building from known to unknown)
        scaffolding_indicators = [
            r'\b(first|second|then|next|finally|step by step)\b',
            r'\b(building on|based on|now that you know)\b',
            r'\b(think about|consider|remember)\b'
        ]
        scaffolding_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in scaffolding_indicators]
        scaffolding_count = sum(1 for pattern in scaffolding_patterns if pattern.search(response))
        
        # Check if answer is given away too easily
        direct_answer_given = any(
            pattern.search(response) for pattern in [
                re.compile(r'\b(the answer is|the solution is|it\'s|that\'s)\b', re.IGNORECASE)
            ]
        )
        
        # Scoring
        score = 0.0
        
        if guidance_count > 0:
            score += min(0.5, guidance_count * 0.15)
        
        if scaffolding_count > 0:
            score += min(0.3, scaffolding_count * 0.1)
        
        # Penalize if answer given away too easily
        if direct_answer_given and guidance_count == 0:
            score *= 0.5
        
        return min(1.0, score + 0.2)  # Base score for any response
    
    def _score_actionability(
        self,
        response: str
    ) -> float:
        """
        Score: Actionability
        Ensuring feedback leads to actionable steps.
        """
        response_lower = response.lower()
        
        # Count actionable patterns
        actionable_count = sum(
            1 for pattern in self.actionable_patterns_compiled
            if pattern.search(response)
        )
        
        # Check for specific steps or instructions
        step_indicators = [
            r'\b(step \d+|first|second|third|next|then|finally)\b',
            r'\b(you should|you can|you might|try|practice|work on)\b',
            r'\b(to do this|to solve this|to understand this)\b'
        ]
        step_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in step_indicators]
        step_count = sum(1 for pattern in step_patterns if pattern.search(response))
        
        # Scoring
        score = 0.0
        
        if actionable_count > 0:
            score += min(0.5, actionable_count * 0.2)
        
        if step_count > 0:
            score += min(0.4, step_count * 0.15)
        
        # Check for vague language (penalize)
        vague_patterns = [
            r'\b(somehow|maybe|perhaps|possibly|might want to consider)\b'
        ]
        vague_count = sum(1 for pattern in vague_patterns if re.compile(pattern, re.IGNORECASE).search(response))
        if vague_count > 2:
            score *= 0.7
        
        return min(1.0, score + 0.3)  # Base score
    
    def _score_coherence(
        self,
        response: str,
        student_query: str
    ) -> float:
        """
        Score: Coherence
        Maintaining logical and clear communication.
        """
        if not response:
            return 0.0
        
        score = 0.0
        
        # Check for sentence structure
        sentences = response.split('.')
        if len(sentences) > 1:
            score += 0.3
        
        # Check for logical connectors
        connectors = [
            r'\b(because|therefore|however|although|since|so|thus)\b',
            r'\b(first|second|then|next|finally|additionally|furthermore)\b',
            r'\b(for example|for instance|specifically|in particular)\b'
        ]
        connector_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in connectors]
        connector_count = sum(1 for pattern in connector_patterns if pattern.search(response))
        
        if connector_count > 0:
            score += min(0.3, connector_count * 0.1)
        
        # Check for topic relevance (query words in response)
        query_words = set(student_query.lower().split())
        response_words = set(response.lower().split())
        common_words = query_words.intersection(response_words)
        
        if len(query_words) > 0:
            relevance_ratio = len(common_words) / len(query_words)
            score += min(0.2, relevance_ratio * 0.2)
        
        # Check for paragraph structure
        if '\n' in response or len(sentences) > 3:
            score += 0.2
        
        return min(1.0, score)
    
    def _score_tutor_tone(
        self,
        response: str
    ) -> float:
        """
        Score: Tutor Tone
        Using encouraging and supportive tone.
        """
        response_lower = response.lower()
        
        score = 0.0
        
        # Count encouraging patterns
        encouraging_count = sum(
            1 for pattern in self.encouraging_patterns_compiled
            if pattern.search(response)
        )
        
        if encouraging_count > 0:
            score += min(0.6, encouraging_count * 0.2)
        
        # Check for supportive language
        supportive_patterns = [
            r'\b(that\'s okay|no problem|don\'t worry|it\'s fine)\b',
            r'\b(you\'re doing well|keep going|you can do it)\b',
            r'\b(good question|nice thinking|great start)\b'
        ]
        supportive_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in supportive_patterns]
        supportive_count = sum(1 for pattern in supportive_patterns_compiled if pattern.search(response))
        
        if supportive_count > 0:
            score += min(0.3, supportive_count * 0.15)
        
        # Check for negative/harsh language (penalize)
        negative_patterns = [
            r'\b(wrong|incorrect|bad|terrible|no that\'s wrong)\b',
            r'\b(you should know|obviously|clearly)\b'
        ]
        negative_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in negative_patterns]
        negative_count = sum(1 for pattern in negative_patterns_compiled if pattern.search(response))
        
        if negative_count > 2:
            score *= 0.6
        
        return min(1.0, score + 0.2)  # Base score for neutral tone
    
    def _score_human_likeness(
        self,
        response: str
    ) -> float:
        """
        Score: Human-likeness
        Natural, conversational responses.
        """
        response_lower = response.lower()
        
        score = 0.0
        
        # Count human-like patterns
        human_like_count = sum(
            1 for pattern in self.human_like_patterns_compiled
            if pattern.search(response)
        )
        
        if human_like_count > 0:
            score += min(0.5, human_like_count * 0.15)
        
        # Check for contractions (more natural)
        contractions = re.findall(r'\b\w+\'\w+\b', response_lower)
        if len(contractions) > 0:
            score += min(0.2, len(contractions) * 0.05)
        
        # Check for questions (conversational)
        question_count = response.count('?')
        if question_count > 0:
            score += min(0.2, question_count * 0.1)
        
        # Penalize robotic patterns
        robotic_count = sum(
            1 for pattern in self.robotic_patterns_compiled
            if pattern.search(response)
        )
        
        if robotic_count > 0:
            score *= (1.0 - min(0.5, robotic_count * 0.2))
        
        # Check for varied sentence length (more natural)
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        if len(sentences) > 2:
            lengths = [len(s.split()) for s in sentences]
            length_variance = max(lengths) - min(lengths) if lengths else 0
            if length_variance > 5:
                score += 0.1
        
        return min(1.0, score + 0.3)  # Base score
    
    def _empty_scores(self) -> Dict[str, float]:
        """Return empty scores dictionary."""
        return {
            "mistake_identification": 0.0,
            "mistake_location": 0.0,
            "revealing_answer": 0.0,
            "providing_guidance": 0.0,
            "actionability": 0.0,
            "coherence": 0.0,
            "tutor_tone": 0.0,
            "human_likeness": 0.0,
            "overall_pedagogical_score": 0.0
        }
    
    def evaluate_batch(
        self,
        responses: List[str],
        student_queries: List[str],
        student_mistakes_list: Optional[List[Optional[List[str]]]] = None,
        conversation_histories: Optional[List[List[Dict[str, str]]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a batch of responses.
        
        Returns:
            Aggregated metrics across all responses
        """
        if len(responses) != len(student_queries):
            raise ValueError("Responses and queries must have same length")
        
        individual_results = []
        for i, response in enumerate(responses):
            mistakes = student_mistakes_list[i] if student_mistakes_list and i < len(student_mistakes_list) else None
            history = conversation_histories[i] if conversation_histories and i < len(conversation_histories) else None
            
            result = self.evaluate_response(
                response=response,
                student_query=student_queries[i],
                student_mistakes=mistakes,
                conversation_history=history
            )
            individual_results.append(result)
        
        # Aggregate metrics
        aggregated = {}
        for dimension in [
            "mistake_identification", "mistake_location", "revealing_answer",
            "providing_guidance", "actionability", "coherence", "tutor_tone",
            "human_likeness", "overall_pedagogical_score"
        ]:
            scores = [r[dimension] for r in individual_results]
            aggregated[dimension] = {
                "mean": sum(scores) / len(scores) if scores else 0.0,
                "min": min(scores) if scores else 0.0,
                "max": max(scores) if scores else 0.0,
                "std": self._calculate_std(scores) if len(scores) > 1 else 0.0
            }
        
        return {
            "total_responses": len(responses),
            "aggregated_scores": aggregated,
            "individual_results": individual_results
        }
    
    def _calculate_std(self, scores: List[float]) -> float:
        """Calculate standard deviation."""
        if len(scores) < 2:
            return 0.0
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance ** 0.5


# Global evaluator instance
pedagogical_evaluator = PedagogicalEvaluator()

