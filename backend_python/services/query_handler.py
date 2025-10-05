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
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a user query and return a response.
        
        Args:
            query: User's question or input
            user_id: Unique identifier for the user
            conversation_history: Previous conversation context
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Ensure LLM service is initialized
            await self._ensure_llm_service_initialized()
            
            # Store query in conversation history
            self._add_to_history(query, 'user', user_id)
            
            # Get relevant context from vector database
            context_chunks = await self._get_relevant_context(query)
            
            # Generate response using LLM
            response = await self._generate_llm_response(
                query, 
                context_chunks, 
                conversation_history
            )
            
            # Store response in conversation history
            self._add_to_history(response, 'assistant', user_id)
            
            return {
                'response': response,
                'query': query,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'context_chunks_used': len(context_chunks),
                'status': 'success'
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
    
    async def _generate_llm_response(
        self, 
        query: str, 
        context_chunks: List[Dict], 
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate response using hybrid LLM service.
        
        Args:
            query: User's question
            context_chunks: Relevant context from vector database
            conversation_history: Previous conversation context
            
        Returns:
            Generated response text
        """
        try:
            # Build context from chunks
            context_text = self._build_context_text(context_chunks)
            
            # Build conversation history
            history_text = self._build_conversation_history(conversation_history)
            
            # Create the prompt
            prompt = self.prompt_templates.create_tutor_prompt(
                query=query,
                context=context_text,
                conversation_history=history_text
            )
            
            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": self.prompt_templates.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            # Use hybrid LLM service
            response = await self.llm_service.generate_response(
                messages=messages,
                query=query,
                max_tokens=1000,
                temperature=0.7
            )
            
            logger.info(f"Generated response using {response.provider.value} provider")
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}")
            return self._generate_mock_response(query, context_chunks)
    
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
        """Build conversation history text."""
        if not conversation_history:
            return "No previous conversation."
        
        history_parts = []
        for entry in conversation_history[-5:]:  # Last 5 exchanges
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
        manager = None
    ) -> None:
        """
        Process a user query and stream the response via WebSocket.
        
        Args:
            query: User's question or input
            user_id: Unique identifier for the user
            websocket: WebSocket connection for streaming
            manager: Connection manager for sending messages
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
                manager
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
        manager = None
    ) -> None:
        """
        Generate streaming response using hybrid LLM service.
        
        Args:
            query: User's question
            context_chunks: Relevant context from vector database
            websocket: WebSocket connection for streaming
            manager: Connection manager for sending messages
        """
        try:
            # Build context from chunks
            context_text = self._build_context_text(context_chunks)
            
            # Create the prompt
            prompt = self.prompt_templates.create_tutor_prompt(
                query=query,
                context=context_text,
                conversation_history=""
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
            
            async for chunk in self.llm_service.generate_streaming_response(
                messages=messages,
                query=query,
                max_tokens=1000,
                temperature=0.7
            ):
                full_response += chunk
                
                # Send chunk to client
                chunk_msg = {
                    "type": "chunk",
                    "content": chunk,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(chunk_msg), websocket)
            
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
