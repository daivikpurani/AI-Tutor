#!/usr/bin/env python3
"""
Script to load all course materials from the course_materials directory into the vector database.
This script processes all supported files in the course_materials folder and its subdirectories,
chunks them, and adds them to the ChromaDB vector database for RAG retrieval.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend_python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend_python'))

from services.vector_db import VectorDatabase
from services.document_chunker import DocumentChunker

async def load_course_materials():
    """Load all documents from course_materials directory."""
    # Initialize services
    vector_db = VectorDatabase()
    document_chunker = DocumentChunker()
    
    # Get course materials directory
    project_root = Path(__file__).parent.parent
    materials_dir = project_root / "course_materials"
    
    if not materials_dir.exists():
        print(f"Course materials directory not found: {materials_dir}")
        print(f"Please create the directory and add your course materials.")
        return
    
    print(f"Loading course materials from: {materials_dir}")
    print("-" * 60)
    
    # Supported file extensions
    supported_extensions = {'.pdf', '.txt', '.md', '.docx', '.doc'}
    
    # Find all supported files recursively
    files_to_process = []
    for ext in supported_extensions:
        files_to_process.extend(materials_dir.rglob(f"*{ext}"))
    
    if not files_to_process:
        print("No supported files found in course_materials directory")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        return
    
    print(f"Found {len(files_to_process)} files to process")
    print("-" * 60)
    
    success_count = 0
    error_count = 0
    
    for file_path in files_to_process:
        try:
            relative_path = file_path.relative_to(materials_dir)
            print(f"Processing: {relative_path}")
            
            # Chunk the document
            chunks = document_chunker.chunk_file(str(file_path))
            
            if not chunks:
                print(f"  ⚠ No chunks extracted (file may be empty or unsupported)")
                continue
            
            # Store chunks in vector database
            success = await vector_db.add_documents(chunks, str(relative_path))
            
            if success:
                success_count += 1
                print(f"  ✓ Added {len(chunks)} chunks")
            else:
                error_count += 1
                print(f"  ✗ Failed to add chunks")
                
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error: {e}")
    
    print("-" * 60)
    print(f"Summary:")
    print(f"  Successfully processed: {success_count}/{len(files_to_process)} files")
    if error_count > 0:
        print(f"  Errors: {error_count} files")
    
    # Check final count
    try:
        count = vector_db.collection.count()
        print(f"Total document chunks in database: {count}")
    except Exception as e:
        print(f"Could not retrieve database count: {e}")

if __name__ == "__main__":
    asyncio.run(load_course_materials())

