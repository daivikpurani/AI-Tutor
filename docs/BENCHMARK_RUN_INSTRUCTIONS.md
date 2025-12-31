# Benchmark Run Instructions

## Overview

The benchmarking suite has been updated with **78 questions** covering multiple course topics:
- Algorithms/Analysis of Algorithms (24 answerable + 6 unanswerable)
- Data Visualization (CSC 805) (25 answerable + 6 unanswerable)
- Original RAG/AI/ML questions (17 questions)

## Prerequisites

### Option 1: Using Ollama (Local Models)

1. **Start Ollama service:**
   ```bash
   # Check if Ollama is installed
   ollama --version
   
   # Start Ollama (if not running as a service)
   ollama serve
   ```

2. **Pull required models:**
   ```bash
   ollama pull llama3.1:8b-instruct
   ollama pull llama3.2:latest
   ollama pull llama3.3:latest
   # Add other models as needed
   ```

3. **Verify Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Option 2: Using OpenAI

1. **Set OpenAI API key:**
   ```bash
   cd backend_python
   # Edit .env file or set environment variable
   export OPENAI_API_KEY=your_api_key_here
   ```

## Running Benchmarks

### Full Benchmark (All 78 Questions)

```bash
cd /Users/daivikpurani/Desktop/ACAD/Thesis/code/FinalProject
source venv/bin/activate

# Run with all available models
python scripts/benchmarks/benchmark.py \
  --queries scripts/benchmarks/queries.txt \
  --models all \
  --mode exploration
```

### Specific Model Types

```bash
# Test only Ollama models
python scripts/benchmarks/benchmark.py \
  --queries scripts/benchmarks/queries.txt \
  --models ollama

# Test only OpenAI
python scripts/benchmarks/benchmark.py \
  --queries scripts/benchmarks/queries.txt \
  --models openai
```

### Limited Scale Testing

```bash
# Small scale (5 questions, 1-2 models)
python scripts/benchmarks/benchmark.py \
  --queries scripts/benchmarks/queries.txt \
  --scale small

# Medium scale (15 questions, 2-3 models)
python scripts/benchmarks/benchmark.py \
  --queries scripts/benchmarks/queries.txt \
  --scale medium

# Custom limit
python scripts/benchmarks/benchmark.py \
  --queries scripts/benchmarks/queries.txt \
  --limit 10
```

## Expected Output

### Report Files

Benchmark results are saved to: `backend_python/logs/benchmarks/`

- **JSON Report**: `benchmark_report_YYYYMMDD_HHMMSS.json`
  - Detailed metrics per query per model
  - Includes: latency, token usage, response quality, citations, confidence scores
  
- **CSV Report**: `benchmark_report_YYYYMMDD_HHMMSS.csv`
  - Spreadsheet-friendly format for analysis
  - Columns: query, model, provider, latency, tokens, quality_score, etc.

### Metrics Collected

For each query-model combination:
- **Latency**: Response time in seconds
- **Token Usage**: Prompt tokens, completion tokens, total tokens
- **Response Quality**: Relevance score, completeness score
- **Citations**: Number of citations, citation quality
- **Self-Check Confidence**: LLM's confidence in its own answer
- **Retrieval Quality**: Context chunk count, similarity scores

## Question Categories

### Answerable Questions (49 total)
- **Algorithms/Analysis**: 24 questions
  - Approximation algorithms, graph algorithms, flow networks, TSP, dynamic programming, backtracking
  
- **Data Visualization (CSC 805)**: 25 questions
  - Perception/cognition, visual representations, visualization process, data types, pipelines, graph visualization

### Unanswerable Questions (12 total)
- **Algorithms**: 6 questions (should return "I don't know.")
- **Data Visualization**: 6 questions (should return "I don't know.")

### Original Questions (17 total)
- RAG/AI/ML domain questions from original test suite

## Analysis

After running benchmarks, you can:

1. **Compare Models**: See which models perform best on different question types
2. **Evaluate RAG Quality**: Check if answerable questions get proper answers
3. **Test "I don't know"**: Verify unanswerable questions correctly return "I don't know."
4. **Performance Metrics**: Compare latency and token usage across models
5. **Citation Quality**: Assess how well models cite sources from course materials

## Troubleshooting

### Ollama Connection Failed
- Ensure Ollama service is running: `ollama serve`
- Check port 11434 is accessible: `curl http://localhost:11434/api/tags`

### OpenAI API Key Missing
- Set environment variable: `export OPENAI_API_KEY=your_key`
- Or add to `backend_python/.env` file

### No Results Generated
- Verify models are available: Check benchmark output for "Testing X models"
- Ensure vector database has course materials loaded
- Check logs for errors

## Next Steps

1. Run full benchmark with available models
2. Review JSON/CSV reports
3. Compare performance across models
4. Identify areas for improvement
5. Re-run after prompt/system improvements
