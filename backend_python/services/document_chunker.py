"""
Enhanced Document Chunker Service
Handles splitting uploaded files into chunks for vector database storage.
Enhanced version with better file format support and error handling.
"""

import os
import re
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Try to import LangChain for semantic chunking
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available. Semantic chunking will fall back to default method.")

class DocumentChunker:
    """
    Enhanced document chunker for vector database storage.
    Supports various file formats and intelligent text splitting.
    """
    
    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 250):
        """
        Initialize the document chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters (default 1500 for papers/slides)
            chunk_overlap: Number of characters to overlap between chunks (default 250, ~15-20%)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_formats = ['.txt', '.md', '.pdf', '.docx', '.doc']
        
        logger.info(f"DocumentChunker initialized with chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def chunk_text(self, text: str, source: str = "text_input") -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks with intelligent boundary detection.
        Optimized for academic papers and PDF slides/decks.
        
        Boundary detection priority:
        1. Paragraph breaks (double newline)
        2. Section markers (headers, numbered sections)
        3. Smart sentence detection (ignores formatting periods)
        
        Args:
            text: Input text to chunk
            source: Source identifier for the text
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Intelligent boundary detection (only if we haven't reached end of text)
            if end < len(text):
                chunk_ratio = (end - start) / self.chunk_size
                original_end = end
                
                # Check higher thresholds first to ensure they are reachable
                # Priority 3: Smart sentence detection (only in last 100 chars)
                # Only use if chunk is >90% of target size (highest threshold, checked first)
                if chunk_ratio > 0.9:
                    search_start = max(start, end - 100)
                    
                    # Look for period followed by space (real sentence end)
                    # This avoids breaking on single-character abbreviations like "a." or "1."
                    sentence_end = text.rfind('. ', search_start, end)
                    while sentence_end > start and sentence_end > search_start:
                        # Verify it's not a single-character abbreviation
                        if sentence_end > 0:
                            char_before = text[sentence_end - 1]
                            # Only consider alphanumeric characters (most sentence endings)
                            if char_before in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                                # Scan backwards to find the start of the token
                                token_start = sentence_end - 1
                                while token_start > start and text[token_start] not in ' \t\n\r':
                                    token_start -= 1
                                # token_start now points to whitespace or start, so token starts at token_start + 1
                                token_start += 1
                                # Calculate token length
                                token_length = sentence_end - token_start
                                
                                # Only split if token length > 1 (avoid single-char abbreviations)
                                if token_length > 1:
                                    end = sentence_end + 2
                                    logger.debug(f"Chunk {chunk_id}: Split at sentence boundary at position {end}")
                                    break
                        
                        # If this sentence_end didn't work, search for the previous one
                        sentence_end = text.rfind('. ', search_start, sentence_end)
                
                # Priority 2: Try section markers (headers, numbered sections)
                # Look for section patterns in last 300 characters
                # Only check if chunk is >80% and we haven't found a boundary yet
                if chunk_ratio > 0.8 and end == original_end:
                    search_start = max(start, end - 300)
                    search_text = text[search_start:end]
                    
                    # Look for markdown headers (#, ##, ###)
                    md_header = search_text.rfind('\n#')
                    if md_header > 0:
                        end = search_start + md_header + 1
                        logger.debug(f"Chunk {chunk_id}: Split at markdown header at position {end}")
                    else:
                        # Look for numbered sections (1., 2., etc. or 1.1, 1.2, etc.)
                        section_pattern = re.search(r'\n\s*\d+\.\s+', search_text)
                        if section_pattern:
                            end = search_start + section_pattern.start() + 1
                            logger.debug(f"Chunk {chunk_id}: Split at numbered section at position {end}")
                
                # Priority 1: Try paragraph breaks (double newline) - best for semantic coherence
                # Only use if chunk is >70% and we haven't found a boundary yet
                if chunk_ratio > 0.7 and end == original_end:
                    para_break = text.rfind('\n\n', start, end)
                    if para_break > start + (self.chunk_size * 0.7):
                        end = para_break + 2
                        logger.debug(f"Chunk {chunk_id}: Split at paragraph break at position {end}")
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_data = {
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'chunk_id': chunk_id,
                    'metadata': {
                        'chunk_size': len(chunk_text),
                        'source': source,
                        'total_chunks': 0  # Will be updated later
                    }
                }
                chunks.append(chunk_data)
                chunk_id += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        # Update total chunks count
        for chunk in chunks:
            chunk['metadata']['total_chunks'] = len(chunks)
        
        logger.info(f"Created {len(chunks)} chunks from text (source: {source}, avg size: {sum(len(c['text']) for c in chunks) / len(chunks) if chunks else 0:.0f} chars)")
        return chunks
    
    def chunk_text_semantic(self, text: str, source: str = "text_input") -> List[Dict[str, Any]]:
        """
        Split text using LangChain's RecursiveCharacterTextSplitter for better semantic boundaries.
        
        This method preserves markdown headers and section boundaries for cleaner chunks.
        Falls back to default chunk_text if LangChain is not available.
        
        Args:
            text: Input text to chunk
            source: Source identifier for the text
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, falling back to default chunking")
            return self.chunk_text(text, source)
        
        if not text.strip():
            logger.warning("Empty text provided for semantic chunking")
            return []
        
        try:
            # Create RecursiveCharacterTextSplitter with semantic separators
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=[
                    "\n## ",      # Markdown h2
                    "\n### ",     # Markdown h3
                    "\n#### ",    # Markdown h4
                    "\n\n",       # Paragraph breaks
                    "\n",         # Line breaks
                    ". ",         # Sentence breaks
                    " ",          # Word breaks
                    ""            # Character breaks (fallback)
                ],
                is_separator_regex=False
            )
            
            # Split text
            text_chunks = text_splitter.split_text(text)
            
            # Convert to our chunk format
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                if chunk_text.strip():
                    chunk_data = {
                        'text': chunk_text.strip(),
                        'start_pos': -1,  # LangChain doesn't provide positions
                        'end_pos': -1,
                        'chunk_id': i,
                        'metadata': {
                            'chunk_size': len(chunk_text),
                            'source': source,
                            'total_chunks': len(text_chunks),
                            'chunking_method': 'semantic_langchain'
                        }
                    }
                    chunks.append(chunk_data)
            
            logger.info(f"Created {len(chunks)} semantic chunks from text (source: {source}, avg size: {sum(len(c['text']) for c in chunks) / len(chunks) if chunks else 0:.0f} chars)")
            return chunks
            
        except Exception as e:
            logger.error(f"Semantic chunking failed: {e}. Falling back to default chunking.")
            return self.chunk_text(text, source)
    
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
        
        logger.info(f"Processing file: {file_path}")
        
        # Extract text based on file type
        text = self._extract_text_from_file(file_path)
        
        if not text.strip():
            logger.warning(f"No text content extracted from {file_path}")
            return []
        
        # Chunk the extracted text (use semantic if enabled)
        try:
            from utils.config import settings
            use_semantic = settings.use_semantic_chunking
        except (ImportError, AttributeError):
            use_semantic = False
        
        if use_semantic and LANGCHAIN_AVAILABLE:
            chunks = self.chunk_text_semantic(text, source=str(file_path))
        else:
            chunks = self.chunk_text(text, source=str(file_path))
        
        # Add file metadata to each chunk
        for chunk in chunks:
            chunk['metadata'].update({
                'filename': file_path.name,
                'file_path': str(file_path),
                'file_type': file_path.suffix.lower(),
                'file_size': file_path.stat().st_size
            })
        
        logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks created")
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
        
        try:
            if suffix == '.txt' or suffix == '.md':
                return self._extract_text_file(file_path)
            elif suffix == '.pdf':
                return self._extract_pdf_file(file_path)
            elif suffix in ['.docx', '.doc']:
                return self._extract_word_file(file_path)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            raise
    
    def _extract_text_file(self, file_path: Path) -> str:
        """Extract text from plain text or markdown files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Failed to read text file {file_path}: {e}")
                raise
    
    def _extract_pdf_file(self, file_path: Path) -> str:
        """Extract text from PDF files."""
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text.strip()
            
        except ImportError:
            logger.warning("PyPDF2 not available, using placeholder for PDF")
            return f"[PDF content placeholder for {file_path.name}]"
        except Exception as e:
            logger.error(f"Failed to extract PDF {file_path}: {e}")
            return f"[Error extracting PDF {file_path.name}: {str(e)}]"
    
    def _extract_word_file(self, file_path: Path) -> str:
        """Extract text from Word documents."""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except ImportError:
            logger.warning("python-docx not available, using placeholder for Word document")
            return f"[Word document content placeholder for {file_path.name}]"
        except Exception as e:
            logger.error(f"Failed to extract Word document {file_path}: {e}")
            return f"[Error extracting Word document {file_path.name}: {str(e)}]"
    
    def chunk_multiple_files(self, file_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Chunk multiple files and return results organized by filename.
        
        Args:
            file_paths: List of file paths to chunk
            
        Returns:
            Dictionary mapping filenames to their chunks
        """
        results = {}
        
        for file_path in file_paths:
            try:
                chunks = self.chunk_file(file_path)
                filename = Path(file_path).name
                results[filename] = chunks
                logger.info(f"Successfully processed {filename}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results[Path(file_path).name] = []
        
        return results
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_characters': 0,
                'average_chunk_size': 0,
                'min_chunk_size': 0,
                'max_chunk_size': 0
            }
        
        chunk_sizes = [len(chunk['text']) for chunk in chunks]
        total_chars = sum(chunk_sizes)
        
        return {
            'total_chunks': len(chunks),
            'total_characters': total_chars,
            'average_chunk_size': total_chars / len(chunks),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes)
        }
