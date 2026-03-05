# Ai-Tutor

A research-oriented chatbot-based learning assistant that provides contextual AI tutoring and automated assessment, grounded in course materials via RAG (retrieval-augmented generation).

**Stack:** FastAPI backend (`backend_python`), Vite + React frontend (`frontend`), ChromaDB for vector search, OpenAI and/or Ollama for LLMs. The chat UI supports Markdown, code highlighting, KaTeX math, citations, and typing indicators.

## Features

- **Context-aware tutoring** — Answers grounded in uploaded course materials
- **Exploration & assessment** — Hybrid routing for exploratory Q&A and graded responses
- **Document upload** — PDF, TXT, MD, DOCX; chunked and embedded into ChromaDB
- **Real-time chat** — REST and WebSocket APIs; per-user conversation history
- **Security** — Rate limiting, input validation, prompt-injection guards, optional rejection of suspicious prompts

## Quick start

1. **Prerequisites:** Python 3.11 or 3.12 (for ChromaDB), Node.js 18+, npm.

2. **Backend**
   ```bash
   cd backend_python
   cp .env.example .env   # edit with OPENAI_API_KEY etc.
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm install && npm run dev
   ```

4. **Load materials (optional)**  
   Put files in `course_materials/`, then run `python scripts/load_course_materials.py` (with venv active and from project root).

- **Frontend:** http://localhost:5173  
- **API:** http://localhost:8000  
- **API docs:** http://localhost:8000/docs  

See [QUICK_START.md](./QUICK_START.md) for one-command setup and [docs/DEVELOPER.md](./docs/DEVELOPER.md) for full setup, API, and troubleshooting.

## Repository structure

```
├── backend_python/     # FastAPI app, ChromaDB, LLM services, RAG pipeline
├── frontend/          # Vite + React chat UI
├── scripts/            # load_course_materials, benchmarks
├── course_materials/   # Course docs (gitignored; add your own)
├── docs/               # Developer and benchmark documentation
├── QUICK_START.md
└── README.md
```

## Documentation

| Doc | Purpose |
|-----|--------|
| [QUICK_START.md](./QUICK_START.md) | Minimal setup and run steps |
| [docs/DEVELOPER.md](./docs/DEVELOPER.md) | Setup, architecture, API, security, testing, troubleshooting |
| [docs/BENCHMARK.md](./docs/BENCHMARK.md) | Benchmarking (ETB, latency/cost, scales) |
| [docs/MIGRATION_GUIDE.md](./docs/MIGRATION_GUIDE.md) | Node → FastAPI migration overview |
| [docs/ARCHITECTURE_DIAGRAMS.md](./docs/ARCHITECTURE_DIAGRAMS.md) | Architecture diagrams |
| [docs/BENCHMARK_DETAILED.md](./docs/BENCHMARK_DETAILED.md) | Full benchmark methodology and reports |
| [docs/WebSocket-Testing-Guide.md](./docs/WebSocket-Testing-Guide.md) | WebSocket testing |
| [docs/Postman-Collection-README.md](./docs/Postman-Collection-README.md) | Postman API collection |
| [docs/CHROMADB_UPGRADE_ISSUES.md](./docs/CHROMADB_UPGRADE_ISSUES.md) | Python/ChromaDB compatibility |
| [docs/WEEKLY_RESEARCH_UPDATE_SECURITY_IMPROVEMENTS.md](./docs/WEEKLY_RESEARCH_UPDATE_SECURITY_IMPROVEMENTS.md) | Weekly update: security hardening and improvements |

## Security

- **Rate limits:** Chat and upload endpoints are rate-limited (see `backend_python/.env.example`).
- **Prompt security:** User input is delimited in prompts and checked for injection patterns; set `REJECT_ON_INJECTION=true` in `.env` to reject suspicious messages with a safe reply.
- **Production:** Use `ENVIRONMENT=production`, strong `SECRET_KEY`, and avoid logging prompt or response content.

## License

Proprietary research project. Restricted to authorized use.
