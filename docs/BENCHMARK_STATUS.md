# Benchmark Status

## Current Status

**Benchmark is running in the background**

- **Full Benchmark**: 78 questions × 4 Ollama models = 312 total queries
- **Estimated Time**: ~1-2 hours (depending on model response times)
- **Models Being Tested**:
  - phi3:mini
  - mistral:7b-instruct
  - llama3.2:latest
  - llama3.3:latest

## Check Progress

### Method 1: Check Running Processes
```bash
ps aux | grep benchmark.py | grep -v grep
```

### Method 2: Check Latest Report
```bash
cd /Users/daivikpurani/Desktop/ACAD/Thesis/code/FinalProject
python -c "
import json
import glob
import os
from datetime import datetime

reports = glob.glob('backend_python/logs/benchmarks/benchmark_report_*.json')
if reports:
    latest = max(reports, key=os.path.getmtime)
    mtime = os.path.getmtime(latest)
    print(f'Latest report: {latest}')
    print(f'Last updated: {datetime.fromtimestamp(mtime)}')
    with open(latest, 'r') as f:
        data = json.load(f)
    print(f'Total queries in report: {data.get(\"total_queries\", 0)}')
    if 'detailed_results' in data:
        print(f'Results collected: {len(data[\"detailed_results\"])}')
else:
    print('No reports found')
"
```

### Method 3: Monitor Log File
```bash
tail -f /tmp/benchmark_full.log
```

## When Complete

Results will be saved to:
- **JSON**: `backend_python/logs/benchmarks/benchmark_report_YYYYMMDD_HHMMSS.json`
- **CSV**: `backend_python/logs/benchmarks/benchmark_report_YYYYMMDD_HHMMSS.csv`

## View Results

### Quick Summary
```bash
cd /Users/daivikpurani/Desktop/ACAD/Thesis/code/FinalProject
python scripts/benchmarks/view_results.py
```

### Detailed Analysis
```bash
# View JSON report
cat backend_python/logs/benchmarks/benchmark_report_*.json | jq '.summary'

# View CSV in spreadsheet
open backend_python/logs/benchmarks/benchmark_report_*.csv
```

## Expected Output

The benchmark will generate:
1. **Per-query metrics**: Latency, tokens, quality scores for each question
2. **Per-model summary**: Average performance across all questions
3. **Comparison data**: Which models perform best on different question types

## Questions Being Tested

- **49 Answerable Questions**: Should get proper answers with citations
- **12 Unanswerable Questions**: Should return "I don't know."
- **17 Original RAG/AI/ML Questions**: Baseline questions

Total: **78 questions**

## Next Steps After Completion

1. Review JSON report for detailed metrics
2. Analyze CSV for spreadsheet analysis
3. Compare model performance
4. Check "I don't know" accuracy for unanswerable questions
5. Verify citation quality for answerable questions
