#!/usr/bin/env python3
"""
Educational Tutoring Benchmark (ETB) Script
Comprehensive evaluation based on peer-reviewed methodologies:
- Maurya et al. (NAACL 2025): 8 pedagogical dimensions
- MathTutorBench (EMNLP 2025): Dialog-based evaluation
- Chen et al. (IJAED 2025): Domain-specific assessment
"""

import argparse
import asyncio
import sys
import os
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend_python'))

# Add scripts/benchmarks to path
benchmarks_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, benchmarks_dir)

from services.benchmark_config import BenchmarkConfig
from services.llm_service import HybridLLMService, LLMProvider
from services.query_handler import QueryHandler
from pedagogical_evaluator import PedagogicalEvaluator
from dialog_evaluator import DialogEvaluator
from domain_evaluator import DomainEvaluator

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


def load_etb_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """
    Load ETB dataset from JSON file.
    
    Expected format: MRBench-inspired structure with conversations and metadata
    """
    if logger is None:
        setup_logging()
    
    if not os.path.exists(dataset_path):
        if logger:
            logger.warning(f"Dataset file not found: {dataset_path}")
        return []
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if logger:
        logger.info(f"Loaded {len(data)} conversations from ETB dataset")
    return data


async def benchmark_single_turn(
    llm_service: HybridLLMService,
    query_handler: QueryHandler,
    pedagogical_evaluator: PedagogicalEvaluator,
    dialog_evaluator: DialogEvaluator,
    domain_evaluator: DomainEvaluator,
    provider: LLMProvider,
    model_name: str,
    question_data: Dict[str, Any],
    mode: str = "exploration"
) -> Dict[str, Any]:
    """
    Benchmark a single-turn question using all three evaluators.
    
    Returns:
        Dictionary with comprehensive evaluation results
    """
    start_time = time.perf_counter()
    error = None
    response_content = ""
    retrieved_context_chunks = []
    
    # Extract question data
    turn = question_data["turns"][0] if question_data["turns"] else {}
    student_query = turn.get("content", "")
    student_mistakes = turn.get("student_mistakes")
    domain = question_data.get("domain", "unknown")
    metadata = question_data.get("metadata", {})
    expected_key_points = metadata.get("expected_key_points")
    ground_truth_facts = metadata.get("ground_truth_facts")
    
    try:
        # Get context from vector DB
        context_chunks = await query_handler._get_relevant_context(student_query)
        retrieved_context_chunks = [
            chunk.get('content', '') if isinstance(chunk, dict) else str(chunk)
            for chunk in context_chunks
        ]
        
        # Build prompt
        context_text = query_handler._build_context_text(context_chunks)
        prompt = query_handler.prompt_templates.create_tutor_prompt(
            query=student_query,
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
        
        # Generate response
        response = await llm_service.generate_response_with_provider(
            messages=messages,
            provider=provider,
            model=model_name,
            max_tokens=1000,
            temperature=0.7
        )
        
        response_content = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        error = str(e)
        logger.error(f"Error benchmarking {provider.value}:{model_name} with question '{student_query[:50]}...': {e}")
        response_content = ""
        response = None
    
    latency_ms = (time.perf_counter() - start_time) * 1000.0
    
    # Evaluate using all three evaluators
    pedagogical_scores = pedagogical_evaluator.evaluate_response(
        response=response_content,
        student_query=student_query,
        student_mistakes=student_mistakes,
        retrieved_context=retrieved_context_chunks
    )
    
    # Single-turn dialog evaluation (basic)
    dialog_scores = dialog_evaluator._evaluate_single_turn(student_query, response_content)
    
    domain_scores = domain_evaluator.evaluate_response(
        response=response_content,
        domain=domain,
        expected_key_points=expected_key_points,
        ground_truth_facts=ground_truth_facts
    )
    
    # Extract token usage
    usage = {}
    if response and hasattr(response, 'usage'):
        usage = response.usage or {}
    
    result = {
        "conversation_id": question_data.get("conversation_id"),
        "type": question_data.get("type", "single_turn"),
        "question": student_query,
        "response": response_content,
        "provider": provider.value,
        "model": model_name,
        "domain": domain,
        "difficulty": question_data.get("difficulty", "unknown"),
        "question_type": question_data.get("question_type", "unknown"),
        "latency_ms": round(latency_ms, 2),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        # Pedagogical scores (8 dimensions)
        "pedagogical_scores": pedagogical_scores,
        # Dialog scores
        "dialog_scores": dialog_scores,
        # Domain scores
        "domain_scores": domain_scores,
        # Overall scores
        "overall_pedagogical_score": pedagogical_scores.get("overall_pedagogical_score", 0.0),
        "overall_dialog_score": dialog_scores.get("overall_dialog_score", 0.0),
        "overall_domain_score": domain_scores.get("overall_domain_score", 0.0),
        # Combined overall score
        "overall_etb_score": (
            pedagogical_scores.get("overall_pedagogical_score", 0.0) * 0.5 +
            dialog_scores.get("overall_dialog_score", 0.0) * 0.2 +
            domain_scores.get("overall_domain_score", 0.0) * 0.3
        ),
        "error": error,
        "status": "error" if error else "success",
        "timestamp": datetime.now().isoformat()
    }
    
    return result


async def benchmark_multi_turn(
    llm_service: HybridLLMService,
    query_handler: QueryHandler,
    pedagogical_evaluator: PedagogicalEvaluator,
    dialog_evaluator: DialogEvaluator,
    domain_evaluator: DomainEvaluator,
    provider: LLMProvider,
    model_name: str,
    conversation_data: Dict[str, Any],
    mode: str = "exploration"
) -> Dict[str, Any]:
    """
    Benchmark a multi-turn conversation.
    
    Returns:
        Dictionary with comprehensive evaluation results
    """
    start_time = time.perf_counter()
    error = None
    responses = []
    all_context_chunks = []
    conversation_history = []
    
    turns = conversation_data.get("turns", [])
    domain = conversation_data.get("domain", "unknown")
    metadata = conversation_data.get("metadata", {})
    
    try:
        # Process each turn
        for turn in turns:
            if turn.get("role") != "student":
                continue
            
            student_query = turn.get("content", "")
            student_mistakes = turn.get("student_mistakes")
            
            # Get context
            context_chunks = await query_handler._get_relevant_context(student_query)
            context_text = query_handler._build_context_text(context_chunks)
            all_context_chunks.extend([
                chunk.get('content', '') if isinstance(chunk, dict) else str(chunk)
                for chunk in context_chunks
            ])
            
            # Build conversation history (QueryHandler expects 'message' key)
            history_text = query_handler._build_conversation_history(conversation_history)
            
            # Build prompt
            prompt = query_handler.prompt_templates.create_tutor_prompt(
                query=student_query,
                context=context_text,
                conversation_history=history_text,
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
            
            # Generate response
            response = await llm_service.generate_response_with_provider(
                messages=messages,
                provider=provider,
                model=model_name,
                max_tokens=1000,
                temperature=0.7
            )
            
            response_content = response.content if hasattr(response, 'content') else str(response)
            responses.append(response_content)
            # Store in format compatible with QueryHandler (uses 'message' key)
            conversation_history.append({"role": "user", "message": student_query})
            conversation_history.append({"role": "assistant", "message": response_content})
            
            # Small delay between turns
            await asyncio.sleep(0.3)
        
    except Exception as e:
        error = str(e)
        logger.error(f"Error benchmarking multi-turn conversation: {e}")
    
    latency_ms = (time.perf_counter() - start_time) * 1000.0
    
    # Extract student queries and tutor responses
    student_queries = [t.get("content", "") for t in turns if t.get("role") == "student"]
    
    # Evaluate conversation
    dialog_scores = dialog_evaluator.evaluate_conversation(
        conversation=turns,
        student_queries=student_queries,
        tutor_responses=responses
    )
    
    # Evaluate each response pedagogically
    pedagogical_scores_list = []
    for i, (query, response) in enumerate(zip(student_queries, responses)):
        turn = turns[i * 2] if i * 2 < len(turns) else {}
        mistakes = turn.get("student_mistakes")
        
        scores = pedagogical_evaluator.evaluate_response(
            response=response,
            student_query=query,
            student_mistakes=mistakes,
            conversation_history=conversation_history[:i*2] if i > 0 else None,
            retrieved_context=all_context_chunks
        )
        pedagogical_scores_list.append(scores)
    
    # Average pedagogical scores
    avg_pedagogical = {}
    if pedagogical_scores_list:
        for key in pedagogical_scores_list[0].keys():
            avg_pedagogical[key] = sum(s[key] for s in pedagogical_scores_list) / len(pedagogical_scores_list)
    else:
        # Empty scores if no responses
        avg_pedagogical = {
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
    
    # Domain evaluation (use first turn's domain)
    domain_scores = domain_evaluator.evaluate_response(
        response=" ".join(responses),
        domain=domain,
        expected_key_points=metadata.get("expected_key_points"),
        ground_truth_facts=metadata.get("ground_truth_facts")
    )
    
    result = {
        "conversation_id": conversation_data.get("conversation_id"),
        "type": "multi_turn",
        "student_queries": student_queries,
        "responses": responses,
        "provider": provider.value,
        "model": model_name,
        "domain": domain,
        "difficulty": conversation_data.get("difficulty", "unknown"),
        "question_type": conversation_data.get("question_type", "unknown"),
        "num_turns": len(student_queries),
        "latency_ms": round(latency_ms, 2),
        # Pedagogical scores (averaged across turns)
        "pedagogical_scores": avg_pedagogical,
        # Dialog scores
        "dialog_scores": dialog_scores,
        # Domain scores
        "domain_scores": domain_scores,
        # Overall scores
        "overall_pedagogical_score": avg_pedagogical.get("overall_pedagogical_score", 0.0),
        "overall_dialog_score": dialog_scores.get("overall_dialog_score", 0.0),
        "overall_domain_score": domain_scores.get("overall_domain_score", 0.0),
        # Combined overall score
        "overall_etb_score": (
            avg_pedagogical.get("overall_pedagogical_score", 0.0) * 0.5 +
            dialog_scores.get("overall_dialog_score", 0.0) * 0.2 +
            domain_scores.get("overall_domain_score", 0.0) * 0.3
        ),
        "error": error,
        "status": "error" if error else "success",
        "timestamp": datetime.now().isoformat()
    }
    
    return result


async def run_etb_benchmark(
    dataset: List[Dict[str, Any]],
    models: List[Dict[str, Any]],
    mode: str = "exploration",
    include_conversations: bool = True
) -> List[Dict[str, Any]]:
    """Run ETB benchmark for all models and questions."""
    # Initialize services
    llm_service = HybridLLMService()
    await llm_service.initialize()
    
    query_handler = QueryHandler()
    await query_handler._ensure_llm_service_initialized()
    
    pedagogical_evaluator = PedagogicalEvaluator()
    dialog_evaluator = DialogEvaluator()
    domain_evaluator = DomainEvaluator()
    
    all_results = []
    
    # Test each model
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
        
        logger.info(f"Benchmarking {provider_name}:{model_name} with {len(dataset)} ETB questions")
        
        for i, question_data in enumerate(dataset, 1):
            conversation_id = question_data.get("conversation_id", f"unknown-{i}")
            question_type = question_data.get("type", "single_turn")
            
            # Skip multi-turn if not requested
            if question_type == "multi_turn" and not include_conversations:
                continue
            
            student_query = ""
            if question_data.get("turns"):
                first_turn = question_data["turns"][0]
                student_query = first_turn.get("content", "")
            
            logger.info(f"  [{i}/{len(dataset)}] Testing: {conversation_id} - {student_query[:60]}...")
            
            try:
                if question_type == "multi_turn":
                    result = await benchmark_multi_turn(
                        llm_service=llm_service,
                        query_handler=query_handler,
                        pedagogical_evaluator=pedagogical_evaluator,
                        dialog_evaluator=dialog_evaluator,
                        domain_evaluator=domain_evaluator,
                        provider=provider,
                        model_name=model_name,
                        conversation_data=question_data,
                        mode=mode
                    )
                else:
                    result = await benchmark_single_turn(
                        llm_service=llm_service,
                        query_handler=query_handler,
                        pedagogical_evaluator=pedagogical_evaluator,
                        dialog_evaluator=dialog_evaluator,
                        domain_evaluator=domain_evaluator,
                        provider=provider,
                        model_name=model_name,
                        question_data=question_data,
                        mode=mode
                    )
                all_results.append(result)
            except Exception as e:
                logger.error(f"Failed to benchmark {conversation_id}: {e}")
                all_results.append({
                    "conversation_id": conversation_id,
                    "provider": provider_name,
                    "model": model_name,
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Small delay between questions
            await asyncio.sleep(0.5)
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description="Educational Tutoring Benchmark (ETB) Runner")
    parser.add_argument(
        "--dataset",
        default="scripts/benchmarks/etb_dataset.json",
        help="Path to ETB dataset JSON file"
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
        default="backend_python/logs/benchmarks/etb",
        help="Output directory for ETB reports"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of questions to test (for quick testing)"
    )
    parser.add_argument(
        "--conversations",
        action="store_true",
        help="Include multi-turn conversations in benchmark"
    )
    parser.add_argument(
        "--scale",
        choices=["small", "medium", "large"],
        default=None,
        help="Benchmark scale preset: small (5 questions, 1-2 models), medium (15 questions, 2-3 models), large (all questions, all models)"
    )
    args = parser.parse_args()
    
    setup_logging()
    
    # Apply scale presets if specified
    question_limit = args.limit
    models_filter = args.models
    include_conversations = args.conversations
    
    if args.scale:
        if args.scale == "small":
            question_limit = 5 if question_limit is None else min(question_limit, 5)
            if args.models == "all":
                models_filter = "ollama"  # Default to ollama for small scale
            include_conversations = False  # Skip conversations for small scale
            logger.info("Using SMALL scale preset: 5 questions, 1-2 models, no conversations")
        elif args.scale == "medium":
            question_limit = 15 if question_limit is None else min(question_limit, 15)
            logger.info("Using MEDIUM scale preset: 15 questions, 2-3 models")
        elif args.scale == "large":
            question_limit = None  # Use all questions
            if args.models == "all":
                models_filter = "all"  # Use all models
            include_conversations = True  # Include conversations for large scale
            logger.info("Using LARGE scale preset: all questions, all models, with conversations")
    
    # Load ETB dataset
    dataset = load_etb_dataset(args.dataset)
    
    if not dataset:
        logger.error("No ETB dataset loaded! Please provide a valid dataset file.")
        return
    
    # Limit dataset if specified
    if question_limit and len(dataset) > question_limit:
        dataset = dataset[:question_limit]
        logger.info(f"Limited to {len(dataset)} questions (scale preset)")
    
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
    logger.info(f"Running ETB benchmark on {len(dataset)} questions")
    if include_conversations:
        logger.info("Including multi-turn conversations")
    
    # Run benchmarks
    logger.info("Starting ETB benchmarks...")
    all_results = asyncio.run(run_etb_benchmark(
        dataset=dataset,
        models=models_to_test,
        mode=args.mode,
        include_conversations=include_conversations
    ))
    
    # Generate ETB reports
    from etb_report_generator import ETBReportGenerator
    report_gen = ETBReportGenerator()
    report_gen.add_results(all_results)
    report_paths = report_gen.generate_all_reports(args.out)
    
    logger.info(f"ETB benchmark complete! Reports saved to {args.out}")
    logger.info(f"  JSON: {report_paths['json']}")
    logger.info(f"  CSV: {report_paths['csv']}")
    logger.info(f"  Summary: {report_paths.get('summary', 'N/A')}")


if __name__ == "__main__":
    main()

