# Hybrid LLM Latency and Cost Trade-offs Technical Report

## Executive Summary

- **Goal**: Evaluate latency and cost trade-offs of hybrid LLM routing across OpenAI GPT-4o and a local Ollama model.
- **Key findings**: To be populated after measurement. Expected pattern: GPT-4o offers lower tail latency and higher quality at higher per-token cost; Ollama offers near-zero marginal cost with higher variance depending on model/hardware.

## System Overview

- **Hybrid router**: `backend_python/services/llm_service.py` implements `HybridLLMService` and `QueryComplexityAnalyzer` to route SIMPLE/COMPLEX/UNKNOWN queries by provider preference and availability.
- **Providers**:
  - **OpenAI (GPT-4o)** via `OpenAIProvider` (returns token usage; pricing-derived cost).
  - **Ollama (model TBD)** via `OllamaProvider` (no token usage; treat marginal cost as $0; note infra amortization separately).
- **Interaction modes**: Non-streaming and streaming paths; measure time-to-first-byte (TTFB) and total generation time in both.

## Assumptions

- **Workload**: 3 buckets (simple, medium, complex); 10 exemplars each; 1 cold run + 3 warm runs per exemplar.
- **Environment**: Single client; stable network; Ollama on local node; identical prompts across providers.
- **Model parameters**: `max_tokens = 1000`, `temperature = 0.7`.
- **Cost placeholders**:
  - **GPT-4o**: Fill current pricing per 1K input/output tokens.
  - **Ollama**: $0 marginal; optionally add monthly compute amortization (e.g., GPU/CPU costs).

## Methodology

- **Metrics**:
  - **Latency**: TTFB, total time (p50/p95/p99), tokens/sec (OpenAI), chars/sec proxy (Ollama).
  - **Cost**: $/request, $/1K tokens, monthly projection at N requests/day.
  - **Routing**: Provider hit rate by complexity class, fallback frequency, error rate.
- **Procedure**:
  - For each query exemplar, run 1 cold then 3 warm trials.
  - Record timestamps for request send, first chunk received, last chunk received; token usage (OpenAI), response length, chosen provider, fallback flags, errors.
- **Instrumentation plan (to implement)**:
  - Add timers around `HybridLLMService.generate_response` and `generate_streaming_response`.
  - Capture first-yield times inside provider adapters and `QueryHandler._generate_streaming_response`.
  - Persist JSONL logs (one record per trial) with fields shown in the Data Schema below.

## Datasets and Workloads

- **Query sets**:
  - **Simple**: Definitional, yes/no, short "what is …".
  - **Medium**: "How does … work?", single-process explanations.
  - **Complex**: Compare/contrast, multi-step analyses.
- Assign stable IDs per query to align results across runs.

## Results Templates (Fill After Measurement)

### Latency by Provider

| Provider | Mode | p50 TTFB (ms) | p95 TTFB (ms) | p50 Total (ms) | p95 Total (ms) | Notes |
|---------|------|---------------|---------------|----------------|----------------|-------|
| GPT-4o  | Non-stream |  |  |  |  |  |
| GPT-4o  | Streaming  |  |  |  |  |  |
| Ollama  | Non-stream |  |  |  |  |  |
| Ollama  | Streaming  |  |  |  |  |  |

### Streaming Throughput

| Provider | Mode | Avg tokens/sec (out) | Stddev | Trials |
|----------|------|----------------------|--------|--------|
| GPT-4o   | Streaming |  |  |  |
| Ollama   | Streaming | (chars/sec proxy) |  |  |

### Cost per Request

| Provider | Avg input tokens | Avg output tokens | Cost per 1K in | Cost per 1K out | Cost/req ($) |
|----------|-------------------|-------------------|----------------|-----------------|--------------|
| GPT-4o   |  |  |  |  |  |
| Ollama   | N/A | N/A | 0 | 0 | 0 |

### Routing Impact

| Complexity | Provider hit rate | Avg cost/req ($) | Avg total ms | Errors |
|------------|-------------------|------------------|--------------|--------|
| Simple     |  |  |  |  |
| Medium     |  |  |  |  |
| Complex    |  |  |  |  |

## Analysis Scaffolding

- **Latency trade-offs**: GPT-4o typically achieves faster/stabler tails; Ollama variance depends on chosen model and host hardware.
- **Cost trade-offs**: GPT-4o cost scales with tokens; Ollama marginal $0 but consumes local compute. Token minimization directly reduces spend.
- **Sensitivity**: Model choice, prompt length, and complexity classification accuracy drive both latency and spend.
- **Failure/fallback**: Document fallback rate and its impact on tail latency and reliability.

## Recommendations (Finalize After Data)

- **Routing policy**: SIMPLE → Ollama; COMPLEX → GPT-4o; UNKNOWN → confidence-threshold route with token/latency budget guardrails.
- **Budgets and safeguards**: Per-class max tokens; monthly cost caps; circuit breaker to Ollama when OpenAI errors or latency > threshold.
- **Prompt shaping**: Keep `SYSTEM` stable; compress context; avoid unnecessary verbosity.
- **Operational**: Cache embeddings/context; reuse conversation state; batch where feasible.

## Next Steps (Measurement Plan)

1. Select Ollama model (e.g., `llama3:8b` or `mistral:7b`) and quantization (e.g., Q4_K_M); note hardware.
2. Implement JSONL logging and timers at the call-sites listed in Methodology.
3. Run 120–180 trials across the three query sets; compute p50/p95; populate tables.
4. Draft final recommendations from observed trade-offs and routing hit rates.

## Data Schema (JSONL per Trial)

```json
{
  "trial_id": "uuid",
  "timestamp": "ISO-8601",
  "query_id": "string",
  "complexity": "simple|medium|complex|unknown",
  "provider": "openai|ollama|mock",
  "mode": "streaming|non_streaming",
  "ttfb_ms": 0,
  "total_ms": 0,
  "openai_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
  "response_chars": 0,
  "tokens_per_sec": 0,
  "chars_per_sec": 0,
  "fallback_used": false,
  "error": null,
  "notes": ""
}
```

## References

- `backend_python/services/llm_service.py` (hybrid routing and providers)
- `backend_python/services/query_handler.py` (query orchestration, streaming path)
- OpenAI pricing (fill with current GPT-4o rates)
- Ollama model card for selected model
