#!/usr/bin/env python3
"""
Model Detection Utility
Lists available Ollama models for benchmarking.
"""

import sys
import os
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend_python'))

from services.benchmark_config import BenchmarkConfig


async def main():
    """Detect and list available models."""
    config = BenchmarkConfig()
    
    print("Detecting available models...")
    print("-" * 60)
    
    # Detect Ollama models
    ollama_models = await config._detect_ollama_models()
    
    print(f"\nOllama Models Found: {len(ollama_models)}")
    for model in ollama_models:
        # Check if it's one of our target models
        is_target = model in config.DEFAULT_OLLAMA_MODELS
        status = "✓ TARGET" if is_target else ""
        print(f"  - {model} {status}")
    
    print(f"\nTarget Ollama Models:")
    for model in config.DEFAULT_OLLAMA_MODELS:
        available = model in ollama_models
        status = "✓ Available" if available else "✗ Not available"
        print(f"  - {model}: {status}")
    
    print(f"\nTarget OpenAI Model:")
    print(f"  - {config.DEFAULT_OPENAI_MODEL}: (check availability during benchmark)")
    
    print("\n" + "-" * 60)
    print("To run benchmarks, use:")
    print("  python scripts/benchmarks/benchmark.py --queries scripts/benchmarks/queries.txt")


if __name__ == "__main__":
    asyncio.run(main())

