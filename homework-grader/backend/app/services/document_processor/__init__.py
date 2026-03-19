"""
Document processor service - orchestrates PDF extraction and chunking.
"""

from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

from app.services.document_processor.pdf_extractor import pdf_extractor
from app.services.document_processor.text_chunker import create_text_chunker
from app.config import settings


class DocumentProcessor:
    """
    Main document processing service.
    Handles PDF extraction, text chunking, and preprocessing.
    """
    
    def __init__(self):
        self.pdf_extractor = pdf_extractor
        self.text_chunker = create_text_chunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    def process_pdf(self, pdf_path: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Process a PDF file: extract text and create chunks.
        
        Args:
            pdf_path: Path to PDF file
            metadata: Optional metadata to attach to chunks
            
        Returns:
            Dictionary with extracted text, chunks, and statistics
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Extract text from PDF
        extraction_result = self.pdf_extractor.extract_text(pdf_path)
        
        # Create chunks
        chunks = self.text_chunker.chunk_by_pages(
            extraction_result['pages'],
            metadata=metadata
        )
        
        result = {
            "file_path": pdf_path,
            "file_name": Path(pdf_path).name,
            "full_text": extraction_result['full_text'],
            "chunks": chunks,
            "statistics": {
                "num_pages": extraction_result['num_pages'],
                "num_chunks": len(chunks),
                "total_chars": extraction_result['total_chars'],
                "avg_chunk_size": sum(c['char_count'] for c in chunks) / len(chunks) if chunks else 0
            },
            "metadata": extraction_result['metadata']
        }
        
        logger.info(f"Processed PDF: {result['statistics']['num_pages']} pages, {result['statistics']['num_chunks']} chunks")
        
        return result
    
    def process_pdf_bytes(self, pdf_bytes: bytes, filename: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Process PDF from bytes (uploaded file).
        
        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename
            metadata: Optional metadata to attach to chunks
            
        Returns:
            Dictionary with extracted text, chunks, and statistics
        """
        logger.info(f"Processing uploaded PDF: {filename}")
        
        # Extract text from PDF bytes
        extraction_result = self.pdf_extractor.extract_text_from_bytes(pdf_bytes)
        
        # Create chunks
        chunks = self.text_chunker.chunk_by_pages(
            extraction_result['pages'],
            metadata=metadata
        )
        
        result = {
            "file_name": filename,
            "full_text": extraction_result['full_text'],
            "chunks": chunks,
            "statistics": {
                "num_pages": extraction_result['num_pages'],
                "num_chunks": len(chunks),
                "total_chars": extraction_result['total_chars'],
                "avg_chunk_size": sum(c['char_count'] for c in chunks) / len(chunks) if chunks else 0
            },
            "metadata": extraction_result['metadata']
        }
        
        logger.info(f"Processed uploaded PDF: {result['statistics']['num_pages']} pages, {result['statistics']['num_chunks']} chunks")
        
        return result


# Singleton instance
document_processor = DocumentProcessor()
