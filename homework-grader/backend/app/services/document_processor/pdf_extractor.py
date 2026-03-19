"""
PDF extraction service for processing course materials and student submissions.
"""

import os
from typing import Dict, List, Optional
from pathlib import Path
import pdfplumber
from loguru import logger


class PDFExtractor:
    """
    Extract text and metadata from PDF files.
    """
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def is_supported(self, filename: str) -> bool:
        """Check if file type is supported."""
        return Path(filename).suffix.lower() in self.supported_extensions
    
    def extract_text(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract metadata
                metadata = {
                    "num_pages": len(pdf.pages),
                    "metadata": pdf.metadata or {},
                }
                
                # Extract text from all pages
                full_text = ""
                pages_text = []
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    pages_text.append({
                        "page_number": page_num,
                        "text": page_text,
                        "char_count": len(page_text)
                    })
                    full_text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                
                return {
                    "full_text": full_text.strip(),
                    "pages": pages_text,
                    "num_pages": metadata["num_pages"],
                    "total_chars": len(full_text),
                    "metadata": metadata["metadata"]
                }
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            raise
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Dict[str, any]:
        """
        Extract text from PDF bytes (for uploaded files).
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Dictionary with extracted text and metadata
        """
        import io
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                # Extract metadata
                metadata = {
                    "num_pages": len(pdf.pages),
                    "metadata": pdf.metadata or {},
                }
                
                # Extract text from all pages
                full_text = ""
                pages_text = []
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    pages_text.append({
                        "page_number": page_num,
                        "text": page_text,
                        "char_count": len(page_text)
                    })
                    full_text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                
                return {
                    "full_text": full_text.strip(),
                    "pages": pages_text,
                    "num_pages": metadata["num_pages"],
                    "total_chars": len(full_text),
                    "metadata": metadata["metadata"]
                }
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF bytes: {e}")
            raise


# Singleton instance
pdf_extractor = PDFExtractor()
