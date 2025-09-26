"""
Ai-Tutor Query Handler
Processes user queries and returns LLM responses with context from vector database.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class QueryHandler:
    """
    Handles user queries by processing them through LLM APIs and vector database.
    """
    
    def __init__(self, llm_api_key: str = None, vector_db_key: str = None):
        """
        Initialize the query handler.
        
        Args:
            llm_api_key: API key for LLM service (OpenAI, ChaiJibri, etc.)
            vector_db_key: API key for vector database (Pinecone, etc.)
        """
        self.llm_api_key = llm_api_key or os.getenv('OPENAI_API_KEY')
        self.vector_db_key = vector_db_key or os.getenv('PINECONE_API_KEY')
        self.conversation_history = []
    
    def process_query(self, query: str, user_id: str = None, context_chunks: List[Dict] = None) -> Dict[str, Any]:
        """
        Process a user query and return a response.
        
        Args:
            query: User's question or input
            user_id: Unique identifier for the user
            context_chunks: Relevant context chunks from vector database
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Store query in conversation history
            self._add_to_history(query, 'user', user_id)
            
            # Get relevant context from vector database (placeholder)
            if context_chunks is None:
                context_chunks = self._get_relevant_context(query)
            
            # Generate response using LLM (placeholder)
            response = self._generate_llm_response(query, context_chunks)
            
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
            return {
                'response': error_response,
                'query': query,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
    
    def _get_relevant_context(self, query: str) -> List[Dict]:
        """
        Retrieve relevant context chunks from vector database.
        
        Args:
            query: User query to find context for
            
        Returns:
            List of relevant context chunks
        """
        # Placeholder: In real implementation, this would:
        # 1. Generate embeddings for the query
        # 2. Search vector database for similar chunks
        # 3. Return top-k most relevant chunks
        
        mock_context = [
            {
                'text': 'This is a sample context chunk that would be retrieved from the vector database based on semantic similarity to your query.',
                'metadata': {
                    'source': 'sample_document.pdf',
                    'chunk_id': 1,
                    'relevance_score': 0.95
                }
            },
            {
                'text': 'Another relevant context chunk that provides additional information related to your question.',
                'metadata': {
                    'source': 'course_materials.docx',
                    'chunk_id': 3,
                    'relevance_score': 0.87
                }
            }
        ]
        
        return mock_context
    
    def _generate_llm_response(self, query: str, context_chunks: List[Dict]) -> str:
        """
        Generate response using LLM API.
        
        Args:
            query: User's question
            context_chunks: Relevant context from vector database
            
        Returns:
            Generated response text
        """
        # Placeholder: In real implementation, this would:
        # 1. Format context chunks into prompt
        # 2. Send request to LLM API (OpenAI, ChaiJibri, etc.)
        # 3. Parse and return response
        
        context_text = "\n".join([chunk['text'] for chunk in context_chunks])
        
        # Mock response generation
        mock_responses = [
            f"Based on the course material, here's what I found regarding your question: '{query}'. The relevant information suggests that this is an important concept to understand.",
            f"Great question! Looking at the uploaded materials, I can explain that '{query}' relates to several key concepts covered in the course.",
            f"I'd be happy to help with '{query}'. From the course content, I can see this topic is covered in detail with practical examples.",
            f"Excellent question about '{query}'! The materials show this is a fundamental concept with several applications we've discussed."
        ]
        
        # Simple mock response selection based on query length
        response_index = len(query) % len(mock_responses)
        base_response = mock_responses[response_index]
        
        # Add context-aware information if available
        if context_chunks:
            base_response += f"\n\nI found {len(context_chunks)} relevant sections in your course materials that address this topic."
        
        return base_response
    
    def _add_to_history(self, message: str, role: str, user_id: str = None):
        """
        Add message to conversation history.
        
        Args:
            message: The message content
            role: 'user' or 'assistant'
            user_id: User identifier
        """
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
        """
        Get conversation history for a specific user.
        
        Args:
            user_id: User identifier (if None, returns all history)
            
        Returns:
            List of conversation entries
        """
        if user_id:
            return [entry for entry in self.conversation_history if entry.get('user_id') == user_id]
        return self.conversation_history
    
    def clear_history(self, user_id: str = None):
        """
        Clear conversation history.
        
        Args:
            user_id: User identifier (if None, clears all history)
        """
        if user_id:
            self.conversation_history = [
                entry for entry in self.conversation_history 
                if entry.get('user_id') != user_id
            ]
        else:
            self.conversation_history = []


def main():
    """
    Example usage of the QueryHandler.
    """
    handler = QueryHandler()
    
    # Example queries
    test_queries = [
        "What is machine learning?",
        "How does neural network training work?",
        "Can you explain the concept of overfitting?",
        "What are the main types of supervised learning?"
    ]
    
    print("Ai-Tutor Query Handler Demo")
    print("=" * 40)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = handler.process_query(query, user_id="demo_user")
        print(f"Response: {result['response']}")
        print(f"Status: {result['status']}")
        print(f"Context chunks used: {result['context_chunks_used']}")
        print("-" * 40)


if __name__ == "__main__":
    main()
