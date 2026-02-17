"""
Enhanced Query Handler with Hybrid LLM Integration
Processes user queries using multiple LLM providers with intelligent routing.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import logging

from services.vector_db import VectorDatabase
from services.llm_service import HybridLLMService, LLMResponse
from utils.prompts import PromptTemplates
from utils.config import settings
from utils.prompt_guard import detect_injection

logger = logging.getLogger(__name__)

# Hardcoded two-turn demo Q&A for RAG-related demos (quick, reliable answers)
DEMO_QA = [
    {
        "turn1_q": ["what is rag", "what is retrieval augmented generation", "explain rag"],
        "turn1_a": "RAG stands for Retrieval-Augmented Generation. It combines a search step over your documents with an LLM: we retrieve relevant chunks first, then the model answers using that context.",
        "turn2_q": ["how does retrieval work", "how do you retrieve", "what gets retrieved"],
        "turn2_a": "We embed your question and the document chunks, search the vector DB for the closest chunks, then optionally rerank them. The top chunks are passed to the LLM as context.",
    },
    {
        "turn1_q": ["what are embeddings", "what is an embedding", "how do embeddings work"],
        "turn1_a": "Embeddings are dense vectors that represent text. Similar meanings get similar vectors, so we can find relevant passages by comparing query and chunk embeddings.",
        "turn2_q": ["why use them in rag", "why embeddings for retrieval", "how do they help the tutor"],
        "turn2_a": "Embeddings let us do semantic search: we find chunks by meaning, not just keywords. That’s why the tutor can answer paraphrased questions and follow-ups.",
    },
    {
        "turn1_q": ["what is a vector database", "what is vector db", "how does chroma work"],
        "turn1_a": "A vector database stores embeddings and supports fast similarity search. We use it to quickly find the document chunks most relevant to your question.",
        "turn2_q": ["how does it help the tutor", "why use a vector db for the tutor", "how does that help answers"],
        "turn2_a": "The tutor sends your question to the vector DB, gets the best-matching chunks, then the LLM reads those chunks and generates a grounded, cited answer.",
    },
    {
        "turn1_q": ["how does this tutor work", "how does the ai tutor work", "how does the tutor find answers"],
        "turn1_a": "The tutor uses RAG: it searches your course materials with embeddings, reranks the results, then an LLM generates an answer using only that retrieved context.",
        "turn2_q": ["what is reranking", "why rerank", "what does reranking do"],
        "turn2_a": "Reranking uses a small model to rescore the retrieved chunks by relevance to your exact question. It improves precision so the LLM sees the best passages first.",
    },
]


class QueryHandler:
    """
    Enhanced query handler with LLM integration and vector database support.
    """
    
    def __init__(self, vector_db: VectorDatabase = None):
        """
        Initialize the query handler.
        
        Args:
            vector_db: VectorDatabase instance for document retrieval
        """
        self.vector_db = vector_db or VectorDatabase()
        self.llm_service = HybridLLMService()
        self.conversation_history = []
        self.prompt_templates = PromptTemplates()
        
        # Initialize hybrid LLM service (will be called asynchronously)
        self._llm_service_initialized = False

    def _normalize_text(self, text: str) -> str:
        """Lowercase, strip, and remove punctuation for stable intent matching."""
        if not text:
            return ""
        lowered = text.lower().strip()
        # keep alphanumerics and spaces only
        normalized = re.sub(r"[^a-z0-9\s]+", "", lowered)
        # collapse multiple spaces
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _get_demo_response(
        self, query: str, conversation_history: List[Dict] = None, user_id: str = None
    ) -> Optional[str]:
        """If query matches a demo Q&A script (turn 1 or 2), return the hardcoded answer; else None."""
        norm = self._normalize_text(query)
        if not norm:
            return None
        history = conversation_history or self.get_conversation_history(user_id) or []
        # Last assistant message (for turn-2 detection)
        last_assistant = None
        for entry in reversed(history):
            if entry.get("role") == "assistant":
                last_assistant = (entry.get("message") or "").strip()
                break
        for script in DEMO_QA:
            # Turn 2: last reply was our turn1 answer and current query matches turn2
            if last_assistant and script["turn1_a"].strip() == last_assistant:
                for q in script["turn2_q"]:
                    if q in norm or norm in q:
                        return script["turn2_a"]
            # Turn 1: current query matches turn1
            for q in script["turn1_q"]:
                if q in norm or norm in q:
                    return script["turn1_a"]
        return None
    
    async def _ensure_llm_service_initialized(self):
        """Ensure hybrid LLM service is initialized."""
        if not self._llm_service_initialized:
            try:
                await self.llm_service.initialize()
                available_providers = self.llm_service.get_available_providers()
                logger.info(f"Hybrid LLM service initialized with providers: {available_providers}")
                self._llm_service_initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize hybrid LLM service: {e}")
                self._llm_service_initialized = False
    
    async def process_query(
        self, 
        query: str, 
        user_id: str = None, 
        conversation_history: List[Dict] = None,
        mode: str = "exploration"
    ) -> Dict[str, Any]:
        """
        Process a user query and return a response.
        
        Args:
            query: User's question or input
            user_id: Unique identifier for the user
            conversation_history: Previous conversation context
            mode: Learning mode ('exploration' or 'assessment')
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Ensure LLM service is initialized
            await self._ensure_llm_service_initialized()

            # Demo: hardcoded two-turn RAG Q&A for reliable demos
            demo_response = self._get_demo_response(
                query, conversation_history or self.get_conversation_history(user_id), user_id
            )
            if demo_response is not None:
                await asyncio.sleep(1.5)  # Brief delay so demo feels natural
                self._add_to_history(query, 'user', user_id)
                self._add_to_history(demo_response, 'assistant', user_id)
                return {
                    'response': demo_response,
                    'query': query,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'context_chunks_used': 0,
                    'status': 'success',
                    'citations': [],
                    'tldr': (demo_response[:157] + '...') if len(demo_response) > 160 else demo_response,
                }

            # Prompt injection guard: reject or pass through based on config
            injected, _ = detect_injection(query)
            if getattr(settings, 'reject_on_injection', False) and injected:
                logger.warning("Prompt injection pattern detected; rejecting request")
                safe_msg = "I can only answer questions about the course materials. Please ask something about the content you're learning."
                self._add_to_history(query, 'user', user_id)
                self._add_to_history(safe_msg, 'assistant', user_id)
                return {
                    'response': safe_msg,
                    'query': query,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'context_chunks_used': 0,
                    'status': 'success',
                    'citations': [],
                    'tldr': safe_msg[:160],
                }
            
            # Store query in conversation history
            self._add_to_history(query, 'user', user_id)
            
            # Compress query with brief history for targeted retrieval
            compressed_query = await self._compress_query(query, conversation_history or self.get_conversation_history(user_id))
            # Get relevant context from vector database
            context_chunks = await self._get_relevant_context(compressed_query)
            
            # Assess retrieval quality for uncertainty handling
            retrieval_quality = self._assess_retrieval_quality(context_chunks)
            logger.debug(f"Retrieval quality assessment: {retrieval_quality}")
            
            # Use server-held recent history for this user; merge with provided if any
            user_history = self.get_conversation_history(user_id)
            if conversation_history:
                user_history = (user_history or []) + conversation_history
            
            # Generate response using LLM
            response = await self._generate_llm_response(
                query, 
                context_chunks, 
                user_history,
                mode,
                retrieval_quality
            )
            
            # Store response in conversation history
            self._add_to_history(response, 'assistant', user_id)
            
            # Build citations from context chunks
            citations = []
            for chunk in context_chunks:
                meta = chunk.get('metadata', {}) if isinstance(chunk, dict) else {}
                title = meta.get('title') or meta.get('filename') or 'Source'
                url = meta.get('url') or meta.get('source_url')
                distance = chunk.get('distance') if isinstance(chunk, dict) else None
                score = None
                try:
                    if isinstance(distance, (int, float)):
                        score = round(1.0 / (1.0 + float(distance)), 4)
                except Exception:
                    score = None
                citations.append({
                    'title': title,
                    'url': url,
                    'score': score
                })

            # Simple TL;DR: first sentence up to ~160 chars
            tldr = None
            if response:
                first_sentence = response.split('\n')[0].strip()
                tldr = (first_sentence[:157] + '...') if len(first_sentence) > 160 else first_sentence

            return {
                'response': response,
                'query': query,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'context_chunks_used': len(context_chunks),
                'status': 'success',
                'citations': citations,
                'tldr': tldr
            }
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error processing your query: {str(e)}"
            logger.error(f"Error processing query: {e}")
            return {
                'response': error_response,
                'query': query,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
    
    def _select_best_document_chunks(
        self, candidates: List[Dict], top_k: int
    ) -> List[Dict]:
        """
        When multiple documents appear in results, prefer the best-matching document
        so we don't mix irrelevant chunks from a wrong doc.
        """
        if not candidates or top_k <= 0:
            return []
        if len(candidates) <= top_k:
            # Check if all from same doc - return as-is
            filenames = {c.get("metadata", {}).get("filename", "") for c in candidates}
            if len(filenames) <= 1:
                return candidates
        # Group by document (filename)
        by_doc: Dict[str, List[Dict]] = {}
        for c in candidates:
            fn = c.get("metadata", {}).get("filename", "")
            by_doc.setdefault(fn, []).append(c)
        # Find the document with the best top chunk (by rerank_score or lowest distance)
        def doc_score(chunks: List[Dict]) -> float:
            if not chunks:
                return float("-inf")
            c = chunks[0]
            if "rerank_score" in c:
                return float(c.get("rerank_score", 0))
            return -float(c.get("distance", float("inf")))
        best_doc = max(by_doc.keys(), key=lambda fn: doc_score(by_doc[fn]))
        return by_doc[best_doc][:top_k]
    
    async def _generate_multi_queries(self, query: str) -> List[str]:
        """
        Generate 2-3 query variants for better recall using Ollama (free).
        
        Args:
            query: Original user query
            
        Returns:
            List of query variants (including original)
        """
        if not settings.enable_multi_query:
            return [query]
        
        try:
            prompt = f"Generate 2 alternative phrasings of this query. Return ONLY the queries, one per line, no numbering:\n\n{query}"
            
            # Use Ollama for free multi-query generation
            response = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                query=query,
                max_tokens=100,
                temperature=0.3
            )
            
            # Parse variants
            variants = [query]  # Start with original
            if response and response.content:
                lines = [line.strip() for line in response.content.strip().split('\n') if line.strip()]
                # Filter out lines that are just numbers or very short
                valid_lines = [l for l in lines if len(l) > 10 and not l[0].isdigit()]
                variants.extend(valid_lines[:2])  # Take up to 2 variants
            
            logger.info(f"Generated {len(variants)} query variants")
            return variants[:3]  # Max 3 total (original + 2 variants)
            
        except Exception as e:
            logger.warning(f"Multi-query generation failed: {e}. Using original query only.")
            return [query]
    
    async def _get_relevant_context(self, query: str, n_results: int = None) -> List[Dict]:
        """
        Retrieve relevant context chunks with multi-query and reranking.
        
        Args:
            query: User query to find context for
            n_results: Number of relevant chunks to retrieve (uses config default if None)
            
        Returns:
            List of relevant context chunks (reranked if enabled)
        """
        try:
            # Generate query variants if enabled
            queries = await self._generate_multi_queries(query)
            
            # Use new search_similar_with_rerank method
            if settings.enable_reranking:
                # Retrieve more candidates so we can pick the best-matching document when multiple docs exist
                rerank_top_k_extended = max(settings.rerank_top_k + 9, 15)  # Get 15+ to allow doc selection
                
                # Multi-query: retrieve from all variants and deduplicate
                if len(queries) > 1:
                    all_chunks = []
                    seen_ids = set()
                    
                    for q in queries:
                        chunks = await self.vector_db.search_similar_with_rerank(
                            query=q,
                            n_results=settings.retrieval_top_k,
                            rerank_top_k=rerank_top_k_extended
                        )
                        for chunk in chunks:
                            chunk_id = chunk.get('id')
                            if chunk_id and chunk_id not in seen_ids:
                                all_chunks.append(chunk)
                                seen_ids.add(chunk_id)
                    
                    # Re-sort by rerank score if available, otherwise by distance
                    if all_chunks and 'rerank_score' in all_chunks[0]:
                        all_chunks.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
                    else:
                        all_chunks.sort(key=lambda x: x.get('distance', float('inf')))
                    
                    context_chunks = self._select_best_document_chunks(
                        all_chunks[:rerank_top_k_extended], settings.rerank_top_k
                    )
                else:
                    # Single query with reranking - get extra candidates for doc selection
                    raw_chunks = await self.vector_db.search_similar_with_rerank(
                        query=query,
                        n_results=settings.retrieval_top_k,
                        rerank_top_k=rerank_top_k_extended
                    )
                    context_chunks = self._select_best_document_chunks(raw_chunks, settings.rerank_top_k)
            else:
                # Fallback to old method without reranking
                context_chunks = await self.vector_db.search_similar(
                    query, 
                    n_results or settings.max_context_chunks
                )
            
            logger.info(f"Retrieved {len(context_chunks)} context chunks (multi-query: {len(queries) > 1}, reranking: {settings.enable_reranking})")
            return context_chunks
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return []
    
    def _assess_retrieval_quality(self, context_chunks: List[Dict]) -> Dict[str, Any]:
        """
        Assess the quality of retrieved context chunks.
        
        Args:
            context_chunks: List of retrieved context chunks with distance/similarity scores
            
        Returns:
            Dictionary with retrieval quality metrics
        """
        if not context_chunks:
            return {
                'chunk_count': 0,
                'avg_similarity': 0.0,
                'avg_distance': float('inf'),
                'has_good_retrieval': False,
                'quality_level': 'none'
            }
        
        # Extract distances and calculate similarities
        distances = []
        similarities = []
        
        for chunk in context_chunks:
            distance = chunk.get('distance', 2.0)
            distances.append(distance)
            # Convert distance to similarity (assuming cosine distance)
            # For cosine distance: similarity ≈ 1 - distance (when normalized)
            # For L2 distance: similarity ≈ 1 / (1 + distance)
            similarity = 1.0 / (1.0 + float(distance)) if distance > 0 else 1.0
            similarities.append(similarity)
        
        avg_distance = sum(distances) / len(distances) if distances else float('inf')
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        # Very relaxed quality thresholds - trust the reranker to filter quality
        # Good retrieval: avg_similarity > 0.40 or avg_distance < 2.5
        has_good_retrieval = (
            avg_similarity > settings.good_retrieval_similarity or 
            avg_distance < settings.good_retrieval_distance
        ) if len(context_chunks) > 0 else False
        
        # Determine quality level (very lenient - trust reranker)
        if len(context_chunks) == 0:
            quality_level = 'none'
        elif has_good_retrieval:
            quality_level = 'good'
        elif avg_similarity > 0.30 and avg_distance < 2.5:  # Very lenient moderate threshold
            quality_level = 'moderate'
        else:
            quality_level = 'poor'
        
        result = {
            'chunk_count': len(context_chunks),
            'avg_similarity': avg_similarity,
            'avg_distance': avg_distance,
            'has_good_retrieval': has_good_retrieval,
            'quality_level': quality_level,
            'min_distance': min(distances) if distances else float('inf'),
                'max_distance': max(distances) if distances else float('inf')
        }
        
        return result
    
    async def _generate_llm_response(
        self, 
        query: str, 
        context_chunks: List[Dict], 
        conversation_history: List[Dict] = None,
        mode: str = "exploration",
        retrieval_quality: Dict[str, Any] = None
    ) -> str:
        """
        Generate response using hybrid LLM service.
        
        Args:
            query: User's question
            context_chunks: Relevant context from vector database
            conversation_history: Previous conversation context
            mode: Learning mode ('exploration' or 'assessment')
            retrieval_quality: Retrieval quality metrics for uncertainty handling
            
        Returns:
            Generated response text
        """
        try:
            # Only return "I don't know" if absolutely no context (let LLM assess quality otherwise)
            if not context_chunks:
                return "I don't know."
            
            # Build context from chunks
            context_text = self._build_context_text(context_chunks)
            
            # Build conversation history (limit handled inside builder)
            history_text = self._build_conversation_history(conversation_history)
            
            # Create the prompt with retrieval quality information
            prompt = self.prompt_templates.create_tutor_prompt(
                query=query,
                context=context_text,
                conversation_history=history_text,
                mode=mode,
                retrieval_quality=retrieval_quality
            )
            
            # Prepare messages for LLM
            system_prompt = (
                self.prompt_templates.SYSTEM_ASSESSMENT if mode == "assessment" else self.prompt_templates.SYSTEM_EXPLORATION
            )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Use hybrid LLM service
            response = await self.llm_service.generate_response(
                messages=messages,
                query=query,
                max_tokens=(settings.assessment_max_gen_tokens if mode == 'assessment' else settings.exploration_max_gen_tokens),
                temperature=(settings.assessment_temperature if mode == 'assessment' else settings.exploration_temperature),
                mode=mode
            )
            
            logger.info(f"Generated response using {response.provider.value} provider")
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}")
            return self._generate_mock_response(query, context_chunks)

    async def _compress_query(self, query: str, conversation_history: List[Dict]) -> str:
        """Compress user query with minimal history using a lightweight LLM call."""
        try:
            history_text = self._build_conversation_history(conversation_history)
            compressor_messages = [
                {"role": "system", "content": self.prompt_templates.QUERY_COMPRESSOR},
                {"role": "user", "content": f"History (brief):\n{history_text}\n\nCurrent query:\n{query}"}
            ]
            # Favor local provider; service will choose
            resp = await self.llm_service.generate_response(
                messages=compressor_messages,
                query=query,
                max_tokens=120,
                temperature=0
            )
            compressed = (resp.content or "").strip()
            # Fallback to simple truncation if compression fails
            if not compressed:
                return query.strip()[:500]
            return compressed[:600]
        except Exception:
            return query.strip()[:500]

    async def process_query_with_metadata(
        self,
        query: str,
        user_id: str = None,
        conversation_history: List[Dict] = None,
        mode: str = "exploration"
    ) -> Dict[str, Any]:
        """Process a query and return response plus LLM routing metadata for benchmarking."""
        try:
            await self._ensure_llm_service_initialized()

            # Demo: hardcoded two-turn RAG Q&A
            demo_response = self._get_demo_response(
                query, conversation_history or self.get_conversation_history(user_id), user_id
            )
            if demo_response is not None:
                await asyncio.sleep(1.5)  # Brief delay so demo feels natural
                self._add_to_history(query, 'user', user_id)
                self._add_to_history(demo_response, 'assistant', user_id)
                first = demo_response.split('\n')[0].strip()
                tldr = (first[:157] + '...') if len(first) > 160 else first
                return {
                    'response': demo_response,
                    'query': query,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'context_chunks_used': 0,
                    'status': 'success',
                    'llm_provider': 'demo',
                    'llm_model': 'demo',
                    'llm_usage': {},
                    'llm_metadata': {},
                    'citations': [],
                    'tldr': tldr,
                }

            # Prompt injection guard
            injected, _ = detect_injection(query)
            if getattr(settings, 'reject_on_injection', False) and injected:
                logger.warning("Prompt injection pattern detected; rejecting request (metadata)")
                safe_msg = "I can only answer questions about the course materials. Please ask something about the content you're learning."
                self._add_to_history(query, 'user', user_id)
                self._add_to_history(safe_msg, 'assistant', user_id)
                return {
                    'response': safe_msg,
                    'query': query,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'context_chunks_used': 0,
                    'status': 'success',
                    'llm_provider': 'none',
                    'llm_model': 'none',
                    'llm_usage': {},
                    'llm_metadata': {},
                    'citations': [],
                    'tldr': safe_msg[:160],
                }

            self._add_to_history(query, 'user', user_id)

            context_chunks = await self._get_relevant_context(query)
            
            # Assess retrieval quality for uncertainty handling
            retrieval_quality = self._assess_retrieval_quality(context_chunks)
            logger.debug(f"Retrieval quality assessment (metadata): {retrieval_quality}")

            # Only return "I don't know" if absolutely no context (let LLM assess quality)
            if not context_chunks:
                return {
                    'response': "I don't know.",
                    'query': query,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'context_chunks_used': 0,
                    'status': 'success',
                    'llm_provider': 'none',
                    'llm_model': 'none',
                    'llm_usage': {},
                    'llm_metadata': {},
                    'citations': [],
                    'tldr': "I don't know."
                }

            context_text = self._build_context_text(context_chunks)
            history_text = self._build_conversation_history(conversation_history)

            prompt = self.prompt_templates.create_tutor_prompt(
                query=query,
                context=context_text,
                conversation_history=history_text,
                mode=mode,
                retrieval_quality=retrieval_quality
            )

            messages = [
                {"role": "system", "content": self.prompt_templates.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            response = await self.llm_service.generate_response(
                messages=messages,
                query=query,
                max_tokens=1000,
                temperature=0.7
            )

            self._add_to_history(response.content, 'assistant', user_id)

            # Build citations from retrieved context
            citations = []
            for chunk in context_chunks:
                meta = chunk.get('metadata', {}) if isinstance(chunk, dict) else {}
                title = meta.get('title') or meta.get('filename') or 'Source'
                url = meta.get('url') or meta.get('source_url')
                distance = chunk.get('distance') if isinstance(chunk, dict) else None
                score = None
                try:
                    if isinstance(distance, (int, float)):
                        score = round(1.0 / (1.0 + float(distance)), 4)
                except Exception:
                    score = None
                citations.append({
                    'title': title,
                    'url': url,
                    'score': score
                })

            # Simple TL;DR from the response
            tldr = None
            if response and response.content:
                first_sentence = response.content.split('\n')[0].strip()
                tldr = (first_sentence[:157] + '...') if len(first_sentence) > 160 else first_sentence

            return {
                'response': response.content.strip(),
                'query': query,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'context_chunks_used': len(context_chunks),
                'status': 'success',
                'llm_provider': response.provider.value,
                'llm_model': response.model,
                'llm_usage': response.usage,
                'llm_metadata': response.metadata,
                'citations': citations,
                'tldr': tldr
            }
        except Exception as e:
            logger.error(f"Error in process_query_with_metadata: {e}")
            return {
                'response': self._generate_mock_response(query, []),
                'query': query,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'context_chunks_used': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def _build_context_text(self, context_chunks: List[Dict]) -> str:
        """Build context text from retrieved chunks with character limit."""
        if not context_chunks:
            return "No relevant context found in the uploaded documents."
        
        context_parts = []
        total_chars = 0
        max_chars = settings.max_context_chars  # 4500 chars
        
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get('metadata', {}).get('filename', 'Unknown source')
            text = chunk.get('text', '')
            
            chunk_text = f"Context {i} (from {source}):\n{text}"
            chunk_len = len(chunk_text)
            
            # Check if adding this chunk would exceed limit
            if total_chars + chunk_len > max_chars:
                # Add partial chunk if we have space
                remaining = max_chars - total_chars
                if remaining > 100:  # Only add if meaningful space left
                    chunk_text = chunk_text[:remaining] + "..."
                    context_parts.append(chunk_text)
                break
            
            context_parts.append(chunk_text)
            total_chars += chunk_len + 2  # +2 for \n\n separator
        
        return "\n\n".join(context_parts)
    
    def _build_conversation_history(self, conversation_history: List[Dict]) -> str:
        """Build conversation history text limited to the last 8 exchanges."""
        if not conversation_history:
            return "No previous conversation."
        
        # Limit to last 8 messages for brevity
        recent = conversation_history[-8:]
        history_parts = []
        for entry in recent:
            role = entry.get('role', 'user')
            message = entry.get('message', '')
            history_parts.append(f"{role.title()}: {message}")
        
        return "\n".join(history_parts)
    
    def _generate_mock_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generate a mock response when OpenAI is not available."""
        normalized = self._normalize_text(query)
        predefined_answers = {
            "what is web development": (
                "Web development is the discipline of designing, building, and maintaining websites and "
                "web applications that run in a browser. It spans three main areas: (1) front-end "
                "development, which focuses on the user interface and experience using HTML for structure, "
                "CSS for presentation, and JavaScript for interactivity; (2) back-end development, which "
                "handles business logic, data storage, authentication, and APIs using servers, databases, "
                "and frameworks; and (3) DevOps/deployment, which covers hosting, CI/CD, monitoring, and "
                "scalability on platforms like Vercel, Netlify, or cloud providers.\n\n"
                "Modern web development emphasizes accessibility (inclusive design and semantic HTML), "
                "performance (fast loading and responsive rendering), security (input validation, auth, "
                "and HTTPS), and SEO (crawlability and metadata). Common stacks include React/Vue/Svelte "
                "on the front-end, Node/Python/Go/Java on the back-end, REST/GraphQL for APIs, and "
                "databases like Postgres, MySQL, or MongoDB. The goal is to deliver reliable, accessible, "
                "and maintainable experiences across devices and network conditions."
            ),
            "web development": (
                "Web development is the process of creating and maintaining websites and web apps. It "
                "includes front-end UI (HTML, CSS, JavaScript), back-end services (servers, databases, "
                "APIs), and deployment/operations, with strong focus on accessibility, performance, and "
                "security."
            ),
        }
        # Prefer exact intent match over substring matches
        if normalized in predefined_answers:
            return predefined_answers[normalized]

        if context_chunks:
            context_info = f"I found {len(context_chunks)} relevant sections in your course materials that address this topic."
        else:
            context_info = "I don't have specific information about this topic in your uploaded materials."

        return (
            f"Here's a concise answer about '{query}': "
            f"{context_info} Please provide or upload materials for a context-grounded explanation."
        )
    
    def _add_to_history(self, message: str, role: str, user_id: str = None):
        """Add message to conversation history."""
        history_entry = {
            'message': message,
            'role': role,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversation_history.append(history_entry)
        
        # Keep only last 20 messages to prevent memory issues
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_conversation_history(self, user_id: str = None) -> List[Dict]:
        """Get conversation history for a specific user."""
        if user_id:
            return [entry for entry in self.conversation_history if entry.get('user_id') == user_id]
        return self.conversation_history
    
    def clear_history(self, user_id: str = None):
        """Clear conversation history."""
        if user_id:
            self.conversation_history = [
                entry for entry in self.conversation_history 
                if entry.get('user_id') != user_id
            ]
        else:
            self.conversation_history = []
    
    async def process_query_streaming(
        self, 
        query: str, 
        user_id: str = None, 
        websocket = None,
        manager = None,
        mode: str = "exploration"
    ) -> None:
        """
        Process a user query and stream the response via WebSocket.
        
        Args:
            query: User's question or input
            user_id: Unique identifier for the user
            websocket: WebSocket connection for streaming
            manager: Connection manager for sending messages
            mode: Learning mode ('exploration' or 'assessment')
        """
        try:
            # Ensure LLM service is initialized
            await self._ensure_llm_service_initialized()
            
            # Store query in conversation history
            self._add_to_history(query, 'user', user_id)

            # Demo: hardcoded two-turn RAG Q&A (send full answer at once)
            user_history = self.get_conversation_history(user_id)
            demo_response = self._get_demo_response(query, user_history, user_id)
            if demo_response is not None:
                await asyncio.sleep(1.5)  # Brief delay so demo feels natural
                self._add_to_history(demo_response, 'assistant', user_id)
                chunk_msg = {
                    "type": "chunk",
                    "content": demo_response,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(chunk_msg), websocket)
                complete_msg = {
                    "type": "complete",
                    "message": "Response complete",
                    "timestamp": datetime.now().isoformat(),
                    "citations": [],
                    "tldr": (demo_response[:157] + '...') if len(demo_response) > 160 else demo_response
                }
                await manager.send_personal_message(json.dumps(complete_msg), websocket)
                return

            # Prompt injection guard (streaming)
            injected, _ = detect_injection(query)
            if getattr(settings, 'reject_on_injection', False) and injected:
                logger.warning("Prompt injection pattern detected; rejecting request (streaming)")
                safe_msg = "I can only answer questions about the course materials. Please ask something about the content you're learning."
                self._add_to_history(safe_msg, 'assistant', user_id)
                await manager.send_personal_message(
                    json.dumps({"type": "chunk", "content": safe_msg, "timestamp": datetime.now().isoformat()}),
                    websocket
                )
                await manager.send_personal_message(
                    json.dumps({
                        "type": "complete",
                        "message": "Response complete",
                        "timestamp": datetime.now().isoformat(),
                        "citations": [],
                        "tldr": safe_msg[:160],
                    }),
                    websocket
                )
                return
            
            # Send context retrieval message
            context_msg = {
                "type": "context",
                "message": "Retrieving relevant information...",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(context_msg), websocket)
            
            # Get relevant context from vector database
            context_chunks = await self._get_relevant_context(query)
            
            # Assess retrieval quality for uncertainty handling
            retrieval_quality = self._assess_retrieval_quality(context_chunks)
            logger.debug(f"Retrieval quality assessment (streaming): {retrieval_quality}")
            
            # Only return "I don't know" if absolutely no context
            if not context_chunks:
                idk_response = "I don't know."
                chunk_msg = {
                    "type": "chunk",
                    "content": idk_response,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(chunk_msg), websocket)
                
                complete_msg = {
                    "type": "complete",
                    "message": "Response complete",
                    "timestamp": datetime.now().isoformat(),
                    "citations": [],
                    "tldr": idk_response
                }
                await manager.send_personal_message(json.dumps(complete_msg), websocket)
                
                self._add_to_history(idk_response, 'assistant', user_id)
                return
            
            # Send context found message
            context_found_msg = {
                "type": "context_found",
                "message": f"Found {len(context_chunks)} relevant sections",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(context_found_msg), websocket)
            
            # Generate streaming response using LLM
            await self._generate_streaming_response(
                query, 
                context_chunks, 
                websocket,
                manager,
                mode,
                retrieval_quality
            )
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error processing your query: {str(e)}"
            logger.error(f"Error processing query: {e}")
            
            error_msg = {
                "type": "error",
                "message": error_response,
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(error_msg), websocket)
    
    async def _generate_streaming_response(
        self, 
        query: str, 
        context_chunks: List[Dict], 
        websocket = None,
        manager = None,
        mode: str = "exploration",
        retrieval_quality: Dict[str, Any] = None
    ) -> None:
        """
        Generate streaming response using hybrid LLM service.
        
        Args:
            query: User's question
            context_chunks: Relevant context from vector database
            websocket: WebSocket connection for streaming
            manager: Connection manager for sending messages
            mode: Learning mode ('exploration' or 'assessment')
            retrieval_quality: Retrieval quality metrics for uncertainty handling
        """
        try:
            # Build context from chunks
            context_text = self._build_context_text(context_chunks)
            
            # Build conversation history text for this user (if available via last user message in history)
            # Since user_id is not passed here, infer recent history by taking the last few turns regardless of id
            user_history = self.get_conversation_history(None)
            history_text = self._build_conversation_history(user_history)
            
            # Only return "I don't know" if absolutely no context
            if not context_chunks:
                idk_response = "I don't know."
                chunk_msg = {
                    "type": "chunk",
                    "content": idk_response,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(chunk_msg), websocket)
                
                complete_msg = {
                    "type": "complete",
                    "message": "Response complete",
                    "timestamp": datetime.now().isoformat(),
                    "citations": [],
                    "tldr": idk_response
                }
                await manager.send_personal_message(json.dumps(complete_msg), websocket)
                return
            
            # Create the prompt with retrieval quality information
            prompt = self.prompt_templates.create_tutor_prompt(
                query=query,
                context=context_text,
                conversation_history=history_text,
                mode=mode,
                retrieval_quality=retrieval_quality
            )
            
            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": self.prompt_templates.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            # Optional thinking delay before showing chunks
            start_msg = {
                "type": "generating",
                "message": "Generating response...",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(start_msg), websocket)
            import asyncio
            await asyncio.sleep(0.6)
            
            # Use hybrid LLM service for streaming
            full_response = ""
            
            # Log only prompt length to avoid leaking prompt content to logs
            logger.info("Sending prompt to LLM (length: %d)", len(prompt))
            
            async for chunk in self.llm_service.generate_streaming_response(
                messages=messages,
                query=query,
                max_tokens=1000,
                temperature=0.7
            ):
                # Only stream the actual LLM response chunks, not the prompt
                if chunk and chunk.strip():  # Ensure chunk is not empty
                    full_response += chunk
                    
                    # Send chunk to client
                    chunk_msg = {
                        "type": "chunk",
                        "content": chunk,
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.send_personal_message(json.dumps(chunk_msg), websocket)
            
            # Build citations from context and TL;DR
            citations = []
            for chunk in context_chunks:
                meta = chunk.get('metadata', {}) if isinstance(chunk, dict) else {}
                title = meta.get('title') or meta.get('filename') or 'Source'
                url = meta.get('url') or meta.get('source_url')
                distance = chunk.get('distance') if isinstance(chunk, dict) else None
                score = None
                try:
                    if isinstance(distance, (int, float)):
                        score = round(1.0 / (1.0 + float(distance)), 4)
                except Exception:
                    score = None
                citations.append({
                    'title': title,
                    'url': url,
                    'score': score
                })

            tldr = None
            if full_response:
                first_sentence = full_response.split('\n')[0].strip()
                tldr = (first_sentence[:157] + '...') if len(first_sentence) > 160 else first_sentence

            # Send completion message with metadata
            complete_msg = {
                "type": "complete",
                "message": "Response complete",
                "timestamp": datetime.now().isoformat(),
                "citations": citations,
                "tldr": tldr
            }
            await manager.send_personal_message(json.dumps(complete_msg), websocket)
            
            # Store response in conversation history
            self._add_to_history(full_response, 'assistant', None)
            
            logger.info("Streamed response complete (length: %d)", len(full_response))
            
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            await self._generate_mock_streaming_response(query, context_chunks, websocket, manager)
    
    async def _generate_mock_streaming_response(
        self, 
        query: str, 
        context_chunks: List[Dict], 
        websocket = None,
        manager = None
    ) -> None:
        """Generate a mock streaming response when OpenAI is not available."""
        try:
            normalized = self._normalize_text(query)
            predefined_answers = {
                "what is web development": (
                    "Web development is the practice of building and maintaining websites and web "
                    "applications. It spans front-end (HTML, CSS, JavaScript), back-end (servers, "
                    "databases, APIs), and deployment/operations, with focus on performance, security, "
                    "accessibility, and SEO."
                ),
                "web development": (
                    "Web development is the process of creating and maintaining websites and web apps, "
                    "covering front-end UI, back-end logic and data, and deployment."
                ),
            }
            full_response = None
            if normalized in predefined_answers:
                full_response = predefined_answers[normalized]

            if full_response is None:
                if context_chunks:
                    context_info = (
                        f"I found {len(context_chunks)} relevant sections in your course materials that address this topic."
                    )
                else:
                    context_info = (
                        "I don't have specific information about this topic in your uploaded materials."
                    )
                full_response = (
                    f"Here's a concise answer about '{query}': {context_info} "
                    f"Please upload materials for a context-grounded explanation."
                )

            # Add a small thinking delay before streaming
            import asyncio
            await asyncio.sleep(0.6)
            
            # Send generation start message
            start_msg = {
                "type": "generating",
                "message": "Generating response...",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(start_msg), websocket)
            
            # Simulate streaming by sending chunks
            words = full_response.split()
            chunk_size = 3  # Send 3 words at a time
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_content = " ".join(chunk_words) + " "
                
                chunk_msg = {
                    "type": "chunk",
                    "content": chunk_content,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(chunk_msg), websocket)
                
                # Small delay to simulate streaming
                import asyncio
                await asyncio.sleep(0.1)
            
            # Send completion message
            complete_msg = {
                "type": "complete",
                "message": "Response complete",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(complete_msg), websocket)
            
            # Store response in conversation history
            self._add_to_history(full_response, 'assistant', None)
            
        except Exception as e:
            logger.error(f"Failed to generate mock streaming response: {e}")
            error_msg = {
                "type": "error",
                "message": "Sorry, I'm having trouble generating a response right now.",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(error_msg), websocket)

    async def get_learning_suggestions(self, user_id: str = None) -> List[str]:
        """
        Generate learning suggestions based on conversation history.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of learning suggestions
        """
        try:
            user_history = self.get_conversation_history(user_id)
            if not user_history:
                return [
                    "Upload some course materials to get personalized learning suggestions!",
                    "Ask me questions about any topic you're studying.",
                    "Try asking 'Can you explain [topic]?' for detailed explanations."
                ]
            
            # Analyze conversation patterns
            topics_mentioned = set()
            for entry in user_history:
                if entry['role'] == 'user':
                    # Simple topic extraction (in real implementation, use NLP)
                    words = entry['message'].lower().split()
                    topics_mentioned.update(words)
            
            suggestions = [
                "Based on our conversation, you might want to explore related topics.",
                "Consider reviewing the materials we discussed earlier.",
                "Try asking more specific questions about the topics you're interested in."
            ]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate learning suggestions: {e}")
            return ["Keep asking questions to improve your learning!"]
