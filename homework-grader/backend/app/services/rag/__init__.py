"""
RAG (Retrieval-Augmented Generation) service for context retrieval.
"""

from typing import List, Dict
from loguru import logger

from app.services.vector_store import vector_store_service


class RAGService:
    """
    RAG service for retrieving relevant context from course materials.
    """
    
    def __init__(self):
        self.vector_store = vector_store_service
    
    def retrieve_context(
        self,
        query_text: str,
        collection_name: str,
        n_results: int = 5
    ) -> List[str]:
        """
        Retrieve relevant context chunks for grading.
        
        Args:
            query_text: Student submission or query
            collection_name: Section's vector store collection
            n_results: Number of chunks to retrieve
            
        Returns:
            List of relevant text chunks
        """
        try:
            logger.info(f"Retrieving context from {collection_name} (n={n_results})")
            
            # Query vector store
            results = self.vector_store.query_documents(
                collection_name=collection_name,
                query_text=query_text,
                n_results=n_results
            )
            
            # Extract documents
            documents = results.get('documents', [[]])[0]
            
            if not documents:
                logger.warning(f"No context retrieved from {collection_name}")
                return []
            
            logger.info(f"Retrieved {len(documents)} context chunks")
            return documents
        
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            # Return empty context rather than failing
            return []
    
    def build_grading_context(
        self,
        submission_text: str,
        collection_name: str,
        n_chunks: int = 5
    ) -> Dict:
        """
        Build comprehensive grading context.
        
        Args:
            submission_text: Student submission
            collection_name: Section's vector store collection
            n_chunks: Number of chunks to retrieve
            
        Returns:
            Dictionary with context and metadata
        """
        try:
            # Retrieve relevant chunks
            context_chunks = self.retrieve_context(
                query_text=submission_text,
                collection_name=collection_name,
                n_results=n_chunks
            )
            
            return {
                "chunks": context_chunks,
                "num_chunks": len(context_chunks),
                "collection": collection_name,
                "has_context": len(context_chunks) > 0
            }
        
        except Exception as e:
            logger.error(f"Error building grading context: {e}")
            return {
                "chunks": [],
                "num_chunks": 0,
                "collection": collection_name,
                "has_context": False,
                "error": str(e)
            }


# Singleton instance
rag_service = RAGService()
