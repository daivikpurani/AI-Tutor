"""
Enhanced Query Handler with Hybrid LLM Integration
Processes user queries using multiple LLM providers with intelligent routing.
"""

import os
import json
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import logging

from services.vector_db import VectorDatabase
from services.llm_service import HybridLLMService, LLMResponse
from utils.prompts import PromptTemplates
from utils.config import settings

logger = logging.getLogger(__name__)

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
    
    async def _get_relevant_context(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Retrieve relevant context chunks from vector database.
        
        Args:
            query: User query to find context for
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            List of relevant context chunks
        """
        try:
            context_chunks = await self.vector_db.search_similar(query, n_results)
            
            # Filter out low-relevance chunks (distance > 2.0 for ChromaDB)
            filtered_chunks = [
                chunk for chunk in context_chunks 
                if chunk.get('distance', 1.0) < 2.0
            ]
            
            logger.info(f"Retrieved {len(filtered_chunks)} relevant context chunks")
            return filtered_chunks
            
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
        
        # Determine quality thresholds
        # Good retrieval: avg_similarity > 0.7 or avg_distance < 1.5
        # Poor retrieval: avg_similarity < 0.6 or avg_distance > 1.8
        has_good_retrieval = (
            avg_similarity > 0.65 and avg_distance < 1.6
        ) if len(context_chunks) > 0 else False
        
        # Determine quality level
        if len(context_chunks) == 0:
            quality_level = 'none'
        elif has_good_retrieval:
            quality_level = 'good'
        elif avg_similarity > 0.5 and avg_distance < 1.8:
            quality_level = 'moderate'
        else:
            quality_level = 'poor'
        
        return {
            'chunk_count': len(context_chunks),
            'avg_similarity': avg_similarity,
            'avg_distance': avg_distance,
            'has_good_retrieval': has_good_retrieval,
            'quality_level': quality_level,
            'min_distance': min(distances) if distances else float('inf'),
            'max_distance': max(distances) if distances else float('inf')
        }
    
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

            self._add_to_history(query, 'user', user_id)

            context_chunks = await self._get_relevant_context(query)
            
            # Assess retrieval quality for uncertainty handling
            retrieval_quality = self._assess_retrieval_quality(context_chunks)
            logger.debug(f"Retrieval quality assessment (metadata): {retrieval_quality}")

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
        """Build context text from retrieved chunks."""
        if not context_chunks:
            return "No relevant context found in the uploaded documents."
        
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get('metadata', {}).get('filename', 'Unknown source')
            text = chunk.get('text', '')
            context_parts.append(f"Context {i} (from {source}):\n{text}")
        
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
            
            # Debug: Log the prompt being sent to LLM (but don't stream it)
            logger.info(f"Sending prompt to LLM (length: {len(prompt)})")
            logger.debug(f"Prompt content: {prompt[:200]}...")
            
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
            
            # Debug: Log the final response
            logger.info(f"Streamed response complete (length: {len(full_response)})")
            logger.debug(f"Final response: {full_response[:200]}...")
            
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
