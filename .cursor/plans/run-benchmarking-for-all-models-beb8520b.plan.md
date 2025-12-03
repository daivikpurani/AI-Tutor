<!-- beb8520b-fa3b-4939-a16a-750a70ab3d2c 8abc95fe-6530-4116-9a93-8040a2287b8a -->
# Run Benchmarking for All Models

## Overview

Update the benchmark configuration to include the newly downloaded models (mistral:7b-instruct and phi3:mini), then run comprehensive benchmarks across all available Ollama models and generate detailed performance reports with real metrics.

## Steps

### 1. Update Benchmark Configuration

- **File**: `backend_python/services/benchmark_config.py`
- **Change**: Add `mistral:7b-instruct` and `phi3:mini` to `DEFAULT_OLLAMA_MODELS` list (line 33-37)
- **Reason**: These models are now available but not included in the default benchmark list

### 2. Verify Benchmark Infrastructure

- Check that all required services are available:
- `RelevanceScorer` service exists
- `QueryHandler` service exists
- Vector database is initialized
- All dependencies are installed

### 3. Run Comprehensive Benchmarks

- **Command**: `python3 scripts/benchmarks/benchmark.py --models ollama --queries scripts/benchmarks/queries.txt`
- **What it does**:
- Tests all configured Ollama models (llama3.2:latest, llama3.3:latest, mistral:7b-instruct, phi3:mini)
- Runs each model against all queries in queries.txt (~20 queries)
- Measures: latency, token usage, response quality, citation scores, completeness, self-check confidence
- Generates JSON and CSV reports in `backend_python/logs/benchmarks/`

### 4. Generate Summary Report

- The benchmark script automatically generates:
- JSON report with detailed metrics per query per model
- CSV report for spreadsheet analysis
- Console summary with aggregated statistics
- Review the output directory for timestamped reports

### 5. Verify Results

- Check that reports are generated successfully
- Verify all models were tested (no errors)
- Confirm metrics are reasonable (latency, scores, etc.)

## Expected Output

- JSON report: `backend_python/logs/benchmarks/benchmark_report_YYYYMMDD_HHMMSS.json`
- CSV report: `backend_python/logs/benchmarks/benchmark_report_YYYYMMDD_HHMMSS.csv`
- Console summary with performance comparison across all models

## Metrics Collected

- Latency (ms) - response time per query
- Token usage (prompt, completion, total)
- Quality scores (citation, completeness, overall)
- Self-check confidence scores
- Error rates
- Response length and word count