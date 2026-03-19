"""
Text chunking service for splitting documents into manageable pieces.
"""

from typing import List, Dict
from loguru import logger


class TextChunker:
    """
    Chunk text into smaller pieces for vector storage.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        # Split into sentences (simple approach)
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk size, save current chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "chunk_index": chunk_index,
                    "char_count": len(current_chunk),
                    "metadata": metadata or {}
                })
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + " " + sentence
                current_length = len(current_chunk)
                chunk_index += 1
            else:
                # Add sentence to current chunk
                current_chunk += " " + sentence
                current_length += sentence_length + 1  # +1 for space
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": chunk_index,
                "char_count": len(current_chunk),
                "metadata": metadata or {}
            })
        
        logger.info(f"Created {len(chunks)} chunks from {len(text)} characters")
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences (simple implementation).
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with NLP)
        import re
        
        # Split on common sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap(self, text: str) -> str:
        """
        Get overlap text from end of chunk.
        
        Args:
            text: Text to get overlap from
            
        Returns:
            Overlap text
        """
        if len(text) <= self.chunk_overlap:
            return text
        
        # Get last chunk_overlap characters, but try to start at word boundary
        overlap_text = text[-self.chunk_overlap:]
        
        # Find first space to start at word boundary
        space_idx = overlap_text.find(' ')
        if space_idx > 0:
            overlap_text = overlap_text[space_idx:].strip()
        
        return overlap_text
    
    def chunk_by_pages(self, pages: List[Dict], metadata: Dict = None) -> List[Dict]:
        """
        Chunk text by pages, keeping page information.
        
        Args:
            pages: List of page dictionaries with 'page_number' and 'text'
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with page information
        """
        all_chunks = []
        
        for page in pages:
            page_text = page.get('text', '')
            page_number = page.get('page_number', 0)
            
            if not page_text.strip():
                continue
            
            # Add page number to metadata
            page_metadata = {**(metadata or {}), "page_number": page_number}
            
            # Chunk the page
            page_chunks = self.chunk_text(page_text, page_metadata)
            all_chunks.extend(page_chunks)
        
        return all_chunks


# Factory function
def create_text_chunker(chunk_size: int = 1000, chunk_overlap: int = 200) -> TextChunker:
    """Create a text chunker with specified parameters."""
    return TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
