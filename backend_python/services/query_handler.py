"""
Enhanced Query Handler with LLM Integration
Processes user queries using OpenAI API and ChromaDB vector search.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
from openai import AsyncOpenAI
import logging

from services.vector_db import VectorDatabase
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
        self.openai_client = None
        self.conversation_history = []
        self.prompt_templates = PromptTemplates()
        
        # Initialize OpenAI client
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client."""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY not found. Using mock responses.")
                return
            
            self.openai_client = AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
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
            
            # Filter out low-relevance chunks (distance > 0.8)
            filtered_chunks = [
                chunk for chunk in context_chunks 
                if chunk.get('distance', 1.0) < 0.8
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
        Generate response using OpenAI API.
        
        Args:
            query: User's question
            context_chunks: Relevant context from vector database
            conversation_history: Previous conversation context
            
        Returns:
            Generated response text
        """
        try:
            # If no OpenAI client, use mock response
            if not self.openai_client:
                return self._generate_mock_response(query, context_chunks)
            
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
            
            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.prompt_templates.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
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
        if context_chunks:
            context_info = f"I found {len(context_chunks)} relevant sections in your course materials that address this topic."
        else:
            context_info = "I don't have specific information about this topic in your uploaded materials."
        
        mock_responses = [
            f"Great question about '{query}'! {context_info} Let me explain this concept based on what I know.",
            f"Excellent question! '{query}' is an important topic. {context_info} Here's what I can tell you about it.",
            f"I'd be happy to help with '{query}'. {context_info} This is a fundamental concept worth understanding.",
            f"Interesting question about '{query}'! {context_info} Let me break this down for you."
        ]
        
        # Simple mock response selection based on query length
        response_index = len(query) % len(mock_responses)
        base_response = mock_responses[response_index]
        
        # Add some educational content
        educational_additions = [
            "\n\nThis concept is important because it forms the foundation for more advanced topics.",
            "\n\nUnderstanding this will help you with related concepts in your studies.",
            "\n\nThis topic often appears in exams and practical applications.",
            "\n\nMastering this concept will make future learning much easier."
        ]
        
        addition_index = len(query) % len(educational_additions)
        return base_response + educational_additions[addition_index]
    
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
        Generate streaming response using OpenAI API.
        
        Args:
            query: User's question
            context_chunks: Relevant context from vector database
            websocket: WebSocket connection for streaming
            manager: Connection manager for sending messages
        """
        try:
            # If no OpenAI client, use mock streaming response
            if not self.openai_client:
                await self._generate_mock_streaming_response(query, context_chunks, websocket, manager)
                return
            
            # Build context from chunks
            context_text = self._build_context_text(context_chunks)
            
            # Create the prompt
            prompt = self.prompt_templates.create_tutor_prompt(
                query=query,
                context=context_text,
                conversation_history=""
            )
            
            # Send generation start message
            start_msg = {
                "type": "generating",
                "message": "Generating response...",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(start_msg), websocket)
            
            # Call OpenAI API with streaming
            stream = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.prompt_templates.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                stream=True
            )
            
            full_response = ""
            
            # Stream the response
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # Send chunk to client
                    chunk_msg = {
                        "type": "chunk",
                        "content": content,
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
            if context_chunks:
                context_info = f"I found {len(context_chunks)} relevant sections in your course materials that address this topic."
            else:
                context_info = "I don't have specific information about this topic in your uploaded materials."
            
            mock_responses = [
                f"Great question about '{query}'! {context_info} Let me explain this concept based on what I know.",
                f"Excellent question! '{query}' is an important topic. {context_info} Here's what I can tell you about it.",
                f"I'd be happy to help with '{query}'. {context_info} This is a fundamental concept worth understanding.",
                f"Interesting question about '{query}'! {context_info} Let me break this down for you."
            ]
            
            # Simple mock response selection based on query length
            response_index = len(query) % len(mock_responses)
            base_response = mock_responses[response_index]
            
            # Add some educational content
            educational_additions = [
                "\n\nThis concept is important because it forms the foundation for more advanced topics.",
                "\n\nUnderstanding this will help you with related concepts in your studies.",
                "\n\nThis topic often appears in exams and practical applications.",
                "\n\nMastering this concept will make future learning much easier."
            ]
            
            addition_index = len(query) % len(educational_additions)
            full_response = base_response + educational_additions[addition_index]
            
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
