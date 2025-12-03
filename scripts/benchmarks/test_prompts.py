"""
Test Prompts Module
Provides categorized test queries for benchmarking.
"""

from typing import List, Dict, Any
from enum import Enum


class QueryCategory(Enum):
    """Categories of test queries."""
    SIMPLE_FACTUAL = "simple_factual"
    COMPLEX_ANALYTICAL = "complex_analytical"
    DOMAIN_SPECIFIC = "domain_specific"
    EDGE_CASE = "edge_case"


class TestPrompts:
    """Collection of test prompts organized by category."""
    
    # Simple factual queries (3-5 queries)
    SIMPLE_FACTUAL = [
        "What is RAG?",
        "Explain vector databases in 2 sentences.",
        "How do embeddings work for document search?",
        "What is a transformer model?",
        "Define attention mechanism in one sentence."
    ]
    
    # Complex analytical queries (3-5 queries)
    COMPLEX_ANALYTICAL = [
        "Compare OpenAI and local LLM usage tradeoffs.",
        "Analyze the benefits and drawbacks of RAG architecture.",
        "Explain how vector databases improve search relevance compared to traditional keyword search.",
        "What are the key differences between fine-tuning and RAG for adapting LLMs?",
        "Compare the computational requirements of different embedding models."
    ]
    
    # Domain-specific academic queries (3-5 queries)
    DOMAIN_SPECIFIC = [
        "Explain transformer architecture and its key components.",
        "What is the attention mechanism and why is it important?",
        "How does backpropagation work in neural networks?",
        "Describe the difference between supervised and unsupervised learning.",
        "What are the main challenges in training large language models?"
    ]
    
    # Edge cases (2-3 queries)
    EDGE_CASE = [
        "?",  # Very short/ambiguous
        "Explain RAG and vector databases and embeddings and transformers.",  # Multi-part
        "What is the meaning of life?",  # Philosophical/out of scope
    ]
    
    @classmethod
    def get_all_queries(cls) -> List[str]:
        """Get all test queries as a flat list."""
        return (
            cls.SIMPLE_FACTUAL +
            cls.COMPLEX_ANALYTICAL +
            cls.DOMAIN_SPECIFIC +
            cls.EDGE_CASE
        )
    
    @classmethod
    def get_queries_by_category(cls, category: QueryCategory) -> List[str]:
        """Get queries for a specific category."""
        category_map = {
            QueryCategory.SIMPLE_FACTUAL: cls.SIMPLE_FACTUAL,
            QueryCategory.COMPLEX_ANALYTICAL: cls.COMPLEX_ANALYTICAL,
            QueryCategory.DOMAIN_SPECIFIC: cls.DOMAIN_SPECIFIC,
            QueryCategory.EDGE_CASE: cls.EDGE_CASE
        }
        return category_map.get(category, [])
    
    @classmethod
    def get_queries_with_metadata(cls) -> List[Dict[str, Any]]:
        """Get all queries with their category metadata."""
        queries = []
        
        for query in cls.SIMPLE_FACTUAL:
            queries.append({
                "query": query,
                "category": QueryCategory.SIMPLE_FACTUAL.value,
                "expected_complexity": "low",
                "expected_length": "short"
            })
        
        for query in cls.COMPLEX_ANALYTICAL:
            queries.append({
                "query": query,
                "category": QueryCategory.COMPLEX_ANALYTICAL.value,
                "expected_complexity": "high",
                "expected_length": "medium"
            })
        
        for query in cls.DOMAIN_SPECIFIC:
            queries.append({
                "query": query,
                "category": QueryCategory.DOMAIN_SPECIFIC.value,
                "expected_complexity": "medium",
                "expected_length": "medium"
            })
        
        for query in cls.EDGE_CASE:
            queries.append({
                "query": query,
                "category": QueryCategory.EDGE_CASE.value,
                "expected_complexity": "variable",
                "expected_length": "variable"
            })
        
        return queries
    
    @classmethod
    def count_by_category(cls) -> Dict[str, int]:
        """Get count of queries per category."""
        return {
            QueryCategory.SIMPLE_FACTUAL.value: len(cls.SIMPLE_FACTUAL),
            QueryCategory.COMPLEX_ANALYTICAL.value: len(cls.COMPLEX_ANALYTICAL),
            QueryCategory.DOMAIN_SPECIFIC.value: len(cls.DOMAIN_SPECIFIC),
            QueryCategory.EDGE_CASE.value: len(cls.EDGE_CASE)
        }


# Convenience instance
test_prompts = TestPrompts()

