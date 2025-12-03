"""
Report Generator Module
Generates comparison reports from benchmark results.
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from statistics import mean, median, stdev
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates benchmark comparison reports."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    def add_results(self, results: List[Dict[str, Any]]):
        """Add benchmark results."""
        self.results.extend(results)
    
    def generate_all_reports(self, output_dir: str):
        """Generate all report formats."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate JSON report
        json_path = os.path.join(output_dir, f"benchmark_report_{timestamp}.json")
        self.generate_json_report(json_path)
        
        # Generate CSV report
        csv_path = os.path.join(output_dir, f"benchmark_report_{timestamp}.csv")
        self.generate_csv_report(csv_path)
        
        # Print console summary
        self.print_summary()
        
        return {
            "json": json_path,
            "csv": csv_path
        }
    
    def generate_json_report(self, output_path: str):
        """Generate JSON report with aggregated statistics."""
        aggregated = self._aggregate_results()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(self.results),
            "models_tested": list(aggregated.keys()),
            "summary": aggregated,
            "detailed_results": self.results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON report saved to {output_path}")
    
    def generate_csv_report(self, output_path: str):
        """Generate CSV report for spreadsheet analysis."""
        if not self.results:
            logger.warning("No results to write to CSV")
            return
        
        # Flatten results for CSV
        rows = []
        for result in self.results:
            row = {
                "query": result.get("query", ""),
                "model": result.get("model", ""),
                "provider": result.get("provider", ""),
                "latency_ms": result.get("latency_ms", 0),
                "response_length": result.get("response_length", 0),
                "prompt_tokens": result.get("prompt_tokens", 0),
                "completion_tokens": result.get("completion_tokens", 0),
                "total_tokens": result.get("total_tokens", 0),
                "self_check_confidence": result.get("self_check_confidence", 0),
                "citation_score": result.get("citation_score", 0),
                "completeness_score": result.get("completeness_score", 0),
                "quality_score": result.get("quality_score", 0),
                "overall_score": result.get("overall_score", 0),
                "error": result.get("error", ""),
                "status": result.get("status", "")
            }
            rows.append(row)
        
        if rows:
            fieldnames = rows[0].keys()
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            logger.info(f"CSV report saved to {output_path}")
    
    def _aggregate_results(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate results by model."""
        aggregated = {}
        
        # Group by model
        by_model: Dict[str, List[Dict[str, Any]]] = {}
        for result in self.results:
            model_key = f"{result.get('provider', 'unknown')}:{result.get('model', 'unknown')}"
            if model_key not in by_model:
                by_model[model_key] = []
            by_model[model_key].append(result)
        
        # Calculate statistics for each model
        for model_key, model_results in by_model.items():
            latencies = [r.get("latency_ms", 0) for r in model_results if isinstance(r.get("latency_ms"), (int, float))]
            total_tokens = [r.get("total_tokens", 0) for r in model_results if isinstance(r.get("total_tokens"), (int, float))]
            confidences = [r.get("self_check_confidence", 0) for r in model_results if isinstance(r.get("self_check_confidence"), (int, float))]
            overall_scores = [r.get("overall_score", 0) for r in model_results if isinstance(r.get("overall_score"), (int, float))]
            errors = [r for r in model_results if r.get("error") or r.get("status") == "error"]
            
            aggregated[model_key] = {
                "total_queries": len(model_results),
                "successful_queries": len(model_results) - len(errors),
                "error_rate": len(errors) / len(model_results) if model_results else 0,
                "latency_ms": {
                    "mean": mean(latencies) if latencies else 0,
                    "median": median(latencies) if latencies else 0,
                    "stdev": stdev(latencies) if len(latencies) > 1 else 0,
                    "min": min(latencies) if latencies else 0,
                    "max": max(latencies) if latencies else 0
                },
                "tokens": {
                    "mean": mean(total_tokens) if total_tokens else 0,
                    "median": median(total_tokens) if total_tokens else 0,
                    "total": sum(total_tokens) if total_tokens else 0
                },
                "relevance": {
                    "mean_confidence": mean(confidences) if confidences else 0,
                    "mean_overall_score": mean(overall_scores) if overall_scores else 0
                }
            }
        
        return aggregated
    
    def print_summary(self):
        """Print console summary of results."""
        if not self.results:
            print("No results to summarize")
            return
        
        aggregated = self._aggregate_results()
        
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        print(f"Total queries: {len(self.results)}")
        print(f"Models tested: {len(aggregated)}")
        print("\nModel Performance:")
        print("-"*80)
        
        for model_key, stats in aggregated.items():
            print(f"\n{model_key}:")
            print(f"  Queries: {stats['successful_queries']}/{stats['total_queries']} successful")
            print(f"  Error rate: {stats['error_rate']:.2%}")
            if stats['latency_ms']['mean'] > 0:
                print(f"  Avg latency: {stats['latency_ms']['mean']:.2f}ms")
            if stats['tokens']['mean'] > 0:
                print(f"  Avg tokens: {stats['tokens']['mean']:.0f}")
            if stats['relevance']['mean_confidence'] > 0:
                print(f"  Avg confidence: {stats['relevance']['mean_confidence']:.3f}")
            if stats['relevance']['mean_overall_score'] > 0:
                print(f"  Avg overall score: {stats['relevance']['mean_overall_score']:.3f}")
        
        print("\n" + "="*80)
    
    def rank_models(self, metric: str = "overall_score") -> List[tuple]:
        """
        Rank models by a specific metric.
        
        Args:
            metric: Metric to rank by (overall_score, latency_ms, total_tokens, etc.)
            
        Returns:
            List of (model_key, value) tuples sorted by value
        """
        aggregated = self._aggregate_results()
        rankings = []
        
        for model_key, stats in aggregated.items():
            if metric == "overall_score":
                value = stats['relevance']['mean_overall_score']
            elif metric == "latency_ms":
                value = stats['latency_ms']['mean']
            elif metric == "total_tokens":
                value = stats['tokens']['mean']
            elif metric == "confidence":
                value = stats['relevance']['mean_confidence']
            else:
                value = 0
            
            rankings.append((model_key, value))
        
        # Sort by value (descending for scores, ascending for latency/tokens)
        reverse = metric in ["overall_score", "confidence"]
        rankings.sort(key=lambda x: x[1], reverse=reverse)
        
        return rankings


# Global report generator instance
report_generator = ReportGenerator()

