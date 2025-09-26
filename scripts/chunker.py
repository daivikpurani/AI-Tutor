"""
Ai-Tutor Document Chunker
Handles splitting uploaded files into chunks for vector database storage.
"""

import os
import re
from typing import List, Dict, Any
from pathlib import Path


class DocumentChunker:
    """
    Handles document chunking for vector database storage.
    Supports various file formats and intelligent text splitting.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_formats = ['.txt', '.md', '.pdf', '.docx', '.doc']
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(start, end - 200)
                sentence_end = text.rfind('.', search_start, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_data = {
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'chunk_id': len(chunks),
                    'metadata': {
                        'chunk_size': len(chunk_text),
                        'source': 'text_input'
                    }
                }
                chunks.append(chunk_data)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def chunk_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Chunk a file based on its format.
        
        Args:
            file_path: Path to the file to chunk
            
        Returns:
            List of chunk dictionaries
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Extract text based on file type
        text = self._extract_text_from_file(file_path)
        
        # Chunk the extracted text
        chunks = self.chunk_text(text)
        
        # Add file metadata to each chunk
        for chunk in chunks:
            chunk['metadata'].update({
                'filename': file_path.name,
                'file_path': str(file_path),
                'file_type': file_path.suffix.lower()
            })
        
        return chunks
    
    def _extract_text_from_file(self, file_path: Path) -> str:
        """
        Extract text from various file formats.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        suffix = file_path.suffix.lower()
        
        if suffix == '.txt' or suffix == '.md':
            return self._extract_text_file(file_path)
        elif suffix == '.pdf':
            return self._extract_pdf_file(file_path)
        elif suffix in ['.docx', '.doc']:
            return self._extract_word_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _extract_text_file(self, file_path: Path) -> str:
        """Extract text from plain text or markdown files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _extract_pdf_file(self, file_path: Path) -> str:
        """Extract text from PDF files - placeholder implementation."""
        # Placeholder: In real implementation, use PyPDF2 or pdfplumber
        return f"[PDF content placeholder for {file_path.name}]"
    
    def _extract_word_file(self, file_path: Path) -> str:
        """Extract text from Word documents - placeholder implementation."""
        # Placeholder: In real implementation, use python-docx
        return f"[Word document content placeholder for {file_path.name}]"


def main():
    """
    Example usage of the DocumentChunker.
    """
    chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
    
    # Example: Chunk sample text
    sample_text = """
    This is a sample document for testing the chunker functionality.
    It contains multiple sentences and paragraphs to demonstrate
    how the chunking algorithm works with different text lengths.
    
    The chunker should split this text into manageable pieces
    while maintaining context through overlapping sections.
    """
    
    chunks = chunker.chunk_text(sample_text)
    
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1}:")
        print(f"Text: {chunk['text'][:100]}...")
        print(f"Size: {chunk['metadata']['chunk_size']} characters")
        print(f"Position: {chunk['start_pos']}-{chunk['end_pos']}")


if __name__ == "__main__":
    main()
