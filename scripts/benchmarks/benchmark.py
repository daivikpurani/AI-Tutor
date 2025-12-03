#!/usr/bin/env python3
"""
Enhanced Benchmark Script
Tests multiple LLM models and generates comprehensive comparison reports.
"""

import argparse
import asyncio
import sys
import os
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend_python'))

# Add scripts/benchmarks to path for test_prompts
benchmarks_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, benchmarks_dir)

from services.benchmark_config import BenchmarkConfig
from services.llm_service import HybridLLMService, LLMProvider
from services.relevance_scorer import RelevanceScorer
from services.query_handler import QueryHandler
from test_prompts import TestPrompts
from report_generator import ReportGenerator
from utils.prompts import PromptTemplates

logger = None


def setup_logging():
    """Setup basic logging."""
    import logging
    global logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)


def load_queries(path: str) -> List[str]:
    """Load queries from file, filtering out comments."""
    queries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                queries.append(line)
    return queries


async def benchmark_single_model(
    llm_service: HybridLLMService,
    query_handler: QueryHandler,
    relevance_scorer: RelevanceScorer,
    provider: LLMProvider,
    model_name: str,
    query: str,
    mode: str = "exploration"
) -> Dict[str, Any]:
    """
    Benchmark a single query against a specific model.
    
    Returns:
        Dictionary with comprehensive metrics
    """
    start_time = time.perf_counter()
    error = None
    response_content = ""
    citations = []
    self_check_confidence = 0.0
    
    try:
        # Get context from vector DB (if available)
        context_chunks = await query_handler._get_relevant_context(query)
        
        # Build prompt
        context_text = query_handler._build_context_text(context_chunks)
        prompt = query_handler.prompt_templates.create_tutor_prompt(
            query=query,
            context=context_text,
            conversation_history="",
            mode=mode
        )
        
        # Prepare messages
        system_prompt = (
            query_handler.prompt_templates.SYSTEM_ASSESSMENT 
            if mode == "assessment" 
            else query_handler.prompt_templates.SYSTEM_EXPLORATION
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Generate response with specific provider/model
        response = await llm_service.generate_response_with_provider(
            messages=messages,
            provider=provider,
            model=model_name,
            max_tokens=1000,
            temperature=0.7
        )
        
        response_content = response.content
        
        # Get self-check confidence if available
        if response.metadata:
            self_check_confidence = response.metadata.get('confidence', 0.0)
        
        # Build citations
        for chunk in context_chunks:
            meta = chunk.get('metadata', {}) if isinstance(chunk, dict) else {}
            citations.append({
                'title': meta.get('title') or meta.get('filename') or 'Source',
                'url': meta.get('url') or meta.get('source_url'),
                'score': None
            })
        
    except Exception as e:
        error = str(e)
        logger.error(f"Error benchmarking {provider.value}:{model_name} with query '{query[:50]}...': {e}")
    
    latency_ms = (time.perf_counter() - start_time) * 1000.0
    
    # Calculate relevance scores
    scores = relevance_scorer.score_response(
        response=response_content,
        query=query,
        self_check_confidence=self_check_confidence,
        citations=citations
    )
    
    # Extract token usage
    usage = {}
    if hasattr(response, 'usage'):
        usage = response.usage or {}
    
    result = {
        "query": query,
        "provider": provider.value,
        "model": model_name,
        "latency_ms": round(latency_ms, 2),
        "response_length": len(response_content),
        "response_words": len(response_content.split()),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "self_check_confidence": scores["self_check_confidence"],
        "citation_score": scores["citation_score"],
        "completeness_score": scores["completeness_score"],
        "quality_score": scores["quality_score"],
        "overall_score": scores["overall_score"],
        "citations_count": len(citations),
        "error": error,
        "status": "error" if error else "success",
        "timestamp": datetime.now().isoformat()
    }
    
    return result


async def run_benchmark_for_model(
    llm_service: HybridLLMService,
    query_handler: QueryHandler,
    relevance_scorer: RelevanceScorer,
    provider: LLMProvider,
    model_name: str,
    queries: List[str],
    mode: str = "exploration"
) -> List[Dict[str, Any]]:
    """Run benchmark for a specific model across all queries."""
    logger.info(f"Benchmarking {provider.value}:{model_name} with {len(queries)} queries")
    results = []
    
    for i, query in enumerate(queries, 1):
        logger.info(f"  [{i}/{len(queries)}] Testing: {query[:60]}...")
        result = await benchmark_single_model(
            llm_service=llm_service,
            query_handler=query_handler,
            relevance_scorer=relevance_scorer,
            provider=provider,
            model_name=model_name,
            query=query,
            mode=mode
        )
        results.append(result)
        
        # Small delay between queries to avoid overwhelming the system
        await asyncio.sleep(0.5)
    
    return results


async def run_all_benchmarks(
    queries: List[str],
    models: List[Dict[str, Any]],
    mode: str = "exploration"
) -> List[Dict[str, Any]]:
    """Run benchmarks for all models."""
    # Initialize services
    llm_service = HybridLLMService()
    await llm_service.initialize()
    
    query_handler = QueryHandler()
    await query_handler._ensure_llm_service_initialized()
    
    relevance_scorer = RelevanceScorer()
    
    all_results = []
    
    # Test each model sequentially
    for model_info in models:
        provider_name = model_info["provider"]
        model_name = model_info["model"]
        
        # Map provider name to enum
        if provider_name == "ollama":
            provider = LLMProvider.OLLAMA
        elif provider_name == "openai":
            provider = LLMProvider.OPENAI
        else:
            logger.warning(f"Unknown provider: {provider_name}, skipping")
            continue
        
        # Check if provider/model is available
        provider_instance = llm_service.providers.get(provider)
        if not provider_instance or not provider_instance.is_available:
            logger.warning(f"Provider {provider_name} not available, skipping {model_name}")
            continue
        
        try:
            model_results = await run_benchmark_for_model(
                llm_service=llm_service,
                query_handler=query_handler,
                relevance_scorer=relevance_scorer,
                provider=provider,
                model_name=model_name,
                queries=queries,
                mode=mode
            )
            all_results.extend(model_results)
        except Exception as e:
            logger.error(f"Failed to benchmark {provider_name}:{model_name}: {e}")
            # Add error results for this model
            for query in queries:
                all_results.append({
                    "query": query,
                    "provider": provider_name,
                    "model": model_name,
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat()
                })
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description="AI Tutor Enhanced Benchmark Runner")
    parser.add_argument(
        "--queries", 
        default="scripts/benchmarks/queries.txt",
        help="Path to queries text file (one per line)"
    )
    parser.add_argument(
        "--models",
        choices=["all", "ollama", "openai"],
        default="all",
        help="Which models to benchmark"
    )
    parser.add_argument(
        "--mode",
        default="exploration",
        choices=["exploration", "assessment"],
        help="LLM mode"
    )
    parser.add_argument(
        "--out",
        default="backend_python/logs/benchmarks",
        help="Output directory"
    )
    parser.add_argument(
        "--use-test-prompts",
        action="store_true",
        help="Use built-in test prompts instead of file"
    )
    parser.add_argument(
        "--scale",
        choices=["small", "medium", "large"],
        default=None,
        help="Benchmark scale preset: small (3-5 queries, 1-2 models), medium (10-20 queries, 2-3 models), large (all queries, all models)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of queries to test (overrides scale preset)"
    )
    args = parser.parse_args()
    
    setup_logging()
    
    # Apply scale presets if specified
    query_limit = None
    models_filter = args.models
    
    if args.scale:
        if args.scale == "small":
            query_limit = 5
            if args.models == "all":
                models_filter = "ollama"  # Default to ollama for small scale
            logger.info("Using SMALL scale preset: 5 queries, 1-2 models")
        elif args.scale == "medium":
            query_limit = 15
            logger.info("Using MEDIUM scale preset: 15 queries, 2-3 models")
        elif args.scale == "large":
            query_limit = None  # Use all queries
            if args.models == "all":
                models_filter = "all"  # Use all models
            logger.info("Using LARGE scale preset: all queries, all models")
    
    # Override with explicit limit if provided
    if args.limit is not None:
        query_limit = args.limit
    
    # Load queries
    if args.use_test_prompts:
        queries = TestPrompts.get_all_queries()
        logger.info(f"Using {len(queries)} built-in test prompts")
    else:
        queries = load_queries(args.queries)
        logger.info(f"Loaded {len(queries)} queries from {args.queries}")
    
    # Apply query limit if specified
    if query_limit and len(queries) > query_limit:
        queries = queries[:query_limit]
        logger.info(f"Limited to {len(queries)} queries (scale preset)")
    
    if not queries:
        logger.error("No queries to benchmark!")
        return
    
    # Detect available models
    config = BenchmarkConfig()
    available_models = asyncio.run(config.detect_available_models())
    
    # Filter models based on --models argument (or scale preset)
    models_to_test = []
    for model in available_models:
        if models_filter == "all":
            models_to_test.append({
                "provider": model.provider,
                "model": model.model_name,
                "display_name": model.display_name
            })
        elif models_filter == "ollama" and model.provider == "ollama":
            models_to_test.append({
                "provider": model.provider,
                "model": model.model_name,
                "display_name": model.display_name
            })
        elif models_filter == "openai" and model.provider == "openai":
            models_to_test.append({
                "provider": model.provider,
                "model": model.model_name,
                "display_name": model.display_name
            })
    
    # For small scale, limit to first 2 models if more available
    if args.scale == "small" and len(models_to_test) > 2:
        models_to_test = models_to_test[:2]
        logger.info(f"Limited to {len(models_to_test)} models for small scale")
    
    if not models_to_test:
        logger.error("No models available for benchmarking!")
        return
    
    logger.info(f"Testing {len(models_to_test)} models: {[m['display_name'] for m in models_to_test]}")
    
    # Run benchmarks
    logger.info("Starting benchmarks...")
    all_results = asyncio.run(run_all_benchmarks(queries, models_to_test, args.mode))
    
    # Generate reports
    report_gen = ReportGenerator()
    report_gen.add_results(all_results)
    report_paths = report_gen.generate_all_reports(args.out)
    
    logger.info(f"Benchmark complete! Reports saved to {args.out}")
    logger.info(f"  JSON: {report_paths['json']}")
    logger.info(f"  CSV: {report_paths['csv']}")


if __name__ == "__main__":
    main()
