# Weekly Research Update

## Last Week's Tasks

- Implemented security hardening for the AI-Tutor backend: prompt-injection guards, rate limiting, and input sanitization.
- Added API and config safeguards: request length limits, filename sanitization, and configurable rejection of suspicious prompts.
- Consolidated and cleaned documentation: removed redundant status/progress/benchmark docs and aligned README, QUICK_START, and DEVELOPER with the current stack and security model.
- Carried over RAG and retrieval improvements from the previous weekend: OpenAI embeddings, cross-encoder reranking, semantic chunking, and migration tooling for re-indexing.

## Completed Work

- **Prompt security:** Introduced `prompt_guard` module with injection-pattern detection (e.g. “ignore previous instructions”, “reveal your prompt”), user-message sanitization (strip, truncate to 2000 chars, collapse newlines), and wrapping of user content in `<<<USER_QUESTION>>>` … `<<<END_USER_QUESTION>>>` so the model treats it as data. System prompts were updated with explicit “CRITICAL - Prompt security” instructions. When `REJECT_ON_INJECTION=true`, detected injection returns a safe message without calling the LLM. Logging of prompt/response content was stopped to avoid leaking instructions.
- **API hardening:** Chat and upload endpoints are rate-limited via SlowAPI (configurable `RATE_LIMIT_CHAT`, `RATE_LIMIT_UPLOAD` in `.env`). `ChatRequest` enforces `message` max length 2000 and `conversation_history` max 20 entries. All file upload paths use a new `filename_sanitizer`: strip path components, remove control characters, validate extension against allowed types, cap length at 255. In production, generic 500 responses avoid exposing internals.
- **Config and tests:** Added `backend_python/.env.example` with `REJECT_ON_INJECTION`, rate limits, and CORS; all references updated from `env.example` to `.env.example`. New tests: `test_prompt_guard.py` (detection, sanitize, wrap) and `test_chat_rejects_injection_when_enabled` in `test_api.py`.
- **Docs consolidation:** README, QUICK_START, and DEVELOPER updated for current stack and security. Removed redundant status/progress/benchmark/startup docs. Single entry point for benchmarking: `docs/BENCHMARK.md` plus `docs/BENCHMARK_DETAILED.md`; `scripts/benchmarks/README.md` for benchmark scripts. PDF generation uses `BENCHMARK_DETAILED`.
- **RAG improvements (previous weekend):** OpenAI embeddings and cross-encoder reranking for better retrieval; semantic chunking (LangChain) in document chunker; configurable retrieval parameters and thresholds; migration script for re-indexing with new embeddings/chunking; query-handler and vector-db updates documented in implementation and testing notes.

## Security & Improvement Areas (What We Implemented)

**Prompt and input guards**

- Injection-pattern detection with configurable reject-on-detect.
- User-message sanitization (length, control chars, newlines) and delimiter wrapping in all prompts.
- Hardened system prompts that instruct the model to treat only delimited content as the user question.

**API and request safety**

- SlowAPI rate limits on chat and upload endpoints (e.g. 60/min chat, 10/min upload).
- Pydantic request limits: message length, conversation history length.
- CORS configuration via `.env` (e.g. `CORS_ORIGINS`).

**File and filename safety**

- Dedicated `filename_sanitizer`: no path traversal, no control chars, allowed-extension checks, max filename length.
- Applied to all upload flows (single, multiple, and title-based filename creation).

**Operations and documentation**

- Production mode: generic 500, no prompt/response logging.
- Single `.env.example` with security and CORS; DEVELOPER and README document rate limits, prompt security, and optional rejection.

## Summary of Security & Hardening

The work is organized into four layers:

**Prompt layer**

- Wraps user input in delimiters and checks for injection patterns.
- Optional rejection with a safe message when injection is detected.
- Reduces risk of instruction override and prompt leaking.

**API layer**

- Rate limits on chat and upload to curb abuse and cost.
- Request schema limits (message length, history size) to keep payloads bounded.
- CORS restricted to configured origins.

**Input layer**

- Sanitized user messages (length, control chars) before inclusion in prompts.
- Sanitized filenames (path stripping, extension allowlist) on all uploads.
- Ensures only safe, validated input reaches the RAG pipeline and storage.

**Docs and ops layer**

- Consolidated benchmark and developer docs; single BENCHMARK entry + BENCHMARK_DETAILED.
- Security and config documented in README, DEVELOPER, and `.env.example`.
- Production guidance: `ENVIRONMENT=production`, strong `SECRET_KEY`, no sensitive logging.

## Insights

- Prompt injection detection plus delimiter wrapping significantly narrows the attack surface for instruction override and prompt extraction; optional reject mode gives a strict option for higher-risk deployments.
- Rate limiting and request limits are simple to configure (SlowAPI + Pydantic) and protect both cost and availability without changing core RAG logic.
- Filename sanitization and extension checks prevent path traversal and arbitrary file types; one shared module keeps behavior consistent across all upload endpoints.
- Documentation consolidation (single benchmark entry, one DEVELOPER guide, aligned README) makes it easier for new contributors and evaluators to find security and run instructions.

## Next Week

- Continue reading and refining the benchmarking methodology (BENCHMARK_DETAILED, evaluation layers, and scripts).
- Run a small-scale benchmark pass with the current security and RAG stack to confirm no regressions and document any latency/behavior notes.

## Concrete Security Checks Added

**Prompt injection detection (`utils/prompt_guard.py`)**

- **Patterns checked (19 regexes, case-insensitive):** e.g. `ignore (all)? (previous|above|prior) instructions`, `disregard/forget ... instructions`, `you are now`, `new instructions:`, `system:`, `assistant:`, `[system]`, `[instruction]`, `<|system|>`, `<|user|>`, `<|assistant|>`, `repeat (the)? (above|previous) (instructions|prompt)`, `reveal/print/output (your)? (instructions|prompt|system prompt)`, `what are your instructions`, `show (me)? (your)? (full)? (system)? prompt`, `### instruction`, `--- instruction`.
- **Where applied:** Before every LLM call in `query_handler` (REST chat, benchmark chat, WebSocket, and any code path that processes a user query). If `REJECT_ON_INJECTION=true` (configurable in `.env`), the request is rejected with a safe canned message and the LLM is not called.
- **User message sanitization:** Strip leading/trailing whitespace; remove null bytes and control characters (keep only `\n` and `ord(c) >= 32`); collapse 3+ newlines to 2; truncate to 2000 characters (configurable `max_length`). Applied before wrapping in delimiters.
- **Delimiter wrapping:** User content is always wrapped as `<<<USER_QUESTION>>>` … `<<<END_USER_QUESTION>>>` in prompts; system prompts include an explicit “CRITICAL - Prompt security” line instructing the model to treat only that block as the user question.

**Request and schema limits (`models/schemas.py`, Pydantic)**

- **ChatRequest:** `message` max length 2000; `user_id` max 50; `conversation_history` max 20 entries (validator enforces); `mode` max 20. Requests that exceed these are rejected with validation errors before reaching the handler.
- **Rate limits (SlowAPI, per client IP):** `/api/chat` and `/api/chat_benchmark`: `RATE_LIMIT_CHAT` (default `60/minute`); `/api/upload` and multi-upload: `RATE_LIMIT_UPLOAD` (default `10/minute`). Configurable in `.env`; `RateLimitExceeded` returns 429.

**Filename sanitization (`utils/filename_sanitizer.py`)**

- **Path stripping:** `os.path.basename()` so paths like `../../../etc/passwd` become only the final component.
- **Character rules:** Remove control characters and DEL (ord &lt; 32 or ord 127); replace `<>:"|?*` and `\x00-\x1f` with `_`; collapse multiple `_` and strip leading/trailing `_.`.
- **Length:** Max 255 characters (base truncated if needed, extension preserved).
- **Extension check:** Case-insensitive allowlist from config (`allowed_file_types`: `.txt`, `.md`, `.pdf`, `.docx`, `.doc`). If `require_extension=True`, invalid or missing extension raises `ValueError` (API returns 400/500).
- **Applied on:** Single-file upload, multi-file upload, and title-based document creation (all use `sanitize_filename` with `settings.allowed_file_types`).

**CORS and error handling**

- **CORS:** Origins taken from `CORS_ORIGINS` in `.env` (comma-separated); production override in config. No wildcard in production.
- **Production 5xx:** When `ENVIRONMENT=production`, 500 responses use a generic message (`_error_detail`) so stack traces and internal details are not exposed to the client.
- **Config:** `REJECT_ON_INJECTION`, `RATE_LIMIT_CHAT`, `RATE_LIMIT_UPLOAD`, `CORS_ORIGINS`, and `SECRET_KEY` documented in `backend_python/.env.example` and README/DEVELOPER.

**Where injection is checked**

- `query_handler.process_query_with_metadata` (REST and benchmark).
- WebSocket message handling and any other entry that passes user text to the LLM (multiple call sites in `query_handler.py` so all paths are covered).

---

## Future Updates (Planned)

1. **User authentication and sessions** — Add optional auth (e.g. API key or session-based) and role-based access so that rate limits and logging can be scoped per user and prepared for multi-tenant or lab deployments.
2. **Stricter production defaults** — Consider defaulting `REJECT_ON_INJECTION=true` and tighter rate limits when `ENVIRONMENT=production`, with clear docs and migration steps for existing deployments.
3. **Upload file-size enforcement** — Enforce `max_file_size` (e.g. 10 MB) at the API layer: reject uploads over the limit before writing to disk and return 413 Payload Too Large with a clear message.
4. **Security headers and CSP** — Add middleware for `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` (or `SAMEORIGIN`), and optionally a Content-Security-Policy for the docs/frontend origin to reduce XSS and clickjacking surface.
5. **Audit logging** — Log security-relevant events (injection rejections, rate-limit hits, upload failures, auth failures) to a dedicated audit log or file without logging prompt/response content, for forensics and tuning.
6. **Input encoding for responses** — Ensure all user-generated content reflected in API responses (e.g. echoed query, filenames) is properly encoded/escaped to prevent XSS when the frontend renders the response.
