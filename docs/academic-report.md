# AI-Tutor: An Academic Report on System Evolution, Iterations, and Research Foundations

## Abstract

This report documents the evolution of the AI-Tutor project from an early Node.js + Pinecone prototype into a FastAPI- and ChromaDB-based, hybrid-LLM tutoring platform with real-time chat, document-grounded responses, and an extensible architecture. We present major iterations, design decisions, improvements, references to foundational literature and tooling, and a slow-to-slow buildup narrative of how the system matured. The goal is to provide a rigorous, citable narrative that captures technical architecture, methodology, and research context.

## 1. Introduction

AI-Tutor is a research-oriented intelligent tutoring system designed to provide contextual, course-grounded assistance via conversational AI. Instructors upload documents that are chunked, embedded, and stored in a vector database; students interact via a chatbot UI that retrieves relevant context and generates responses through a hybrid LLM strategy (local and hosted providers). The project emphasizes grounded responses, reliability, cost-latency trade-offs, and developer ergonomics.

- Canonical backend: `FinalProject/backend_python` (FastAPI, ChromaDB, hybrid LLM routing)
- Frontend: React + Vite (in `FinalProject/frontend`), with WebSocket streaming for UX
- Legacy code and early research: `Backend_legacy/`

## 2. Project History and Evolution

### 2.1 Early Phase: Node.js + Pinecone (Legacy)

- Architecture centered on Node.js/Express, Python scripts for prompts and chunking, and Pinecone for vector storage (see `system_architecture.md`, `Backend_legacy/vectorstore/architecture.md`).
- Document ingestion and “agentic chunking” pipeline used OpenAI embeddings with Pinecone indexing.
- Initial prompt specification targeted interdisciplinary collaboration (CS–Biology DNA) to inform tutoring tone and cross-domain explanations (`Backend_legacy/Initialprompt.md`).
- Referenced foundational resources and kept research PDFs local under `Backend_legacy/pdfs/`.

Limitations observed:
- Split runtime (Node + Python) introduced cross-process complexity and overhead.
- External vector DB (Pinecone) added dependencies and ops burden for research-scale experimentation.
- Mixed-language stack hindered rapid iteration on ML/LLM features.

### 2.2 Migration to Python FastAPI + ChromaDB

- A comprehensive migration replaced Node.js/Express with FastAPI, and Pinecone with local ChromaDB for faster research iteration and reduced external dependencies.
- Consolidated AI/ML logic in Python for native access to libraries and cleaner composition (`FinalProject/docs/MIGRATION_GUIDE.md`).
- Introduced Pydantic models for typed request/response validation, and auto-generated API docs (`/docs`, `/redoc`).
- WebSocket streaming implemented for real-time conversational UX.

Outcomes:
- Reduced overhead and latency by eliminating cross-process calls.
- Simplified setup and local persistence via SQLite-backed ChromaDB.
- Improved reliability and developer experience.

### 2.3 Hybrid LLM Routing and Research Instrumentation

- Designed a hybrid provider model teaming OpenAI (GPT-4o) with a local Ollama model (e.g., Llama 3), guided by a `QueryComplexityAnalyzer` and fallbacks.
- Documented an empirical methodology for analyzing latency, throughput, cost, and routing hit-rates across streaming and non-streaming paths (`FinalProject/docs/hybrid-latency-cost.md`).
- Established structured logging plans and data schemas for reproducible measurement.

### 2.4 Frontend Consolidation and WebSocket UX

- Unified the frontend around a React + Vite app with WebSocket flows for responsive streaming output (`FinalProject/frontend/`).
- Provided guides to test WebSocket endpoints and browser-based streaming scenarios (`FinalProject/docs/WebSocket-Testing-Guide.md`).

### 2.5 Documentation and Developer Experience

- Canonical documentation and developer references centralized in `FinalProject/README.md` and `FinalProject/docs/DEVELOPER.md`.
- Startup scripts and guides (`start.sh`, `start-dev.sh`, `QUICK_START.md`, `docs/DEVELOPER.md`) streamline setup, environment checks, and daily workflow.

## 3. Iterations and Design Decisions

- Vector DB iteration: Pinecone → ChromaDB. Rationale: simplify ops, enable local persistence, guarantee reproducibility, and reduce costs.
- Backend iteration: Node.js → FastAPI. Rationale: tighter integration with Python ecosystem, type safety (Pydantic), auto-docs, and async performance.
- LLM provider strategy: Single provider → Hybrid routing with fallbacks (OpenAI ↔ Ollama) to optimize cost/latency and resilience.
- Communication mode: REST-only → Dual REST + WebSocket for both batch and streaming conversational experiences.
- Context grounding: Stricter document-grounded responses, explicit handling when context is absent or conflicting.
- Instrumentation: Added measurement plan for latency, throughput, and cost to guide evidence-based provider routing policies.

## 4. System Architecture (Current)

Core components (see `FinalProject/docs/ARCHITECTURE_DIAGRAMS.md`):
- API Gateway and WebSocket server (FastAPI)
- Query Handler orchestrating retrieval-augmented generation
- Vector DB service (ChromaDB) with local persistence
- Document Chunker supporting TXT/MD/PDF/DOCX with overlap and metadata
- LLM Service implementing hybrid routing and streaming
- Frontend React app with real-time streaming and markdown rendering

Key qualities:
- Provider abstraction and fallback resilience
- Local-first vector search for reproducibility
- Typed interfaces with Pydantic for safety
- Clear separation of concerns and modular services

## 5. Improvements Implemented

- End-to-end migration to FastAPI + ChromaDB with async endpoints and typed models (`FinalProject/docs/MIGRATION_GUIDE.md`).
- Hybrid LLM routing strategy with complexity-aware decisioning and fallbacks (`FinalProject/docs/hybrid-latency-cost.md`).
- Real-time WebSocket streaming path for better user experience (`FinalProject/docs/WebSocket-Testing-Guide.md`).
- Document-grounded response policy to ensure fidelity and verifiability (`FinalProject/backend_python/README.md`).
- Developer tooling: startup scripts, environment validation, clean project structure, auto API docs, and testing scaffolds.

Representative backend modules:
- `services/query_handler.py`: conversation orchestration (streaming and non-streaming)
- `services/vector_db.py`: ChromaDB operations and semantic search
- `services/document_chunker.py`: multi-format ingestion and chunking
- `services/llm_service.py`: hybrid routing and provider adapters
- `utils/prompts.py`: system prompts and templates

## 6. Methodology: Slow-to-Slow Build-up

The project followed a methodical progression from concept to robust research platform:

1) Problem framing and domain prompts: defined interdisciplinary tutoring goals and communication principles (`Backend_legacy/Initialprompt.md`).
2) Prototype RAG pipeline: agentic chunking and Pinecone indexing validated feasibility (`Backend_legacy/vectorstore/architecture.md`).
3) Architectural consolidation: migration to FastAPI and ChromaDB for tighter ML integration and local persistence.
4) Conversational UX: added WebSocket streaming and session memory for multi-turn tutoring.
5) Hybrid routing: introduced local LLMs via Ollama for simple queries and cost control, OpenAI for complex cases.
6) Measurement and governance: drafted latency/cost instrumentation and routing guardrails to align quality and spend.

This slow, deliberate build-up allowed research flexibility while incrementally improving reliability, performance, and developer velocity.

## 7. Evaluation Plan (Latency, Cost, Quality)

- Metrics: TTFB, total latency (p50/p95/p99), tokens/sec or chars/sec proxy, cost per request, routing hit-rate, error/fallback rates.
- Modes: streaming and non-streaming.
- Workloads: simple/medium/complex query sets with repeated trials to collect stable statistics.
- Data capture: JSONL schema for reproducibility and later analysis (`FinalProject/docs/hybrid-latency-cost.md`).

## 8. Sources and Tooling Documentation

Project documentation and guides:
- `FinalProject/README.md` — system overview, features, setup, endpoints
- `FinalProject/docs/DEVELOPER.md` — developer workflow, environment, scripts, testing
- `FinalProject/docs/MIGRATION_GUIDE.md` — Node.js → FastAPI + ChromaDB migration
- `FinalProject/QUICK_START.md`, `FinalProject/docs/DEVELOPER.md` — startup methods, URLs, troubleshooting
- `FinalProject/docs/WebSocket-Testing-Guide.md` — WebSocket testing patterns
- `FinalProject/docs/hybrid-latency-cost.md` — measurement plan and trade-offs
- `FinalProject/docs/ARCHITECTURE_DIAGRAMS.md` — Mermaid diagrams (context, container, component, sequences)

Legacy and architecture references:
- `system_architecture.md`, `system_architecture_diagram_report.md`
- `Backend_legacy/vectorstore/architecture.md`
- `Backend_legacy/Initialprompt.md`

## 9. Research Papers and References

Local references included in the repository:
- `Backend_legacy/pdfs/Large Language Models- A Survey.pdf`
- `Backend_legacy/pdfs/promptengineering.pdf`
- `Backend_legacy/pdfs/promptengineering_compressed.pdf`
- `Backend_legacy/pdfs/Project Description_submitted version.pdf`
- `Backend_legacy/pdfs/Zhongetal.-2024-EnhancingtheAnalysisofInterdisciplinaryLearni.pdf`
- `Backend_legacy/backupPDF/DeepSeekR1.pdf`

Tool and framework documentation (external):
- FastAPI — https://fastapi.tiangolo.com/
- ChromaDB — https://docs.trychroma.com/
- OpenAI API — https://platform.openai.com/docs
- Sentence Transformers — https://www.sbert.net/
- Ollama — https://ollama.ai/

Recommended citation scaffolding for the hybrid routing study (fill after measurements):
- OpenAI pricing and model cards for selected versions (e.g., GPT-4o)
- Ollama model cards for selected local models (e.g., Llama 3, Mistral)

## 10. Conclusion and Future Work

AI-Tutor evolved from a multi-language prototype with external dependencies into a coherent, locally reproducible research platform with typed interfaces, WebSocket streaming, and hybrid LLM routing. The architecture and documentation emphasize reliability, grounded responses, and cost-aware operation. Next steps include instrumented latency/cost experiments, authentication and role-based features, analytics dashboards, and containerized deployment for broader evaluation.

## Appendix A: Key Endpoints (Backend)

- REST API: `/api/chat`, `/api/upload`, `/api/documents`, `/api/health`
- WebSocket: `ws://localhost:8000/ws/chat`
- Docs: `http://localhost:8000/docs`, `http://localhost:8000/redoc`

## Appendix B: Reproducibility Notes

- Persisted vector store under `FinalProject/backend_python/chroma_db/`
- Environment variables managed via `backend_python/.env.example`
- Deterministic chunking parameters: `CHUNK_SIZE`, `CHUNK_OVERLAP`
- Local-first evaluation recommended prior to cloud deployment
