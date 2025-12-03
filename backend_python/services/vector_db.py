"""
ChromaDB Vector Database Service
Handles document storage, retrieval, and similarity search using ChromaDB.
"""

import os
import uuid
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorDatabase:
    """
    ChromaDB-based vector database for storing and retrieving document chunks.
    """
    
    def __init__(self, persist_directory: str = None, collection_name: str = None):
        """
        Initialize the vector database.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection to use
        """
        # Import settings here to avoid circular imports
        try:
            from utils.config import settings
            self.persist_directory = persist_directory or settings.chroma_persist_directory
            self.collection_name = collection_name or settings.vector_db_collection_name
        except ImportError:
            # Fallback if settings not available
            self.persist_directory = persist_directory or "./chroma_db"
            self.collection_name = collection_name or "ai_tutor_documents"
        
        self.client = None
        self.collection = None
        self.embedding_model = None
        
        # Initialize ChromaDB client and collection
        self._initialize_client()
        self._initialize_embedding_model()
        self._initialize_collection()
    
    def _initialize_client(self):
        """Initialize ChromaDB client with enhanced settings."""
        try:
            # Ensure directory exists
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # ChromaDB 0.3.23 uses Client() with Settings, not PersistentClient
            settings = Settings(
                persist_directory=self.persist_directory,
                chroma_db_impl="duckdb",
                chroma_api_impl="local"
            )
            self.client = chromadb.Client(settings=settings)
            logger.info(f"ChromaDB client initialized with persistence at: {self.persist_directory}")
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
    
    def _get_embedding_function(self):
        """Create an embedding function for ChromaDB."""
        def embed_function(texts):
            """Embed texts using the SentenceTransformer model."""
            if not texts:
                return []
            # Handle both single strings and lists
            if isinstance(texts, str):
                texts = [texts]
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
        
        return embed_function
    
    def _initialize_collection(self):
        """Initialize or get the document collection."""
        try:
            # Create embedding function for ChromaDB
            embedding_function = self._get_embedding_function()
            
            # Use configured collection name
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
                logger.info(f"Connected to existing '{self.collection_name}' collection")
            except:
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function,
                    metadata={"description": "AI Tutor documents", "created_at": datetime.now().isoformat()}
                )
                logger.info(f"Created new '{self.collection_name}' collection")
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
                    'source': chunk.get('metadata', {}).get('source', 'upload'),
                    'upload_date': datetime.now().isoformat()
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
    
    async def add_document_direct(self, text: str, filename: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a single document directly to the collection without chunking.
        
        Args:
            text: Document text content
            filename: Name of the document
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            
            # Prepare metadata
            doc_metadata = {
                'filename': filename,
                'file_type': metadata.get('file_type', 'text') if metadata else 'text',
                'source': metadata.get('source', 'direct_upload') if metadata else 'direct_upload',
                'upload_date': datetime.now().isoformat(),
                'content_length': len(text),
                'is_chunked': False
            }
            
            # Add metadata from input
            if metadata:
                doc_metadata.update(metadata)
            
            # Add to collection
            self.collection.add(
                documents=[text],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Successfully added document '{filename}' directly to collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document directly: {e}")
            return False
    
    async def search_similar(self, query: str, n_results: int = 5, filter_metadata: Dict = None,
                             use_mmr: bool = True, mmr_lambda: float = 0.5) -> List[Dict[str, Any]]:
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
                    # Add a short preview to reduce context size upstream
                    preview = (doc or "").strip()
                    chunk_data['preview'] = (preview[:300] + ("..." if len(preview) > 300 else ""))
                    similar_chunks.append(chunk_data)
            
            # Apply simple MMR for diversity if requested and we have more than 2 candidates
            if use_mmr and len(similar_chunks) > 2:
                try:
                    selected = self._mmr_select(query, similar_chunks, top_k=min(len(similar_chunks), n_results), lambda_mult=mmr_lambda)
                    similar_chunks = selected
                except Exception as e:
                    logger.debug(f"MMR selection failed, using original order: {e}")

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
                            'id': metadata.get('document_id', filename),
                            'filename': filename,
                            'file_type': metadata.get('file_type', 'unknown'),
                            'chunk_count': 1,
                            'total_size': metadata.get('chunk_size', metadata.get('content_length', 0)),
                            'upload_date': metadata.get('upload_date', 'unknown'),
                            'description': metadata.get('description', ''),
                            'is_chunked': metadata.get('is_chunked', True)
                        }
                    else:
                        documents[filename]['chunk_count'] += 1
                        documents[filename]['total_size'] += metadata.get('chunk_size', metadata.get('content_length', 0))
            
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
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        try:
            count = self.collection.count()
            
            # Get collection metadata
            collection_info = self.collection.get()
            
            stats = {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory,
                "disk_usage": self._get_directory_size(self.persist_directory),
                "last_updated": datetime.now().isoformat(),
                "collection_metadata": collection_info.get('metadatas', [])[:5] if collection_info else []
            }
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}
    
    def _get_directory_size(self, path: str) -> str:
        """Get directory size in human-readable format."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Failed to calculate directory size: {e}")
            return "Unknown"
        
        # Convert to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.1f} TB"

    def _mmr_select(self, query: str, candidates: List[Dict[str, Any]], top_k: int, lambda_mult: float = 0.5) -> List[Dict[str, Any]]:
        """Maximal Marginal Relevance selection using embedding_model."""
        # Compute embeddings
        query_emb = self.embedding_model.encode([query], convert_to_tensor=False)[0]
        doc_embs = self.embedding_model.encode([c.get('text', '') for c in candidates], convert_to_tensor=False)
        import numpy as np

        def cosine_sim(a, b):
            a = np.array(a)
            b = np.array(b)
            denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
            return float(np.dot(a, b) / denom)

        selected_indices = []
        candidate_indices = list(range(len(candidates)))

        # Precompute relevance to query
        relevance = [cosine_sim(query_emb, emb) for emb in doc_embs]

        while len(selected_indices) < top_k and candidate_indices:
            mmr_scores = []
            for idx in candidate_indices:
                if not selected_indices:
                    diversity_penalty = 0.0
                else:
                    diversity_penalty = max(
                        cosine_sim(doc_embs[idx], doc_embs[j]) for j in selected_indices
                    )
                score = lambda_mult * relevance[idx] - (1 - lambda_mult) * diversity_penalty
                mmr_scores.append((score, idx))
            mmr_scores.sort(reverse=True)
            best_idx = mmr_scores[0][1]
            selected_indices.append(best_idx)
            candidate_indices.remove(best_idx)

        return [candidates[i] for i in selected_indices]
    
    async def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the ChromaDB database."""
        try:
            shutil.copytree(self.persist_directory, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    async def restore_database(self, backup_path: str) -> bool:
        """Restore ChromaDB database from backup."""
        try:
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
            shutil.copytree(backup_path, self.persist_directory)
            logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    async def reset_database(self) -> bool:
        """
        Reset the entire database (delete all data).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(self.collection_name)
            self._initialize_collection()
            logger.info("Database reset successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
