#!/usr/bin/env python3
"""
Quick script to view benchmark results summary.
"""

import json
import glob
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend_python to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend_python"))

def find_latest_report():
    """Find the most recent benchmark report."""
    reports_dir = project_root / "backend_python" / "logs" / "benchmarks"
    reports = list(reports_dir.glob("benchmark_report_*.json"))
    
    if not reports:
        print("No benchmark reports found.")
        return None
    
    latest = max(reports, key=os.path.getmtime)
    return latest

def view_summary(report_path):
    """View summary of benchmark results."""
    with open(report_path, 'r') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 80)
    print(f"Report: {report_path.name}")
    print(f"Timestamp: {data.get('timestamp', 'N/A')}")
    print(f"Total queries tested: {data.get('total_queries', 0)}")
    print(f"Models tested: {len(data.get('models_tested', []))}")
    
    if 'models_tested' in data:
        print(f"\nModels: {', '.join(data['models_tested'])}")
    
    if 'summary' in data and data['summary']:
        print("\n" + "-" * 80)
        print("MODEL PERFORMANCE")
        print("-" * 80)
        
        for model_key, stats in data['summary'].items():
            print(f"\n{model_key}:")
            print(f"  Queries: {stats.get('successful_queries', 0)}/{stats.get('total_queries', 0)} successful")
            print(f"  Error rate: {stats.get('error_rate', 0):.2%}")
            
            latency = stats.get('latency_ms', {})
            if latency.get('mean', 0) > 0:
                print(f"  Avg latency: {latency.get('mean', 0):.2f}ms")
            
            tokens = stats.get('tokens', {})
            if tokens.get('mean', 0) > 0:
                print(f"  Avg tokens: {tokens.get('mean', 0):.0f}")
                print(f"  Total tokens: {tokens.get('total', 0):.0f}")
            
            relevance = stats.get('relevance', {})
            if relevance.get('mean_confidence', 0) > 0:
                print(f"  Avg confidence: {relevance.get('mean_confidence', 0):.3f}")
            if relevance.get('mean_overall_score', 0) > 0:
                print(f"  Avg overall score: {relevance.get('mean_overall_score', 0):.3f}")
    
    if 'detailed_results' in data and data['detailed_results']:
        print("\n" + "-" * 80)
        print("SAMPLE RESULTS (first 5)")
        print("-" * 80)
        for i, result in enumerate(data['detailed_results'][:5], 1):
            print(f"\n{i}. Query: {result.get('query', 'N/A')[:60]}...")
            print(f"   Model: {result.get('provider', 'N/A')}:{result.get('model', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            if result.get('latency_ms'):
                print(f"   Latency: {result.get('latency_ms'):.0f}ms")
            if result.get('quality_score'):
                print(f"   Quality: {result.get('quality_score'):.3f}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    report = find_latest_report()
    if report:
        view_summary(report)
    else:
        print("\nRun benchmarks first:")
        print("  python scripts/benchmarks/benchmark.py --queries scripts/benchmarks/queries.txt --models ollama")
