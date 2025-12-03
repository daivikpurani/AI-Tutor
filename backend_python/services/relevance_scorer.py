"""
Relevance Scoring Module
Provides multiple methods to score response relevance and quality.
"""

import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class RelevanceScorer:
    """Scores LLM responses for relevance, quality, and completeness."""
    
    def __init__(self):
        self.citation_pattern = re.compile(r'\[source:\s*[^\]]+\]', re.IGNORECASE)
        self.citation_pattern_alt = re.compile(r'\[.*?\]', re.IGNORECASE)
    
    def score_response(
        self, 
        response: str, 
        query: str,
        self_check_confidence: Optional[float] = None,
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive scoring of a response.
        
        Args:
            response: The LLM response text
            query: The original query
            self_check_confidence: Confidence score from self-check (0-1)
            citations: List of citation dictionaries
            
        Returns:
            Dictionary with various relevance and quality scores
        """
        scores = {
            "self_check_confidence": self_check_confidence or 0.0,
            "citation_score": self._score_citations(response, citations),
            "completeness_score": self._score_completeness(response, query),
            "quality_score": self._score_quality(response),
            "overall_score": 0.0
        }
        
        # Calculate overall score (weighted average)
        weights = {
            "self_check_confidence": 0.4,
            "citation_score": 0.2,
            "completeness_score": 0.2,
            "quality_score": 0.2
        }
        
        scores["overall_score"] = (
            scores["self_check_confidence"] * weights["self_check_confidence"] +
            scores["citation_score"] * weights["citation_score"] +
            scores["completeness_score"] * weights["completeness_score"] +
            scores["quality_score"] * weights["quality_score"]
        )
        
        return scores
    
    def _score_citations(
        self, 
        response: str, 
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """
        Score citation quality and presence.
        
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0
        
        # Check for inline citations in response
        inline_citations = self.citation_pattern.findall(response)
        if inline_citations:
            score += 0.3  # Has inline citations
        
        # Check for citation pattern alternatives
        alt_citations = self.citation_pattern_alt.findall(response)
        if alt_citations and len(alt_citations) > len(inline_citations):
            score += 0.2  # Has some citation-like markers
        
        # Check provided citations list
        if citations:
            citation_count = len(citations)
            if citation_count > 0:
                score += min(0.3, citation_count * 0.1)  # More citations = better
            
            # Check citation quality (has title/url)
            quality_citations = sum(
                1 for c in citations 
                if c.get('title') or c.get('url')
            )
            if quality_citations > 0:
                score += min(0.2, quality_citations * 0.05)
        
        return min(1.0, score)
    
    def _score_completeness(self, response: str, query: str) -> float:
        """
        Score how completely the response addresses the query.
        
        Returns:
            Score between 0.0 and 1.0
        """
        if not response or len(response.strip()) < 10:
            return 0.0
        
        score = 0.0
        
        # Length heuristic (longer responses tend to be more complete)
        response_length = len(response)
        word_count = len(response.split())
        
        if word_count < 20:
            score += 0.2
        elif word_count < 50:
            score += 0.4
        elif word_count < 100:
            score += 0.6
        else:
            score += 0.7
        
        # Check for question words in query and response structure
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Check if response addresses question words
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'explain', 'compare']
        query_has_question = any(word in query_lower for word in question_words)
        
        if query_has_question:
            # Check if response has structure (sentences, paragraphs)
            if '.' in response:
                score += 0.1
            if '\n' in response or len(response.split('.')) > 2:
                score += 0.1
        
        # Check for key terms from query in response
        query_words = set(query_lower.split())
        response_words = set(response_lower.split())
        common_words = query_words.intersection(response_words)
        
        if len(query_words) > 0:
            overlap_ratio = len(common_words) / len(query_words)
            score += min(0.1, overlap_ratio * 0.1)
        
        return min(1.0, score)
    
    def _score_quality(self, response: str) -> float:
        """
        Score basic response quality (structure, coherence, etc.).
        
        Returns:
            Score between 0.0 and 1.0
        """
        if not response or len(response.strip()) < 10:
            return 0.0
        
        score = 0.0
        
        # Basic structure checks
        if len(response) > 50:
            score += 0.2
        
        # Check for sentences (has periods)
        if '.' in response:
            score += 0.2
        
        # Check for multiple sentences
        sentences = response.split('.')
        if len(sentences) > 2:
            score += 0.2
        
        # Check for paragraphs or structure
        if '\n' in response:
            score += 0.1
        
        # Check for common quality indicators
        quality_indicators = [
            'because', 'therefore', 'however', 'example', 'for instance',
            'specifically', 'in addition', 'furthermore'
        ]
        response_lower = response.lower()
        found_indicators = sum(1 for indicator in quality_indicators if indicator in response_lower)
        score += min(0.3, found_indicators * 0.1)
        
        return min(1.0, score)
    
    def extract_citations_from_response(self, response: str) -> List[str]:
        """Extract citation patterns from response text."""
        citations = self.citation_pattern.findall(response)
        return citations
    
    def has_citations(self, response: str) -> bool:
        """Check if response contains citations."""
        return len(self.extract_citations_from_response(response)) > 0
    
    def should_say_i_dont_know(
        self,
        response: str,
        query: str,
        retrieval_quality: Optional[Dict[str, Any]] = None,
        context_chunks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Determine if the response should have said "I don't know" based on quality metrics.
        
        Args:
            response: The LLM response text
            query: The original query
            retrieval_quality: Retrieval quality metrics dict
            context_chunks: List of context chunks used
            
        Returns:
            Dict with 'should_say_i_dont_know' (bool) and 'reasons' (list of strings)
        """
        reasons = []
        should_say = False
        
        # Check retrieval quality
        if retrieval_quality:
            chunk_count = retrieval_quality.get('chunk_count', 0)
            has_good = retrieval_quality.get('has_good_retrieval', False)
            quality_level = retrieval_quality.get('quality_level', 'unknown')
            
            if chunk_count == 0:
                should_say = True
                reasons.append("No context chunks were retrieved")
            elif quality_level == 'poor':
                should_say = True
                reasons.append(f"Poor retrieval quality (level: {quality_level})")
            elif not has_good and quality_level == 'moderate':
                # Check if response seems to be guessing
                if not self.has_citations(response):
                    should_say = True
                    reasons.append("Moderate retrieval quality but no citations provided")
        
        # Check if response contains uncertainty indicators
        uncertainty_phrases = [
            "i don't know",
            "i don't have",
            "i cannot find",
            "insufficient information",
            "not in the documents",
            "not available in",
            "unable to find"
        ]
        response_lower = response.lower()
        has_uncertainty = any(phrase in response_lower for phrase in uncertainty_phrases)
        
        # Check if response lacks citations but should have them
        if context_chunks and len(context_chunks) > 0:
            if not self.has_citations(response) and len(response) > 100:
                # Long response without citations might be speculative
                if not has_uncertainty:
                    reasons.append("Response lacks citations despite having context")
        
        # Check if response seems speculative (contains hedging without acknowledging uncertainty)
        hedging_words = ['might', 'possibly', 'perhaps', 'could be', 'may be', 'likely']
        has_hedging = any(word in response_lower for word in hedging_words)
        if has_hedging and not has_uncertainty and not self.has_citations(response):
            reasons.append("Response contains speculative language without citations or uncertainty acknowledgment")
        
        return {
            'should_say_i_dont_know': should_say or len(reasons) > 0,
            'reasons': reasons,
            'has_uncertainty_acknowledgment': has_uncertainty,
            'has_citations': self.has_citations(response)
        }


# Global scorer instance
relevance_scorer = RelevanceScorer()

