"""
ChromaDB Vector Database Service
Handles document storage, retrieval, and similarity search using ChromaDB.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorDatabase:
    """
    ChromaDB-based vector database for storing and retrieving document chunks.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector database.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_model = None
        
        # Initialize ChromaDB client and collection
        self._initialize_client()
        self._initialize_embedding_model()
        self._initialize_collection()
    
    def _initialize_client(self):
        """Initialize ChromaDB client."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model for embeddings."""
        try:
            # Use a lightweight, fast model for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def _initialize_collection(self):
        """Initialize or get the document collection."""
        try:
            # Try to get existing "test" collection first, then create if needed
            try:
                self.collection = self.client.get_collection(name="test")
                logger.info("Connected to existing 'test' collection")
            except:
                self.collection = self.client.get_or_create_collection(
                    name="test",
                    metadata={"description": "AI Tutor test documents"}
                )
                logger.info("Created new 'test' collection")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise
    
    async def add_documents(self, chunks: List[Dict[str, Any]], filename: str) -> bool:
        """
        Add document chunks to the vector database.
        
        Args:
            chunks: List of document chunks with text and metadata
            filename: Name of the source file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                # Generate unique ID for each chunk
                chunk_id = str(uuid.uuid4())
                
                # Extract text content
                text = chunk.get('text', '')
                if not text.strip():
                    continue
                
                documents.append(text)
                metadatas.append({
                    'filename': filename,
                    'chunk_id': chunk.get('chunk_id', 0),
                    'chunk_size': len(text),
                    'start_pos': chunk.get('start_pos', 0),
                    'end_pos': chunk.get('end_pos', 0),
                    'file_type': chunk.get('metadata', {}).get('file_type', 'unknown'),
                    'source': chunk.get('metadata', {}).get('source', 'upload')
                })
                ids.append(chunk_id)
            
            if not documents:
                logger.warning(f"No valid documents to add for {filename}")
                return False
            
            # Add to ChromaDB collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(documents)} chunks from {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    async def search_similar(self, query: str, n_results: int = 5, filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic similarity.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar document chunks with metadata
        """
        try:
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            similar_chunks = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    chunk_data = {
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i] if results['ids'] else None
                    }
                    similar_chunks.append(chunk_data)
            
            logger.info(f"Found {len(similar_chunks)} similar chunks for query: {query[:50]}...")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    async def get_document_chunks(self, filename: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.
        
        Args:
            filename: Name of the document
            
        Returns:
            List of chunks for the document
        """
        try:
            results = self.collection.get(
                where={"filename": filename}
            )
            
            chunks = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    chunk_data = {
                        'text': doc,
                        'metadata': results['metadatas'][i] if results['metadatas'] else {},
                        'id': results['ids'][i] if results['ids'] else None
                    }
                    chunks.append(chunk_data)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to get document chunks: {e}")
            return []
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all unique documents in the database.
        
        Returns:
            List of document metadata
        """
        try:
            # Get all documents
            results = self.collection.get()
            
            # Extract unique filenames
            documents = {}
            if results['metadatas']:
                for metadata in results['metadatas']:
                    filename = metadata.get('filename', 'unknown')
                    if filename not in documents:
                        documents[filename] = {
                            'filename': filename,
                            'file_type': metadata.get('file_type', 'unknown'),
                            'chunk_count': 1,
                            'total_size': metadata.get('chunk_size', 0)
                        }
                    else:
                        documents[filename]['chunk_count'] += 1
                        documents[filename]['total_size'] += metadata.get('chunk_size', 0)
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    async def delete_document(self, filename: str) -> bool:
        """
        Delete all chunks for a specific document.
        
        Args:
            filename: Name of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all IDs for the document
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if results['ids']:
                # Delete all chunks for this document
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document: {filename}")
                return True
            else:
                logger.warning(f"No chunks found for document: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def health_check(self) -> str:
        """
        Check the health of the vector database.
        
        Returns:
            Health status string
        """
        try:
            # Try to get collection info
            count = self.collection.count()
            return f"healthy (documents: {count})"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return f"unhealthy: {str(e)}"
    
    async def reset_database(self) -> bool:
        """
        Reset the entire database (delete all data).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection("ai_tutor_documents")
            self._initialize_collection()
            logger.info("Database reset successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
