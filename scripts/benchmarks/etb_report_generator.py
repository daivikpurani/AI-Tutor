"""
ETB Report Generator Module
Generates comprehensive reports for Educational Tutoring Benchmark.
Based on peer-reviewed methodologies from NAACL 2025, EMNLP 2025, and IJAED 2025.
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from statistics import mean, median, stdev
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ETBReportGenerator:
    """Generates comprehensive ETB benchmark reports."""
    
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
        json_path = os.path.join(output_dir, f"etb_benchmark_{timestamp}.json")
        self.generate_json_report(json_path)
        
        # Generate CSV report
        csv_path = os.path.join(output_dir, f"etb_benchmark_{timestamp}.csv")
        self.generate_csv_report(csv_path)
        
        # Generate summary report
        summary_path = os.path.join(output_dir, f"etb_summary_{timestamp}.txt")
        self.generate_summary_report(summary_path)
        
        # Generate pedagogical dimensions report
        pedagogical_path = os.path.join(output_dir, f"etb_pedagogical_dimensions_{timestamp}.json")
        self.generate_pedagogical_report(pedagogical_path)
        
        # Generate dialog analysis report
        dialog_path = os.path.join(output_dir, f"etb_dialog_analysis_{timestamp}.json")
        self.generate_dialog_report(dialog_path)
        
        # Generate domain analysis report
        domain_path = os.path.join(output_dir, f"etb_domain_analysis_{timestamp}.json")
        self.generate_domain_report(domain_path)
        
        # Generate comparative analysis report
        comparative_path = os.path.join(output_dir, f"etb_comparative_analysis_{timestamp}.json")
        self.generate_comparative_report(comparative_path)
        
        # Print console summary
        self.print_summary()
        
        return {
            "json": json_path,
            "csv": csv_path,
            "summary": summary_path,
            "pedagogical": pedagogical_path,
            "dialog": dialog_path,
            "domain": domain_path,
            "comparative": comparative_path
        }
    
    def generate_json_report(self, output_path: str):
        """Generate comprehensive JSON report."""
        aggregated = self._aggregate_results()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_evaluations": len(self.results),
            "models_tested": list(aggregated.keys()),
            "summary": aggregated,
            "by_pedagogical_dimension": self._aggregate_by_pedagogical_dimension(),
            "by_domain": self._aggregate_by_domain(),
            "by_difficulty": self._aggregate_by_difficulty(),
            "by_question_type": self._aggregate_by_question_type(),
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
        
        rows = []
        for result in self.results:
            # Flatten nested scores for CSV
            pedagogical = result.get("pedagogical_scores", {})
            dialog = result.get("dialog_scores", {})
            domain = result.get("domain_scores", {})
            
            row = {
                "conversation_id": result.get("conversation_id", ""),
                "type": result.get("type", ""),
                "question": result.get("question", ""),
                "model": result.get("model", ""),
                "provider": result.get("provider", ""),
                "domain": result.get("domain", ""),
                "difficulty": result.get("difficulty", ""),
                "question_type": result.get("question_type", ""),
                # Pedagogical dimensions
                "mistake_identification": pedagogical.get("mistake_identification", 0),
                "mistake_location": pedagogical.get("mistake_location", 0),
                "revealing_answer": pedagogical.get("revealing_answer", 0),
                "providing_guidance": pedagogical.get("providing_guidance", 0),
                "actionability": pedagogical.get("actionability", 0),
                "coherence": pedagogical.get("coherence", 0),
                "tutor_tone": pedagogical.get("tutor_tone", 0),
                "human_likeness": pedagogical.get("human_likeness", 0),
                "overall_pedagogical_score": pedagogical.get("overall_pedagogical_score", 0),
                # Dialog scores
                "dialog_coherence": dialog.get("dialog_coherence", 0),
                "context_retention": dialog.get("context_retention", 0),
                "learning_progression": dialog.get("learning_progression", 0),
                "pedagogical_consistency": dialog.get("pedagogical_consistency", 0),
                "student_engagement": dialog.get("student_engagement", 0),
                "overall_dialog_score": dialog.get("overall_dialog_score", 0),
                # Domain scores
                "domain_accuracy": domain.get("domain_accuracy", 0),
                "terminology_correctness": domain.get("terminology_correctness", 0),
                "technical_depth": domain.get("technical_depth", 0),
                "practical_relevance": domain.get("practical_relevance", 0),
                "overall_domain_score": domain.get("overall_domain_score", 0),
                # Overall scores
                "overall_etb_score": result.get("overall_etb_score", 0),
                "latency_ms": result.get("latency_ms", 0),
                "total_tokens": result.get("total_tokens", 0),
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
    
    def generate_summary_report(self, output_path: str):
        """Generate human-readable summary report."""
        aggregated = self._aggregate_results()
        by_dimension = self._aggregate_by_pedagogical_dimension()
        by_domain = self._aggregate_by_domain()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("EDUCATIONAL TUTORING BENCHMARK (ETB) - SUMMARY REPORT\n")
            f.write("Based on: Maurya et al. (NAACL 2025), MathTutorBench (EMNLP 2025), Chen et al. (IJAED 2025)\n")
            f.write("="*80 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Total Evaluations: {len(self.results)}\n")
            f.write(f"Models Tested: {len(aggregated)}\n\n")
            
            # Overall performance by model
            f.write("OVERALL PERFORMANCE BY MODEL\n")
            f.write("-"*80 + "\n")
            for model_key, stats in aggregated.items():
                f.write(f"\n{model_key}:\n")
                f.write(f"  Evaluations: {stats['total_evaluations']}\n")
                f.write(f"  Overall ETB Score: {stats['overall_etb_score']['mean']:.3f}\n")
                f.write(f"  Overall Pedagogical Score: {stats['overall_pedagogical_score']['mean']:.3f}\n")
                f.write(f"  Overall Dialog Score: {stats['overall_dialog_score']['mean']:.3f}\n")
                f.write(f"  Overall Domain Score: {stats['overall_domain_score']['mean']:.3f}\n")
                f.write(f"  Avg Latency: {stats['latency_ms']['mean']:.2f}ms\n")
            
            # Performance by pedagogical dimension
            f.write("\n\nPERFORMANCE BY PEDAGOGICAL DIMENSION (8 Dimensions)\n")
            f.write("-"*80 + "\n")
            dimensions = [
                "mistake_identification", "mistake_location", "revealing_answer",
                "providing_guidance", "actionability", "coherence", "tutor_tone", "human_likeness"
            ]
            for dim in dimensions:
                if dim in by_dimension:
                    stats = by_dimension[dim]
                    f.write(f"\n{dim.replace('_', ' ').title()}:\n")
                    f.write(f"  Mean Score: {stats['mean']:.3f}\n")
                    f.write(f"  Min: {stats['min']:.3f}, Max: {stats['max']:.3f}\n")
            
            # Performance by domain
            f.write("\n\nPERFORMANCE BY DOMAIN\n")
            f.write("-"*80 + "\n")
            for domain, stats in by_domain.items():
                f.write(f"\n{domain}:\n")
                f.write(f"  Evaluations: {stats['total_evaluations']}\n")
                f.write(f"  Mean Domain Score: {stats['overall_domain_score']['mean']:.3f}\n")
                f.write(f"  Mean Domain Accuracy: {stats['domain_accuracy']['mean']:.3f}\n")
            
            # Model rankings
            f.write("\n\nMODEL RANKINGS\n")
            f.write("-"*80 + "\n")
            rankings = self._rank_models()
            for i, (model_key, score) in enumerate(rankings, 1):
                f.write(f"{i}. {model_key}: {score:.3f}\n")
        
        logger.info(f"Summary report saved to {output_path}")
    
    def generate_pedagogical_report(self, output_path: str):
        """Generate detailed pedagogical dimensions report."""
        by_dimension = self._aggregate_by_pedagogical_dimension()
        by_model_dimension = self._aggregate_by_model_and_dimension()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "dimension_performance": by_dimension,
            "by_model": by_model_dimension,
            "dimension_correlations": self._calculate_dimension_correlations()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pedagogical dimensions report saved to {output_path}")
    
    def generate_dialog_report(self, output_path: str):
        """Generate dialog analysis report."""
        dialog_results = [r for r in self.results if r.get("type") == "multi_turn"]
        by_model_dialog = self._aggregate_dialog_by_model()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_conversations": len(dialog_results),
            "dialog_metrics": {
                "dialog_coherence": self._aggregate_metric("dialog_scores.dialog_coherence"),
                "context_retention": self._aggregate_metric("dialog_scores.context_retention"),
                "learning_progression": self._aggregate_metric("dialog_scores.learning_progression"),
                "pedagogical_consistency": self._aggregate_metric("dialog_scores.pedagogical_consistency"),
                "student_engagement": self._aggregate_metric("dialog_scores.student_engagement")
            },
            "by_model": by_model_dialog
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dialog analysis report saved to {output_path}")
    
    def generate_domain_report(self, output_path: str):
        """Generate domain-specific analysis report."""
        by_domain = self._aggregate_by_domain()
        by_model_domain = self._aggregate_by_model_and_domain()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "domain_performance": by_domain,
            "by_model": by_model_domain,
            "domain_comparison": self._compare_domains()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Domain analysis report saved to {output_path}")
    
    def generate_comparative_report(self, output_path: str):
        """Generate comparative analysis report."""
        rankings = self._rank_models()
        strengths_weaknesses = self._analyze_strengths_weaknesses()
        best_models = self._find_best_models_per_metric()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "model_rankings": {
                "overall_etb_score": rankings,
                "pedagogical_score": self._rank_models("overall_pedagogical_score"),
                "dialog_score": self._rank_models("overall_dialog_score"),
                "domain_score": self._rank_models("overall_domain_score")
            },
            "strengths_weaknesses": strengths_weaknesses,
            "best_models_per_metric": best_models,
            "statistical_significance": self._calculate_statistical_significance()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Comparative analysis report saved to {output_path}")
    
    def _aggregate_results(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate results by model."""
        aggregated = {}
        
        # Group by model
        by_model: Dict[str, List[Dict[str, Any]]] = {}
        for result in self.results:
            if result.get("status") == "error":
                continue
            model_key = f"{result.get('provider', 'unknown')}:{result.get('model', 'unknown')}"
            if model_key not in by_model:
                by_model[model_key] = []
            by_model[model_key].append(result)
        
        # Calculate statistics for each model
        for model_key, model_results in by_model.items():
            etb_scores = [r.get("overall_etb_score", 0) for r in model_results if isinstance(r.get("overall_etb_score"), (int, float))]
            pedagogical_scores = [r.get("overall_pedagogical_score", 0) for r in model_results if isinstance(r.get("overall_pedagogical_score"), (int, float))]
            dialog_scores = [r.get("overall_dialog_score", 0) for r in model_results if isinstance(r.get("overall_dialog_score"), (int, float))]
            domain_scores = [r.get("overall_domain_score", 0) for r in model_results if isinstance(r.get("overall_domain_score"), (int, float))]
            latencies = [r.get("latency_ms", 0) for r in model_results if isinstance(r.get("latency_ms"), (int, float))]
            
            aggregated[model_key] = {
                "total_evaluations": len(model_results),
                "overall_etb_score": {
                    "mean": mean(etb_scores) if etb_scores else 0.0,
                    "median": median(etb_scores) if len(etb_scores) > 1 else (etb_scores[0] if etb_scores else 0.0),
                    "stdev": stdev(etb_scores) if len(etb_scores) > 1 else 0.0,
                    "min": min(etb_scores) if etb_scores else 0.0,
                    "max": max(etb_scores) if etb_scores else 0.0
                },
                "overall_pedagogical_score": {
                    "mean": mean(pedagogical_scores) if pedagogical_scores else 0.0,
                    "median": median(pedagogical_scores) if len(pedagogical_scores) > 1 else (pedagogical_scores[0] if pedagogical_scores else 0.0),
                    "stdev": stdev(pedagogical_scores) if len(pedagogical_scores) > 1 else 0.0
                },
                "overall_dialog_score": {
                    "mean": mean(dialog_scores) if dialog_scores else 0.0,
                    "median": median(dialog_scores) if len(dialog_scores) > 1 else (dialog_scores[0] if dialog_scores else 0.0),
                    "stdev": stdev(dialog_scores) if len(dialog_scores) > 1 else 0.0
                },
                "overall_domain_score": {
                    "mean": mean(domain_scores) if domain_scores else 0.0,
                    "median": median(domain_scores) if len(domain_scores) > 1 else (domain_scores[0] if domain_scores else 0.0),
                    "stdev": stdev(domain_scores) if len(domain_scores) > 1 else 0.0
                },
                "latency_ms": {
                    "mean": mean(latencies) if latencies else 0.0,
                    "median": median(latencies) if len(latencies) > 1 else (latencies[0] if latencies else 0.0),
                    "stdev": stdev(latencies) if len(latencies) > 1 else 0.0
                }
            }
        
        return aggregated
    
    def _aggregate_by_pedagogical_dimension(self) -> Dict[str, Dict[str, float]]:
        """Aggregate scores by pedagogical dimension."""
        dimensions = [
            "mistake_identification", "mistake_location", "revealing_answer",
            "providing_guidance", "actionability", "coherence", "tutor_tone", "human_likeness"
        ]
        
        aggregated = {}
        for dim in dimensions:
            scores = []
            for result in self.results:
                if result.get("status") == "error":
                    continue
                pedagogical = result.get("pedagogical_scores", {})
                score = pedagogical.get(dim)
                if isinstance(score, (int, float)):
                    scores.append(score)
            
            if scores:
                aggregated[dim] = {
                    "mean": mean(scores),
                    "median": median(scores) if len(scores) > 1 else scores[0],
                    "stdev": stdev(scores) if len(scores) > 1 else 0.0,
                    "min": min(scores),
                    "max": max(scores)
                }
        
        return aggregated
    
    def _aggregate_by_domain(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate results by domain."""
        by_domain = defaultdict(list)
        
        for result in self.results:
            if result.get("status") == "error":
                continue
            domain = result.get("domain", "unknown")
            by_domain[domain].append(result)
        
        aggregated = {}
        for domain, results in by_domain.items():
            domain_scores = [r.get("domain_scores", {}).get("overall_domain_score", 0) for r in results]
            accuracy_scores = [r.get("domain_scores", {}).get("domain_accuracy", 0) for r in results]
            
            aggregated[domain] = {
                "total_evaluations": len(results),
                "overall_domain_score": {
                    "mean": mean(domain_scores) if domain_scores else 0.0,
                    "median": median(domain_scores) if len(domain_scores) > 1 else (domain_scores[0] if domain_scores else 0.0)
                },
                "domain_accuracy": {
                    "mean": mean(accuracy_scores) if accuracy_scores else 0.0,
                    "median": median(accuracy_scores) if len(accuracy_scores) > 1 else (accuracy_scores[0] if accuracy_scores else 0.0)
                }
            }
        
        return aggregated
    
    def _aggregate_by_difficulty(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate results by difficulty level."""
        by_difficulty = defaultdict(list)
        
        for result in self.results:
            if result.get("status") == "error":
                continue
            difficulty = result.get("difficulty", "unknown")
            by_difficulty[difficulty].append(result)
        
        aggregated = {}
        for difficulty, results in by_difficulty.items():
            etb_scores = [r.get("overall_etb_score", 0) for r in results]
            aggregated[difficulty] = {
                "total_evaluations": len(results),
                "mean_etb_score": mean(etb_scores) if etb_scores else 0.0
            }
        
        return aggregated
    
    def _aggregate_by_question_type(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate results by question type."""
        by_type = defaultdict(list)
        
        for result in self.results:
            if result.get("status") == "error":
                continue
            q_type = result.get("question_type", "unknown")
            by_type[q_type].append(result)
        
        aggregated = {}
        for q_type, results in by_type.items():
            etb_scores = [r.get("overall_etb_score", 0) for r in results]
            aggregated[q_type] = {
                "total_evaluations": len(results),
                "mean_etb_score": mean(etb_scores) if etb_scores else 0.0
            }
        
        return aggregated
    
    def _aggregate_by_model_and_dimension(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Aggregate pedagogical dimensions by model."""
        by_model = defaultdict(lambda: defaultdict(list))
        
        for result in self.results:
            if result.get("status") == "error":
                continue
            model_key = f"{result.get('provider', 'unknown')}:{result.get('model', 'unknown')}"
            pedagogical = result.get("pedagogical_scores", {})
            
            for dim in ["mistake_identification", "mistake_location", "revealing_answer",
                       "providing_guidance", "actionability", "coherence", "tutor_tone", "human_likeness"]:
                score = pedagogical.get(dim)
                if isinstance(score, (int, float)):
                    by_model[model_key][dim].append(score)
        
        aggregated = {}
        for model_key, dimensions in by_model.items():
            aggregated[model_key] = {}
            for dim, scores in dimensions.items():
                aggregated[model_key][dim] = {
                    "mean": mean(scores),
                    "median": median(scores) if len(scores) > 1 else scores[0]
                }
        
        return aggregated
    
    def _aggregate_dialog_by_model(self) -> Dict[str, Dict[str, float]]:
        """Aggregate dialog metrics by model."""
        dialog_results = [r for r in self.results if r.get("type") == "multi_turn" and r.get("status") != "error"]
        by_model = defaultdict(lambda: defaultdict(list))
        
        for result in dialog_results:
            model_key = f"{result.get('provider', 'unknown')}:{result.get('model', 'unknown')}"
            dialog = result.get("dialog_scores", {})
            
            for metric in ["dialog_coherence", "context_retention", "learning_progression",
                          "pedagogical_consistency", "student_engagement"]:
                score = dialog.get(metric)
                if isinstance(score, (int, float)):
                    by_model[model_key][metric].append(score)
        
        aggregated = {}
        for model_key, metrics in by_model.items():
            aggregated[model_key] = {}
            for metric, scores in metrics.items():
                aggregated[model_key][metric] = {
                    "mean": mean(scores),
                    "median": median(scores) if len(scores) > 1 else scores[0]
                }
        
        return aggregated
    
    def _aggregate_by_model_and_domain(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Aggregate domain scores by model."""
        by_model_domain = defaultdict(lambda: defaultdict(list))
        
        for result in self.results:
            if result.get("status") == "error":
                continue
            model_key = f"{result.get('provider', 'unknown')}:{result.get('model', 'unknown')}"
            domain = result.get("domain", "unknown")
            domain_scores_dict = result.get("domain_scores", {})
            
            for metric in ["domain_accuracy", "terminology_correctness", "technical_depth",
                          "practical_relevance", "overall_domain_score"]:
                score = domain_scores_dict.get(metric)
                if isinstance(score, (int, float)):
                    by_model_domain[model_key][domain].append({metric: score})
        
        aggregated = {}
        for model_key, domains in by_model_domain.items():
            aggregated[model_key] = {}
            for domain, scores_list in domains.items():
                aggregated[model_key][domain] = {}
                for metric in ["domain_accuracy", "terminology_correctness", "technical_depth",
                              "practical_relevance", "overall_domain_score"]:
                    metric_scores = [s[metric] for s in scores_list if metric in s]
                    if metric_scores:
                        aggregated[model_key][domain][metric] = {
                            "mean": mean(metric_scores),
                            "median": median(metric_scores) if len(metric_scores) > 1 else metric_scores[0]
                        }
        
        return aggregated
    
    def _aggregate_metric(self, metric_path: str) -> Dict[str, float]:
        """Aggregate a specific metric from nested structure."""
        scores = []
        for result in self.results:
            if result.get("status") == "error":
                continue
            parts = metric_path.split(".")
            value = result
            for part in parts:
                value = value.get(part, {}) if isinstance(value, dict) else None
                if value is None:
                    break
            if isinstance(value, (int, float)):
                scores.append(value)
        
        if scores:
            return {
                "mean": mean(scores),
                "median": median(scores) if len(scores) > 1 else scores[0],
                "stdev": stdev(scores) if len(scores) > 1 else 0.0,
                "min": min(scores),
                "max": max(scores)
            }
        return {"mean": 0.0, "median": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0}
    
    def _rank_models(self, metric: str = "overall_etb_score") -> List[Tuple[str, float]]:
        """Rank models by a specific metric."""
        aggregated = self._aggregate_results()
        rankings = []
        
        for model_key, stats in aggregated.items():
            if metric == "overall_etb_score":
                value = stats["overall_etb_score"]["mean"]
            elif metric == "overall_pedagogical_score":
                value = stats["overall_pedagogical_score"]["mean"]
            elif metric == "overall_dialog_score":
                value = stats["overall_dialog_score"]["mean"]
            elif metric == "overall_domain_score":
                value = stats["overall_domain_score"]["mean"]
            else:
                value = 0.0
            
            rankings.append((model_key, value))
        
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings
    
    def _analyze_strengths_weaknesses(self) -> Dict[str, Dict[str, List[str]]]:
        """Analyze strengths and weaknesses per model."""
        by_model_dimension = self._aggregate_by_model_and_dimension()
        strengths_weaknesses = {}
        
        # Calculate average for each dimension across all models
        dimension_averages = defaultdict(list)
        for model_key, dimensions in by_model_dimension.items():
            for dim, stats in dimensions.items():
                dimension_averages[dim].append(stats["mean"])
        
        dim_means = {dim: mean(scores) for dim, scores in dimension_averages.items()}
        
        for model_key, dimensions in by_model_dimension.items():
            strengths = []
            weaknesses = []
            
            for dim, stats in dimensions.items():
                model_mean = stats["mean"]
                overall_mean = dim_means.get(dim, 0.5)
                
                if model_mean > overall_mean + 0.1:  # Significantly above average
                    strengths.append(dim)
                elif model_mean < overall_mean - 0.1:  # Significantly below average
                    weaknesses.append(dim)
            
            strengths_weaknesses[model_key] = {
                "strengths": strengths,
                "weaknesses": weaknesses
            }
        
        return strengths_weaknesses
    
    def _find_best_models_per_metric(self) -> Dict[str, str]:
        """Find best model for each metric."""
        best_models = {}
        
        # Best overall
        rankings = self._rank_models("overall_etb_score")
        if rankings:
            best_models["overall_etb_score"] = rankings[0][0]
        
        # Best pedagogical
        rankings = self._rank_models("overall_pedagogical_score")
        if rankings:
            best_models["overall_pedagogical_score"] = rankings[0][0]
        
        # Best dialog
        rankings = self._rank_models("overall_dialog_score")
        if rankings:
            best_models["overall_dialog_score"] = rankings[0][0]
        
        # Best domain
        rankings = self._rank_models("overall_domain_score")
        if rankings:
            best_models["overall_domain_score"] = rankings[0][0]
        
        return best_models
    
    def _compare_domains(self) -> Dict[str, Any]:
        """Compare performance across domains."""
        by_domain = self._aggregate_by_domain()
        
        domain_scores = {}
        for domain, stats in by_domain.items():
            domain_scores[domain] = stats["overall_domain_score"]["mean"]
        
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "rankings": sorted_domains,
            "best_domain": sorted_domains[0][0] if sorted_domains else None,
            "worst_domain": sorted_domains[-1][0] if sorted_domains else None
        }
    
    def _calculate_dimension_correlations(self) -> Dict[str, float]:
        """Calculate correlations between pedagogical dimensions."""
        # Simple correlation approximation
        dimensions = [
            "mistake_identification", "mistake_location", "revealing_answer",
            "providing_guidance", "actionability", "coherence", "tutor_tone", "human_likeness"
        ]
        
        correlations = {}
        for i, dim1 in enumerate(dimensions):
            for dim2 in dimensions[i+1:]:
                scores1 = []
                scores2 = []
                
                for result in self.results:
                    if result.get("status") == "error":
                        continue
                    pedagogical = result.get("pedagogical_scores", {})
                    s1 = pedagogical.get(dim1)
                    s2 = pedagogical.get(dim2)
                    if isinstance(s1, (int, float)) and isinstance(s2, (int, float)):
                        scores1.append(s1)
                        scores2.append(s2)
                
                if len(scores1) > 1:
                    # Simple correlation coefficient
                    mean1 = mean(scores1)
                    mean2 = mean(scores2)
                    numerator = sum((s1 - mean1) * (s2 - mean2) for s1, s2 in zip(scores1, scores2))
                    denom1 = sum((s1 - mean1) ** 2 for s1 in scores1) ** 0.5
                    denom2 = sum((s2 - mean2) ** 2 for s2 in scores2) ** 0.5
                    
                    if denom1 > 0 and denom2 > 0:
                        corr = numerator / (denom1 * denom2)
                        correlations[f"{dim1}_{dim2}"] = corr
        
        return correlations
    
    def _calculate_statistical_significance(self) -> Dict[str, Any]:
        """Calculate statistical significance between models."""
        aggregated = self._aggregate_results()
        models = list(aggregated.keys())
        
        if len(models) < 2:
            return {"note": "Need at least 2 models for statistical comparison"}
        
        significance = {}
        
        # Compare each pair of models
        for i, model1 in enumerate(models):
            for model2 in models[i+1:]:
                key = f"{model1}_vs_{model2}"
                
                # Get scores for both models
                scores1 = [r.get("overall_etb_score", 0) for r in self.results 
                          if f"{r.get('provider')}:{r.get('model')}" == model1 and r.get("status") != "error"]
                scores2 = [r.get("overall_etb_score", 0) for r in self.results 
                          if f"{r.get('provider')}:{r.get('model')}" == model2 and r.get("status") != "error"]
                
                if len(scores1) > 1 and len(scores2) > 1:
                    mean1 = mean(scores1)
                    mean2 = mean(scores2)
                    diff = abs(mean1 - mean2)
                    
                    # Simple t-test approximation
                    pooled_std = ((stdev(scores1)**2 + stdev(scores2)**2) / 2) ** 0.5
                    if pooled_std > 0:
                        t_stat = diff / (pooled_std * (2 / min(len(scores1), len(scores2))) ** 0.5)
                        significance[key] = {
                            "mean_difference": diff,
                            "t_statistic": t_stat,
                            "significant": abs(t_stat) > 1.96  # Approximate 95% confidence
                        }
        
        return significance
    
    def print_summary(self):
        """Print console summary of results."""
        if not self.results:
            print("No results to summarize")
            return
        
        aggregated = self._aggregate_results()
        rankings = self._rank_models()
        
        print("\n" + "="*80)
        print("ETB BENCHMARK SUMMARY")
        print("="*80)
        print(f"Total evaluations: {len(self.results)}")
        print(f"Models tested: {len(aggregated)}")
        print("\nModel Rankings (by Overall ETB Score):")
        print("-"*80)
        
        for i, (model_key, score) in enumerate(rankings, 1):
            stats = aggregated.get(model_key, {})
            print(f"{i}. {model_key}: {score:.3f}")
            print(f"   Pedagogical: {stats.get('overall_pedagogical_score', {}).get('mean', 0):.3f}, "
                  f"Dialog: {stats.get('overall_dialog_score', {}).get('mean', 0):.3f}, "
                  f"Domain: {stats.get('overall_domain_score', {}).get('mean', 0):.3f}")
        
        print("\n" + "="*80)


# Global report generator instance
etb_report_generator = ETBReportGenerator()

