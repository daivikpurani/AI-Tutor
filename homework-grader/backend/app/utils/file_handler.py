"""
File handler utilities for saving and managing uploaded files.
"""

import os
import shutil
from pathlib import Path
from typing import Tuple
from datetime import datetime
from loguru import logger

from app.config import settings


class FileHandler:
    """
    Handle file uploads and storage.
    """
    
    def __init__(self):
        """Initialize file handler and ensure directories exist."""
        # Use absolute paths so uploads are always stored inside the
        # homework-grader project tree, regardless of the process working directory.
        self.materials_dir = Path(settings.materials_upload_dir_abs)
        self.submissions_dir = Path(settings.submissions_upload_dir_abs)
        
        # Create directories if they don't exist
        self.materials_dir.mkdir(parents=True, exist_ok=True)
        self.submissions_dir.mkdir(parents=True, exist_ok=True)
    
    def save_material(
        self,
        file_content: bytes,
        filename: str,
        section_id: int
    ) -> Tuple[str, str, int]:
        """
        Save course material file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            section_id: Section ID
            
        Returns:
            Tuple of (file_path, file_name, file_size)
        """
        # Create section-specific directory
        section_dir = self.materials_dir / f"section_{section_id}"
        section_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(filename).suffix
        base_name = Path(filename).stem
        unique_filename = f"{base_name}_{timestamp}{file_ext}"
        
        # Full path
        file_path = section_dir / unique_filename
        
        # Save file
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            file_size = len(file_content)
            logger.info(f"Saved material: {file_path} ({file_size} bytes)")
            
            return str(file_path), unique_filename, file_size
        
        except Exception as e:
            logger.error(f"Error saving material file: {e}")
            raise
    
    def save_submission(
        self,
        file_content: bytes,
        filename: str,
        assignment_id: int,
        student_id: int
    ) -> Tuple[str, str, int]:
        """
        Save student submission file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            assignment_id: Assignment ID
            student_id: Student ID
            
        Returns:
            Tuple of (file_path, file_name, file_size)
        """
        # Create assignment-specific directory
        assignment_dir = self.submissions_dir / f"assignment_{assignment_id}"
        assignment_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with student ID and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(filename).suffix
        base_name = Path(filename).stem
        unique_filename = f"student_{student_id}_{base_name}_{timestamp}{file_ext}"
        
        # Full path
        file_path = assignment_dir / unique_filename
        
        # Save file
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            file_size = len(file_content)
            logger.info(f"Saved submission: {file_path} ({file_size} bytes)")
            
            return str(file_path), unique_filename, file_size
        
        except Exception as e:
            logger.error(f"Error saving submission file: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    def get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename."""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"


# Singleton instance
file_handler = FileHandler()
