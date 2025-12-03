"""
Domain Evaluator Module
Implements domain-specific assessment methodology from Chen et al. (IJAED 2025)
"Benchmarking Large Language Models on Homework Assessment"
"""

import re
import logging
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class DomainEvaluator:
    """
    Evaluates responses for domain-specific accuracy and quality.
    
    Based on: Chen et al. (IJAED 2025) - Domain-specific assessment methodology
    """
    
    def __init__(self):
        # Domain-specific terminology dictionaries
        self.domain_terminology = {
            "rag": [
                "retrieval", "augmentation", "generation", "vector database",
                "embedding", "semantic search", "context", "chunking",
                "reranking", "knowledge base"
            ],
            "embeddings": [
                "vector", "embedding", "semantic", "similarity", "cosine",
                "dimensionality", "transformer", "encoding", "representation"
            ],
            "vector_databases": [
                "vector", "database", "indexing", "similarity search",
                "chromadb", "pinecone", "hnsw", "ivf", "lsh"
            ],
            "transformers": [
                "attention", "self-attention", "multi-head", "positional encoding",
                "encoder", "decoder", "transformer", "layer normalization"
            ],
            "neural_networks": [
                "neural network", "backpropagation", "gradient", "loss function",
                "activation", "weights", "bias", "forward pass", "backward pass"
            ],
            "ai_ml": [
                "machine learning", "deep learning", "supervised", "unsupervised",
                "reinforcement learning", "model", "training", "inference"
            ]
        }
        
        # Domain-specific accuracy patterns
        self.accuracy_indicators = {
            "rag": {
                "correct": [
                    r'\b(retrieval.*augmentation|augmentation.*retrieval)\b',
                    r'\b(two phases|retrieval phase|augmentation phase)\b',
                    r'\b(vector database|semantic search)\b'
                ],
                "incorrect": [
                    r'\b(RAG.*fine.*tuning|fine.*tuning.*RAG)\b',  # Common confusion
                    r'\b(RAG.*always.*improves)\b'  # Overgeneralization
                ]
            },
            "embeddings": {
                "correct": [
                    r'\b(semantic.*meaning|vector.*representation)\b',
                    r'\b(cosine.*similarity|similarity.*search)\b',
                    r'\b(high.*dimensional|dense.*vector)\b'
                ],
                "incorrect": [
                    r'\b(embeddings.*exact.*match)\b',
                    r'\b(embeddings.*always.*better)\b'
                ]
            }
        }
    
    def evaluate_response(
        self,
        response: str,
        domain: str,
        expected_key_points: Optional[List[str]] = None,
        ground_truth_facts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate response for domain-specific accuracy and quality.
        
        Args:
            response: Tutor's response text
            domain: Domain name (rag, embeddings, transformers, etc.)
            expected_key_points: List of key points that should be covered
            ground_truth_facts: Dictionary of ground truth facts
            
        Returns:
            Dictionary with domain-specific evaluation metrics
        """
        if not response:
            return self._empty_scores()
        
        response_lower = response.lower()
        domain_lower = domain.lower()
        
        metrics = {
            "domain_accuracy": self._score_domain_accuracy(
                response, domain_lower, expected_key_points, ground_truth_facts
            ),
            "terminology_correctness": self._score_terminology_correctness(
                response_lower, domain_lower
            ),
            "technical_depth": self._score_technical_depth(
                response_lower, domain_lower
            ),
            "practical_relevance": self._score_practical_relevance(
                response_lower, domain_lower
            ),
            "feedback_quality": self._score_feedback_quality(
                response, domain_lower
            )
        }
        
        # Calculate overall domain score
        weights = {
            "domain_accuracy": 0.35,
            "terminology_correctness": 0.25,
            "technical_depth": 0.20,
            "practical_relevance": 0.10,
            "feedback_quality": 0.10
        }
        
        metrics["overall_domain_score"] = sum(
            metrics[metric] * weights[metric] for metric in weights.keys()
        )
        
        return metrics
    
    def _score_domain_accuracy(
        self,
        response: str,
        domain: str,
        expected_key_points: Optional[List[str]],
        ground_truth_facts: Optional[Dict[str, Any]]
    ) -> float:
        """
        Score: Domain Accuracy
        Factual correctness within the domain context.
        """
        score = 0.0
        
        # Check against expected key points
        if expected_key_points:
            response_lower = response.lower()
            covered_points = 0
            
            for point in expected_key_points:
                point_words = set(point.lower().split())
                response_words = set(response_lower.split())
                
                # Check for significant overlap
                overlap = len(point_words.intersection(response_words))
                if overlap >= len(point_words) * 0.5:  # At least 50% overlap
                    covered_points += 1
            
            score += (covered_points / len(expected_key_points)) * 0.6
        
        # Check against ground truth facts
        if ground_truth_facts:
            response_lower = response.lower()
            correct_facts = 0
            total_facts = 0
            
            for fact_key, fact_value in ground_truth_facts.items():
                if isinstance(fact_value, str):
                    total_facts += 1
                    # Check if fact is present and correct
                    fact_words = set(fact_value.lower().split())
                    response_words = set(response_lower.split())
                    overlap = len(fact_words.intersection(response_words))
                    if overlap >= len(fact_words) * 0.6:
                        correct_facts += 1
                elif isinstance(fact_value, list):
                    # Check if list items are mentioned
                    for item in fact_value:
                        total_facts += 1
                        if item.lower() in response_lower:
                            correct_facts += 1
            
            if total_facts > 0:
                score += (correct_facts / total_facts) * 0.4
        
        # Check for domain-specific accuracy patterns
        if domain in self.accuracy_indicators:
            patterns = self.accuracy_indicators[domain]
            
            # Check for correct patterns
            correct_count = sum(
                1 for pattern in patterns.get("correct", [])
                if re.search(pattern, response.lower(), re.IGNORECASE)
            )
            
            # Check for incorrect patterns (penalize)
            incorrect_count = sum(
                1 for pattern in patterns.get("incorrect", [])
                if re.search(pattern, response.lower(), re.IGNORECASE)
            )
            
            if correct_count > 0:
                score += min(0.3, correct_count * 0.1)
            
            if incorrect_count > 0:
                score *= (1.0 - min(0.5, incorrect_count * 0.2))
        
        return min(1.0, score + 0.2)  # Base score
    
    def _score_terminology_correctness(
        self,
        response_lower: str,
        domain: str
    ) -> float:
        """
        Score: Terminology Correctness
        Proper use of domain-specific terminology.
        """
        if domain not in self.domain_terminology:
            return 0.5  # Neutral if domain not in dictionary
        
        domain_terms = self.domain_terminology[domain]
        
        # Count correct terminology usage
        correct_terms = sum(
            1 for term in domain_terms
            if term.lower() in response_lower
        )
        
        # Score based on terminology coverage
        if len(domain_terms) > 0:
            score = min(1.0, correct_terms / len(domain_terms) * 1.5)  # Allow for partial coverage
        else:
            score = 0.5
        
        # Check for incorrect terminology (common mistakes)
        incorrect_patterns = {
            "rag": [
                r'\b(RAG.*same.*fine.*tuning)\b',
                r'\b(vector.*database.*same.*SQL)\b'
            ],
            "embeddings": [
                r'\b(embedding.*exact.*match)\b',
                r'\b(vector.*same.*word)\b'
            ]
        }
        
        if domain in incorrect_patterns:
            incorrect_count = sum(
                1 for pattern in incorrect_patterns[domain]
                if re.search(pattern, response_lower, re.IGNORECASE)
            )
            if incorrect_count > 0:
                score *= (1.0 - min(0.4, incorrect_count * 0.2))
        
        return min(1.0, score)
    
    def _score_technical_depth(
        self,
        response_lower: str,
        domain: str
    ) -> float:
        """
        Score: Technical Depth
        Appropriate level of technical detail for the domain.
        """
        score = 0.0
        
        # Check for technical concepts
        technical_indicators = {
            "rag": [
                r'\b(architecture|pipeline|component|phase|mechanism)\b',
                r'\b(retrieval|augmentation|embedding|vector|similarity)\b'
            ],
            "embeddings": [
                r'\b(dimensional|vector|space|similarity|distance)\b',
                r'\b(neural.*network|transformer|encoding|representation)\b'
            ],
            "transformers": [
                r'\b(attention|self.*attention|multi.*head|positional)\b',
                r'\b(encoder|decoder|layer|normalization|feed.*forward)\b'
            ],
            "neural_networks": [
                r'\b(backpropagation|gradient|loss|activation|weight|bias)\b',
                r'\b(forward.*pass|backward.*pass|training|inference)\b'
            ]
        }
        
        if domain in technical_indicators:
            technical_count = sum(
                1 for pattern in technical_indicators[domain]
                if re.search(pattern, response_lower, re.IGNORECASE)
            )
            
            if technical_count > 0:
                score = min(1.0, technical_count * 0.2)
        
        # Check for mathematical/theoretical depth
        math_indicators = [
            r'\b(formula|equation|mathematical|theoretical|foundation)\b',
            r'\b(algorithm|complexity|optimization|efficiency)\b'
        ]
        math_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in math_indicators]
        math_count = sum(1 for pattern in math_patterns if pattern.search(response_lower))
        
        if math_count > 0:
            score += min(0.3, math_count * 0.15)
        
        return min(1.0, score + 0.3)  # Base score
    
    def _score_practical_relevance(
        self,
        response_lower: str,
        domain: str
    ) -> float:
        """
        Score: Practical Relevance
        Connection to real-world applications and use cases.
        """
        score = 0.0
        
        # Check for application/use case mentions
        application_patterns = [
            r'\b(use case|application|example|scenario|when.*use)\b',
            r'\b(practical|real.*world|production|deployment)\b',
            r'\b(benefit|advantage|useful|helpful|solve)\b'
        ]
        application_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in application_patterns]
        
        application_count = sum(
            1 for pattern in application_patterns_compiled
            if pattern.search(response_lower)
        )
        
        if application_count > 0:
            score += min(0.6, application_count * 0.2)
        
        # Check for specific examples
        example_patterns = [
            r'\b(for example|for instance|such as|like|imagine)\b',
            r'\b(consider|suppose|think.*about)\b'
        ]
        example_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in example_patterns]
        example_count = sum(1 for pattern in example_patterns_compiled if pattern.search(response_lower))
        
        if example_count > 0:
            score += min(0.4, example_count * 0.2)
        
        return min(1.0, score + 0.2)
    
    def _score_feedback_quality(
        self,
        response: str,
        domain: str
    ) -> float:
        """
        Score: Feedback Quality
        Quality of domain-specific feedback and guidance.
        """
        response_lower = response.lower()
        score = 0.0
        
        # Check for constructive feedback
        feedback_patterns = [
            r'\b(helpful|useful|good|better|improve|suggest)\b',
            r'\b(consider|think about|try|practice|work on)\b',
            r'\b(important|key|crucial|essential|critical)\b'
        ]
        feedback_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in feedback_patterns]
        
        feedback_count = sum(
            1 for pattern in feedback_patterns_compiled
            if pattern.search(response_lower)
        )
        
        if feedback_count > 0:
            score += min(0.5, feedback_count * 0.15)
        
        # Check for actionable steps
        actionable_patterns = [
            r'\b(step|first|then|next|finally|to do)\b',
            r'\b(you should|you can|you might|try|practice)\b'
        ]
        actionable_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in actionable_patterns]
        actionable_count = sum(1 for pattern in actionable_patterns_compiled if pattern.search(response_lower))
        
        if actionable_count > 0:
            score += min(0.5, actionable_count * 0.2)
        
        return min(1.0, score + 0.2)
    
    def _empty_scores(self) -> Dict[str, float]:
        """Return empty scores dictionary."""
        return {
            "domain_accuracy": 0.0,
            "terminology_correctness": 0.0,
            "technical_depth": 0.0,
            "practical_relevance": 0.0,
            "feedback_quality": 0.0,
            "overall_domain_score": 0.0
        }
    
    def evaluate_batch(
        self,
        responses: List[str],
        domains: List[str],
        expected_key_points_list: Optional[List[Optional[List[str]]]] = None,
        ground_truth_facts_list: Optional[List[Optional[Dict[str, Any]]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a batch of responses across domains.
        
        Returns:
            Aggregated metrics by domain
        """
        if len(responses) != len(domains):
            raise ValueError("Responses and domains must have same length")
        
        individual_results = []
        domain_results = defaultdict(list)
        
        for i, (response, domain) in enumerate(zip(responses, domains)):
            expected_points = expected_key_points_list[i] if expected_key_points_list and i < len(expected_key_points_list) else None
            ground_truth = ground_truth_facts_list[i] if ground_truth_facts_list and i < len(ground_truth_facts_list) else None
            
            result = self.evaluate_response(
                response=response,
                domain=domain,
                expected_key_points=expected_points,
                ground_truth_facts=ground_truth
            )
            individual_results.append(result)
            domain_results[domain].append(result)
        
        # Aggregate by domain
        domain_aggregates = {}
        for domain, results in domain_results.items():
            domain_aggregates[domain] = {}
            for metric in [
                "domain_accuracy", "terminology_correctness", "technical_depth",
                "practical_relevance", "feedback_quality", "overall_domain_score"
            ]:
                scores = [r[metric] for r in results]
                domain_aggregates[domain][metric] = {
                    "mean": sum(scores) / len(scores) if scores else 0.0,
                    "min": min(scores) if scores else 0.0,
                    "max": max(scores) if scores else 0.0
                }
        
        return {
            "total_responses": len(responses),
            "by_domain": domain_aggregates,
            "individual_results": individual_results
        }


# Global evaluator instance
domain_evaluator = DomainEvaluator()

