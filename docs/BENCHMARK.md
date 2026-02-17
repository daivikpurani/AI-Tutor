# Benchmarking

## Quick start

**One-command runs** (from project root, with venv active):

| Scale | Time | Commands |
|-------|------|----------|
| **small** | 2–5 min | `python scripts/benchmarks/etb_benchmark.py --scale small` or `python scripts/benchmarks/benchmark.py --scale small --use-test-prompts` |
| **medium** | 15–30 min | `python scripts/benchmarks/etb_benchmark.py --scale medium` |
| **large** | 1–3 hours | `python scripts/benchmarks/etb_benchmark.py --scale large` |

| Scale | Questions | Models | Conversations | Best for |
|-------|-----------|--------|---------------|----------|
| small | 5 | 1–2 | No | Quick testing, development |
| medium | 15 | 2–3 | Optional | Regular evaluation |
| large | All | All | Yes | Research, publication |

Reports: **ETB** → `backend_python/logs/benchmarks/etb/` · **Basic** → `backend_python/logs/benchmarks/`

## Run instructions

**Prerequisites:** Ollama running (`ollama serve`) and/or `OPENAI_API_KEY` in `backend_python/.env`. Vector DB should have course materials loaded (`python scripts/load_course_materials.py`).

**78 questions** cover: Algorithms (24 answerable + 6 unanswerable), Data Visualization (25 + 6), and RAG/AI/ML (17). Full run with all models: `python scripts/benchmarks/benchmark.py --queries scripts/benchmarks/queries.txt --models all --mode exploration`. Use `--scale small` or `--limit N` for faster runs.

**Troubleshooting:** Ollama → `curl http://localhost:11434/api/tags`. OpenAI → set key in `backend_python/.env`. No context → load documents first.

---

## Full documentation

For methodology, system architecture, evaluation frameworks, dataset structure, report formats, advanced configuration, troubleshooting, and research references, see **[BENCHMARK_DETAILED.md](BENCHMARK_DETAILED.md)**.
