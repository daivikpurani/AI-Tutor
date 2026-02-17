# Benchmarks

Run benchmarks from **project root** with the backend venv active.

- **ETB (Educational Tutoring Benchmark):** `python scripts/benchmarks/etb_benchmark.py --scale small|medium|large`
- **Basic (latency/cost):** `python scripts/benchmarks/benchmark.py --scale small --use-test-prompts`

**Full documentation:** [docs/BENCHMARK.md](../../docs/BENCHMARK.md) and [docs/BENCHMARK_DETAILED.md](../../docs/BENCHMARK_DETAILED.md).

**Main scripts:** `etb_benchmark.py`, `benchmark.py`, `pedagogical_evaluator.py`, `dialog_evaluator.py`, `domain_evaluator.py`, `etb_report_generator.py`. Data: `etb_dataset.json`, `queries.txt`.
