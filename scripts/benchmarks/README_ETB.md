# Educational Tutoring Benchmark (ETB)

Comprehensive benchmarking system for evaluating AI tutoring applications based on peer-reviewed methodologies.

## Overview

The ETB system implements evaluation methodologies from three peer-reviewed papers:

1. **Maurya et al. (NAACL 2025)**: 8 pedagogical dimensions for assessing tutor responses
2. **MathTutorBench (EMNLP 2025)**: Dialog-based evaluation for multi-turn conversations
3. **Chen et al. (IJAED 2025)**: Domain-specific assessment framework

## Components

### Evaluators

- **`pedagogical_evaluator.py`**: Evaluates 8 pedagogical dimensions
  - Mistake Identification
  - Mistake Location
  - Revealing of Answer
  - Providing Guidance
  - Actionability
  - Coherence
  - Tutor Tone
  - Human-likeness

- **`dialog_evaluator.py`**: Evaluates multi-turn conversations
  - Dialog coherence
  - Context retention
  - Learning progression
  - Pedagogical consistency
  - Student engagement

- **`domain_evaluator.py`**: Domain-specific evaluation
  - Domain accuracy
  - Terminology correctness
  - Technical depth
  - Practical relevance

### Dataset

- **`etb_dataset.json`**: 20 conversations covering:
  - Multiple domains (RAG, embeddings, transformers, neural networks, AI/ML)
  - Various difficulty levels (beginner, intermediate, advanced)
  - Single-turn and multi-turn conversations
  - Metadata with expected key points and ground truth facts

### Benchmark Script

- **`etb_benchmark.py`**: Main benchmark runner
  - Tests multiple LLM models (Ollama + OpenAI)
  - Evaluates using all three evaluators
  - Generates comprehensive reports

### Report Generator

- **`etb_report_generator.py`**: Generates 7 types of reports:
  1. JSON report (detailed structured data)
  2. CSV report (spreadsheet-friendly)
  3. Summary report (human-readable)
  4. Pedagogical dimensions report
  5. Dialog analysis report
  6. Domain analysis report
  7. Comparative analysis report

## Usage

### Prerequisites

Install dependencies:
```bash
cd backend_python
pip install -r requirements.txt
```

Or use the virtual environment:
```bash
source venv/bin/activate
pip install -r backend_python/requirements.txt
```

### Running Benchmarks

**Quick test (5 questions):**
```bash
python scripts/benchmarks/etb_benchmark.py --limit 5
```

**Test specific models:**
```bash
# Ollama models only
python scripts/benchmarks/etb_benchmark.py --models ollama

# OpenAI models only
python scripts/benchmarks/etb_benchmark.py --models openai

# All models
python scripts/benchmarks/etb_benchmark.py --models all
```

**Include multi-turn conversations:**
```bash
python scripts/benchmarks/etb_benchmark.py --conversations
```

**Custom output directory:**
```bash
python scripts/benchmarks/etb_benchmark.py --out custom/path/to/reports
```

**Assessment mode:**
```bash
python scripts/benchmarks/etb_benchmark.py --mode assessment
```

### Command-Line Options

- `--dataset`: Path to ETB dataset JSON file (default: `scripts/benchmarks/etb_dataset.json`)
- `--models`: Which models to benchmark (`all`, `ollama`, `openai`)
- `--mode`: LLM mode (`exploration` or `assessment`)
- `--out`: Output directory for reports (default: `backend_python/logs/benchmarks/etb`)
- `--limit`: Limit number of questions (for quick testing)
- `--conversations`: Include multi-turn conversations

## Output Reports

Reports are saved to the specified output directory with timestamps:

1. **`etb_benchmark_TIMESTAMP.json`**: Complete structured data
2. **`etb_benchmark_TIMESTAMP.csv`**: Spreadsheet-compatible format
3. **`etb_summary_TIMESTAMP.txt`**: Human-readable summary
4. **`etb_pedagogical_dimensions_TIMESTAMP.json`**: Pedagogical analysis
5. **`etb_dialog_analysis_TIMESTAMP.json`**: Dialog metrics
6. **`etb_domain_analysis_TIMESTAMP.json`**: Domain-specific analysis
7. **`etb_comparative_analysis_TIMESTAMP.json`**: Model comparisons

## Evaluation Metrics

### Overall ETB Score
Weighted combination:
- 50% Pedagogical Score (8 dimensions)
- 20% Dialog Score (multi-turn metrics)
- 30% Domain Score (domain-specific accuracy)

### Pedagogical Dimensions (8)
Each dimension scored 0.0-1.0:
- Mistake Identification
- Mistake Location
- Revealing Answer
- Providing Guidance
- Actionability
- Coherence
- Tutor Tone
- Human-likeness

### Dialog Metrics
- Dialog Coherence
- Context Retention
- Learning Progression
- Pedagogical Consistency
- Student Engagement

### Domain Metrics
- Domain Accuracy
- Terminology Correctness
- Technical Depth
- Practical Relevance
- Feedback Quality

## Example Output

```
ETB BENCHMARK SUMMARY
================================================================================
Total evaluations: 100
Models tested: 3

Model Rankings (by Overall ETB Score):
--------------------------------------------------------------------------------
1. ollama:llama3.1:8b-instruct: 0.823
   Pedagogical: 0.815, Dialog: 0.780, Domain: 0.845
2. openai:gpt-4o-mini: 0.798
   Pedagogical: 0.790, Dialog: 0.820, Domain: 0.785
3. ollama:mistral:7b-instruct: 0.765
   Pedagogical: 0.755, Dialog: 0.740, Domain: 0.800
```

## References

1. Maurya et al. (NAACL 2025). "Unifying AI Tutor Evaluation: An Evaluation Taxonomy for Pedagogical Ability Assessment of LLM-Powered AI Tutors"

2. MathTutorBench (EMNLP 2025). "A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors"

3. Chen et al. (IJAED 2025). "Benchmarking Large Language Models on Homework Assessment"

## License

See main project LICENSE file.

