# Benchmark Quick Start Guide

## One-Command Benchmarks

### Small Scale (2-5 minutes)
```bash
# ETB Benchmark
python scripts/benchmarks/etb_benchmark.py --scale small

# Basic Benchmark
python scripts/benchmarks/benchmark.py --scale small --use-test-prompts
```

### Medium Scale (15-30 minutes)
```bash
# ETB Benchmark
python scripts/benchmarks/etb_benchmark.py --scale medium

# Basic Benchmark
python scripts/benchmarks/benchmark.py --scale medium --use-test-prompts
```

### Large Scale (1-3 hours)
```bash
# ETB Benchmark
python scripts/benchmarks/etb_benchmark.py --scale large

# Basic Benchmark
python scripts/benchmarks/benchmark.py --scale large --use-test-prompts
```

## What Each Scale Does

| Scale | Questions | Models | Conversations | Best For |
|-------|-----------|--------|----------------|----------|
| **small** | 5 | 1-2 | No | Quick testing, development |
| **medium** | 15 | 2-3 | Optional | Regular evaluation |
| **large** | All | All | Yes | Research, publication |

## Customization

You can override scale presets with explicit options:

```bash
# Use small scale but test OpenAI instead of Ollama
python scripts/benchmarks/etb_benchmark.py --scale small --models openai

# Use medium scale but limit to 10 questions
python scripts/benchmarks/etb_benchmark.py --scale medium --limit 10

# Use large scale but skip conversations
python scripts/benchmarks/etb_benchmark.py --scale large --models ollama
```

## Output Location

All reports are saved to: `backend_python/logs/benchmarks/`

- ETB benchmarks: `backend_python/logs/benchmarks/etb/`
- Basic benchmarks: `backend_python/logs/benchmarks/`

## For More Details

See [BENCHMARK_SCALE_GUIDE.md](./BENCHMARK_SCALE_GUIDE.md) for comprehensive documentation.

