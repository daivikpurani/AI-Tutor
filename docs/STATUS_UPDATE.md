# RAG AI Tutor — Status Update

## Overview

Recent work has focused on improving retrieval quality, multi-turn conversations, and how we chunk and embed course materials. The system now uses stronger embeddings, reranking, semantic chunking, and better use of conversation history. This document summarizes **what** changed, **why** we made each change, and **why** certain decisions were taken.

---

## 1. Multi-Part & Multi-Turn Conversations

**What changed**

- The tutor keeps **conversation history per user** on the server (last 20 messages).
- Before retrieval, the **current query is compressed with recent history** via a small LLM call so follow-ups like “Explain that again” or “What about X?” are turned into clear, standalone queries for search.
- The **last 8 exchanges** are included in the prompt so the model answers in context of the dialogue.
- The chat API accepts optional **conversation history** from the client and can merge it with server-side history.

**Why we made these changes**

- Users naturally ask **follow-ups** (“And what about X?”, “Explain that again”, “How does that relate to Y?”). Without history, the vector search only sees the latest short message and often retrieves irrelevant or generic chunks, leading to poor or off-topic answers.
- **Query compression** turns the current turn + recent history into a single, self-contained query (e.g. “What about X?” + previous discussion → “How does X relate to [topic from history]?”). That way retrieval is driven by full intent, not just the last sentence.
- We needed a **single source of truth** for history: keeping it on the server (with optional client override) avoids the front end having to send full history on every request and keeps behaviour consistent for WebSocket and REST.

**Decision rationale**

- **Last 20 messages / last 8 in prompt**: Limits context size to avoid token blow-up and irrelevant old turns; 8 exchanges is enough for coherent follow-ups without drowning the prompt. Twenty in storage allows “clear and start fresh” behaviour without losing recent context.
- **Compression via a small LLM call**: We chose a lightweight model (e.g. local Ollama) to keep cost near zero and latency low, while still resolving pronouns and references so the compressed query is meaningful for retrieval.
- **Merge client + server history**: Supports both browser-only clients (no server state) and stateful sessions; server history wins when both are present so WebSocket and REST stay in sync.

**Result**

- Follow-up and multi-part questions are handled with proper context.
- Retrieval is driven by a context-aware, compressed query instead of the raw short message.

---

## 2. Embeddings & Retrieval

**Models and behavior**

- **OpenAI embeddings** (`text-embedding-3-small`) are supported for both indexing and query embedding, with a **local embedding fallback** when OpenAI is off.
- **Cross-encoder reranking**: we use **`cross-encoder/ms-marco-MiniLM-L-6-v2`** (local) to reorder retrieved chunks by relevance after the first retrieval step.
- **Multi-query generation**: a local model (e.g. **Ollama**) generates **2–3 query variants** per turn; we search for each, merge and deduplicate, then rerank. This improves recall for paraphrased or multi-faceted questions.

**Retrieval pipeline**

- Retrieve **12 candidates** (configurable `retrieval_top_k`).
- Apply a **relaxed similarity/distance threshold** so we don’t over-filter.
- **Rerank** with the cross-encoder and keep the **top 6** (`rerank_top_k`).
- **Quality thresholds** for “good enough” retrieval were relaxed (e.g. similarity ~0.55, distance ~1.8) so we only say “I don’t know” when there is truly no useful context.

**Why we made these changes**

- **OpenAI embeddings**: Local sentence-transformers work well for in-domain text but often miss paraphrases and academic phrasing. OpenAI’s `text-embedding-3-small` gives stronger semantic alignment across phrasings and domains, which directly improves recall. We keep a **local fallback** so the system still runs without API keys or when cost is a concern.
- **Reranking**: Bi-encoder search (embed query + chunks, rank by similarity) is fast but can put a highly relevant chunk at position 5 or 6. A **cross-encoder** scores (query, chunk) pairs together, so it can reorder by true relevance. We do “retrieve more, then rerank to top 6” so we don’t miss good chunks that were just below the initial cutoff.
- **Multi-query**: One query can miss relevant chunks if the user phrases things differently than the document. Generating 2–3 variants (e.g. “What is RAG?”, “Explain retrieval-augmented generation”) and merging results increases recall for paraphrased and multi-faceted questions.

**Decision rationale**

- **12 → 6 (retrieve 12, rerank to 6)**: Retrieving 12 gives the reranker enough candidates to promote the best; returning 6 keeps the prompt size and latency under control while still giving the LLM enough context.
- **Relaxed similarity/distance threshold**: The previous strict threshold (e.g. distance < 0.8) caused many good chunks to be dropped before reranking. We relaxed so more candidates reach the reranker; the reranker then does the real filtering. “I don’t know” is reserved for when **no** chunks pass at all.
- **Ollama for multi-query**: Multi-query is a small, cheap task (short output). Using a local model (Ollama) keeps it free and avoids extra API calls; we only need plausible query variants, not the highest-quality prose.
- **ms-marco MiniLM for reranking**: This model is small, fast, and trained for relevance ranking. Running it locally avoids latency and cost from a hosted reranker while still improving order of chunks.

**Result**

- Better semantic match and ordering of chunks; fewer unnecessary “I don’t know” answers; better behavior on paraphrased and multi-part questions.

---

## 3. Chunking & Context

**Chunking**

- **Semantic chunking** is enabled via **LangChain’s RecursiveCharacterTextSplitter**, with separators that respect **markdown headers** (e.g. `##`, `###`), **paragraphs**, then **sentences and words**. New uploads use this when the option is on.
- Chunk size and overlap remain configurable; the splitter is used for all new document processing when semantic chunking is enabled.

**Context window**

- **Maximum context length** sent to the LLM was increased (e.g. from 2,000 to **4,500 characters**), so the model sees more of the retrieved material per turn.

**Why we made these changes**

- **Fixed-size chunking** (e.g. “every 1000 characters”) often splits in the middle of a sentence or section, so the model gets incomplete definitions or broken lists. That hurt answer quality and made citations confusing. We wanted **semantic boundaries**: splits at headers, paragraphs, then sentences, so each chunk is a coherent unit.
- **2,000 characters** was too small for questions that need several concepts or a short proof; the model often lacked the next sentence that completed the thought. Increasing to **4,500** gives room for 6 reranked chunks without blowing the context window or latency.

**Decision rationale**

- **RecursiveCharacterTextSplitter with markdown-first separators**: Course materials and papers often use markdown or heading-like structure. Splitting on `##`, `###`, `\n\n`, then `\n`, then sentence/word keeps sections and paragraphs intact. We use LangChain’s implementation so we don’t maintain custom regex logic.
- **4,500 characters**: Balances “enough context to answer well” with “don’t overload the prompt.” It fits 6 chunks of ~700 chars each with some overlap; we can tune down if we need to reduce tokens or cost.
- **Semantic chunking only for new uploads by default**: Existing documents were already indexed with the old chunker. Re-chunking requires a **migration** (re-index) so we didn’t force it automatically; new uploads get the better chunking immediately.

**Result**

- Chunks align better with sections and topics; the model gets more (and more coherent) context per query.

---

## 4. Prompts & “I don’t know” Logic

**What changed**

- Tutor and retrieval prompts were **simplified**: we rely on the **reranker** to surface good context and no longer apply overly strict “quality” rules that triggered “I don’t know” too often.
- “I don’t know” is now used only when **no context chunks** are available at all (`chunk_count == 0`).
- All prompt context limits use the **configurable max context length** (e.g. 4,500 characters) instead of a fixed 2,000.

**Why we made these changes**

- The previous prompts included **strict quality rules** (e.g. “if similarity is below X, say I don’t know”). In practice, similarity scores were noisy and often rejected good chunks, so the tutor said “I don’t know” even when the reranker had found relevant content. That hurt user trust and made the system feel broken.
- We already invested in **reranking** to put the best chunks first. Duplicating that with extra “quality” checks in the prompt was redundant and caused false negatives. We decided to **trust the reranker**: if we have chunks, we pass them to the LLM and let it answer; we only say “I don’t know” when we have **zero** chunks.

**Decision rationale**

- **“I don’t know” only when chunk_count == 0**: Simple rule: no context → no answer. Any non-empty reranked set is considered usable; the LLM can still say “this isn’t in the materials” in its reply if the content is off-topic.
- **Removed strict similarity/distance wording from prompts**: We no longer tell the model “if retrieval quality is poor, refuse to answer.” That wording was causing over-refusal. The model still sees retrieval metadata if we pass it, but we don’t mandate refusal.
- **Configurable max context length in prompts**: Replacing the hardcoded 2,000 with the same config value (e.g. 4,500) used elsewhere keeps behaviour consistent and makes it easy to tune one place.

**Result**

- Fewer false “I don’t know” responses; answers are given whenever the reranker returns relevant chunks.

---

## 5. Migration Path for Existing Content

**What’s available**

- A **migration workflow** re-indexes existing course materials so they benefit from the new setup:
  - Export existing documents from the vector store.
  - Reset the collection.
  - **Re-chunk** with the semantic splitter (LangChain).
  - **Re-embed** with the chosen embedding model (e.g. OpenAI `text-embedding-3-small` if enabled).
  - Re-index into ChromaDB.

**When to use it**

- Run this when you want **existing documents** to use the new chunking and embedding models. New uploads already use semantic chunking when enabled; migration brings old content in line.

**Cost note**

- If using OpenAI for re-embedding, re-indexing is on the order of a few cents for typical course-material sizes (e.g. ~$0.02 for on the order of 100 docs).

**Why we added a migration path**

- Existing documents were indexed with **old chunk sizes**, **old (e.g. local) embeddings**, and no semantic boundaries. Turning on OpenAI embeddings or semantic chunking only affects **new** uploads; old chunks stay as they are. Without a way to **re-index**, we’d have a mixed store (some chunks good, some weak) and inconsistent retrieval.
- A **single migration script** that exports → reset → re-chunk → re-embed → re-index lets us bring all content in line with the new pipeline in one go, with clear logging and no manual re-upload.

**Decision rationale**

- **Export then reset**: We export document content/metadata first so we can re-process from originals (or stored text). Resetting the collection avoids duplicate or conflicting chunks from mixing old and new embedding models.
- **Re-chunk then re-embed**: Chunking must happen before embedding because each chunk is embedded separately. Doing both in one script keeps the process repeatable and document-atomic.
- **Optional OpenAI in migration**: Migration can run with local embeddings only (no cost) or with OpenAI for better quality; we don’t force a paid path so labs or air-gapped setups can still use it.

---

## 6. Configuration Summary

| Area | What we're using / changing |
|------|-----------------------------|
| **Embeddings** | OpenAI `text-embedding-3-small` (optional) + local fallback |
| **Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local) |
| **Multi-query** | 2–3 variants via Ollama (or configured local model) |
| **Retrieval** | 12 candidates → rerank → top 6; relaxed similarity/distance thresholds |
| **Context** | Max context length ~4,500 characters (configurable) |
| **Chunking** | Semantic splitter (LangChain) with markdown/paragraph/sentence separators |
| **Conversation** | Server-side history (last 20 msgs); last 8 turns in prompt; query compression with history |

---

## 7. Expected Impact

| Metric | Before | After |
|--------|--------|--------|
| "I don't know" rate | High (strict thresholds) | Much lower; only when no context |
| Context relevance | Moderate (single embedding, no rerank) | Higher (OpenAI + reranking + multi-query) |
| Answer context | 5 chunks, ~2K chars | 6 reranked chunks, ~4.5K chars |
| Multi-turn / follow-ups | Limited | Query compression + history in prompt |
| Chunk quality | Fixed-size splits | Semantic boundaries (headers, paragraphs) |

---

## 8. Current State & Next Steps

- **Live now**: Reranking, relaxed thresholds, larger context, multi-query (when Ollama is running), semantic chunking for **new** uploads, and multi-turn conversation with history and query compression.
- **Optional**: Run the **migration** to re-chunk and re-embed **existing** documents with the new models and chunking for maximum quality.
- **Optional**: Enable **OpenAI embeddings** and re-index (via migration) for best retrieval; local embeddings remain supported for cost-free operation.
