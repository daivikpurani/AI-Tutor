# Benchmark Scale Options Guide

This guide explains how to run the benchmarking system at different scales: **small**, **medium**, and **large**.

## Overview

The benchmarking system supports two types of benchmarks:

1. **Basic Benchmark** (`benchmark.py`): Tests models with simple queries and generates latency/cost metrics
2. **ETB Benchmark** (`etb_benchmark.py`): Comprehensive educational tutoring evaluation with pedagogical, dialog, and domain metrics

## Scale Definitions

### Small Scale
- **Purpose**: Quick validation, smoke tests, development debugging
- **Queries**: 3-5 queries
- **Models**: 1-2 models
- **Time**: ~2-5 minutes
- **Use Case**: Verify system is working, test changes quickly

### Medium Scale
- **Purpose**: Standard evaluation, model comparison
- **Queries**: 10-20 queries
- **Models**: 2-3 models
- **Time**: ~10-30 minutes
- **Use Case**: Regular benchmarking, comparing model performance

### Large Scale
- **Purpose**: Comprehensive evaluation, research-grade results
- **Queries**: All available queries (20+)
- **Models**: All available models (5+)
- **Time**: ~1-3 hours
- **Use Case**: Final evaluation, publication-ready results

---

## Small Scale Benchmarks

### Option 1: Using Scale Preset (Easiest)

**Quick test with scale preset:**
```bash
# ETB benchmark - small scale (5 questions, 1-2 models)
python scripts/benchmarks/etb_benchmark.py --scale small

# Basic benchmark - small scale (5 queries, 1-2 models)
python scripts/benchmarks/benchmark.py --scale small --use-test-prompts
```

**Estimated Time**: 2-5 minutes  
**What it does**: Automatically limits to 5 questions, 1-2 Ollama models, skips conversations

### Option 2: Quick ETB Test (Manual Configuration)

**Test with 5 questions, single model:**
```bash
# Test with Ollama models only, limit to 5 questions
python scripts/benchmarks/etb_benchmark.py --limit 5 --models ollama

# Test with OpenAI only, limit to 5 questions
python scripts/benchmarks/etb_benchmark.py --limit 5 --models openai

# Test with first available model, limit to 3 questions
python scripts/benchmarks/etb_benchmark.py --limit 3 --models ollama
```

**Estimated Time**: 2-5 minutes  
**Output**: Full ETB reports with pedagogical, dialog, and domain metrics

### Option 3: Basic Benchmark with Test Prompts

**Use built-in test prompts (18 queries total):**
```bash
# Test with all models but use only simple factual queries
python scripts/benchmarks/benchmark.py --use-test-prompts --models ollama
```

**Estimated Time**: 3-8 minutes  
**Output**: Basic latency, token usage, and quality scores

### Option 4: Custom Small Query Set

**Create a small queries file:**
```bash
# Create a small_queries.txt file with 3-5 queries
echo -e "What is RAG?\nExplain vector databases.\nWhat is a transformer?" > small_queries.txt

# Run benchmark with custom queries
python scripts/benchmarks/benchmark.py --queries small_queries.txt --models ollama
```

**Estimated Time**: 2-4 minutes  
**Output**: Basic metrics for specified queries

---

## Medium Scale Benchmarks

### Option 1: Using Scale Preset (Easiest)

**Standard test with scale preset:**
```bash
# ETB benchmark - medium scale (15 questions, 2-3 models)
python scripts/benchmarks/etb_benchmark.py --scale medium

# Basic benchmark - medium scale (15 queries, 2-3 models)
python scripts/benchmarks/benchmark.py --scale medium --use-test-prompts
```

**Estimated Time**: 15-30 minutes  
**What it does**: Automatically limits to 15 questions, uses 2-3 models

### Option 2: Standard ETB Benchmark (Manual Configuration)

**Test with 10-15 questions, multiple models:**
```bash
# Test with 10 questions, all models
python scripts/benchmarks/etb_benchmark.py --limit 10 --models all

# Test with 15 questions, Ollama models only
python scripts/benchmarks/etb_benchmark.py --limit 15 --models ollama

# Test with 12 questions, include multi-turn conversations
python scripts/benchmarks/etb_benchmark.py --limit 12 --conversations --models all
```

**Estimated Time**: 15-30 minutes  
**Output**: Comprehensive ETB reports with statistical significance

### Option 3: Basic Benchmark with Full Query Set

**Use all queries from queries.txt:**
```bash
# Test all queries (typically 20-25 queries) with all models
python scripts/benchmarks/benchmark.py --queries scripts/benchmarks/queries.txt --models all

# Test with built-in prompts, all models
python scripts/benchmarks/benchmark.py --use-test-prompts --models all
```

**Estimated Time**: 20-45 minutes  
**Output**: Complete comparison across all models and queries

### Option 4: Category-Specific Medium Benchmark

**Test specific query categories:**
```python
# Create a medium_queries.txt with queries from specific categories
# Include: 5 simple factual + 5 complex analytical + 5 domain-specific
```

Then run:
```bash
python scripts/benchmarks/benchmark.py --queries medium_queries.txt --models all
```

**Estimated Time**: 15-25 minutes  
**Output**: Focused analysis on specific query types

---

## Large Scale Benchmarks

### Option 1: Using Scale Preset (Easiest)

**Full benchmark with scale preset:**
```bash
# ETB benchmark - large scale (all questions, all models, with conversations)
python scripts/benchmarks/etb_benchmark.py --scale large

# Basic benchmark - large scale (all queries, all models)
python scripts/benchmarks/benchmark.py --scale large --use-test-prompts
```

**Estimated Time**: 1-3 hours  
**What it does**: Uses all available questions, all available models, includes multi-turn conversations

### Option 2: Full ETB Benchmark (Manual Configuration)

**Complete evaluation with all questions and models:**
```bash
# Full ETB benchmark with all questions, all models, including conversations
python scripts/benchmarks/etb_benchmark.py --models all --conversations

# Full benchmark in assessment mode
python scripts/benchmarks/etb_benchmark.py --models all --mode assessment --conversations

# Full benchmark with custom output directory
python scripts/benchmarks/etb_benchmark.py --models all --conversations --out backend_python/logs/benchmarks/full_run_$(date +%Y%m%d)
```

**Estimated Time**: 1-3 hours (depending on number of models and questions)  
**Output**: Complete ETB evaluation with all 7 report types

### Option 3: Comprehensive Basic Benchmark

**Test all queries with all models:**
```bash
# Full benchmark with all queries
python scripts/benchmarks/benchmark.py --queries scripts/benchmarks/queries.txt --models all

# Full benchmark with test prompts
python scripts/benchmarks/benchmark.py --use-test-prompts --models all

# Full benchmark in both exploration and assessment modes
python scripts/benchmarks/benchmark.py --use-test-prompts --models all --mode exploration
python scripts/benchmarks/benchmark.py --use-test-prompts --models all --mode assessment
```

**Estimated Time**: 1-2 hours  
**Output**: Complete performance comparison across all models

### Option 4: Multi-Mode Comprehensive Benchmark

**Run benchmarks in both modes:**
```bash
# Create a script to run both modes
cat > run_full_benchmark.sh << 'EOF'
#!/bin/bash
echo "Running exploration mode..."
python scripts/benchmarks/etb_benchmark.py --models all --mode exploration --conversations --out backend_python/logs/benchmarks/full_exploration

echo "Running assessment mode..."
python scripts/benchmarks/etb_benchmark.py --models all --mode assessment --conversations --out backend_python/logs/benchmarks/full_assessment
EOF

chmod +x run_full_benchmark.sh
./run_full_benchmark.sh
```

**Estimated Time**: 2-4 hours  
**Output**: Complete evaluation in both exploration and assessment modes

---

## Quick Reference: Scale Comparison

### Using the `--scale` Preset Option (Easiest)

| Scale | Queries | Models | Time | Command Example |
|-------|---------|--------|------|----------------|
| **Small** | 5 | 1-2 | 2-5 min | `etb_benchmark.py --scale small` |
| **Medium** | 15 | 2-3 | 15-30 min | `etb_benchmark.py --scale medium` |
| **Large** | All (20+) | All (5+) | 1-3 hours | `etb_benchmark.py --scale large` |

### Manual Configuration

| Scale | Queries | Models | Time | Command Example |
|-------|---------|--------|------|----------------|
| **Small** | 3-5 | 1-2 | 2-5 min | `etb_benchmark.py --limit 5 --models ollama` |
| **Medium** | 10-20 | 2-3 | 15-30 min | `etb_benchmark.py --limit 15 --models all` |
| **Large** | All (20+) | All (5+) | 1-3 hours | `etb_benchmark.py --models all --conversations` |

---

## Advanced Options

### Parallel Execution (Future Enhancement)

For large-scale benchmarks, you could run multiple models in parallel:
```bash
# Run different models in separate terminals/processes
# Terminal 1:
python scripts/benchmarks/etb_benchmark.py --limit 20 --models ollama --out logs/ollama_run

# Terminal 2:
python scripts/benchmarks/etb_benchmark.py --limit 20 --models openai --out logs/openai_run
```

### Custom Dataset for Large Scale

Create a custom large dataset:
```bash
# Use a larger ETB dataset
python scripts/benchmarks/etb_benchmark.py --dataset custom_large_dataset.json --models all
```

### Incremental Benchmarking

Run benchmarks incrementally and combine results:
```bash
# Day 1: Test Ollama models
python scripts/benchmarks/etb_benchmark.py --models ollama --out logs/day1_ollama

# Day 2: Test OpenAI models
python scripts/benchmarks/etb_benchmark.py --models openai --out logs/day2_openai
```

---

## Recommendations

### For Development/Testing
- **Use**: Small scale (5 queries, 1-2 models)
- **Command**: `python scripts/benchmarks/etb_benchmark.py --scale small`

### For Regular Evaluation
- **Use**: Medium scale (15 queries, 2-3 models)
- **Command**: `python scripts/benchmarks/etb_benchmark.py --scale medium`

### For Research/Publication
- **Use**: Large scale (all queries, all models, both modes)
- **Command**: `python scripts/benchmarks/etb_benchmark.py --scale large`

---

## Monitoring Progress

All benchmarks provide progress logging:
- Query-by-query progress: `[1/20] Testing: query...`
- Model-by-model progress: `Benchmarking ollama:llama3.1:8b-instruct...`
- Final summary with report locations

Check logs in real-time:
```bash
# Run benchmark with visible output
python scripts/benchmarks/etb_benchmark.py --limit 10 --models all 2>&1 | tee benchmark.log
```

---

## Output Locations

- **Small/Medium Scale**: `backend_python/logs/benchmarks/`
- **Large Scale**: `backend_python/logs/benchmarks/etb/` (for ETB) or custom directory
- **Reports**: JSON, CSV, and summary text files with timestamps

---

## Troubleshooting

### If benchmark takes too long:
- Reduce `--limit` value
- Use `--models ollama` instead of `--models all`
- Skip `--conversations` flag for ETB benchmark

### If you run out of memory:
- Run benchmarks sequentially (one model at a time)
- Reduce query limit
- Close other applications

### If you want faster results:
- Use basic benchmark instead of ETB benchmark
- Test fewer models
- Use `--limit` to reduce queries

