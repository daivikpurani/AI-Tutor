#!/usr/bin/env python3
"""
Migration Script for Re-indexing Documents with OpenAI Embeddings
Re-chunks and re-embeds existing documents for improved retrieval quality.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend_python"))

from services.vector_db import VectorDatabase
from services.document_chunker import DocumentChunker
from utils.config import settings
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate_documents():
    """
    Migrate existing documents to use new embeddings and chunking.
    
    Steps:
    1. Export all documents from ChromaDB
    2. Delete old collection
    3. Re-chunk documents with semantic splitter (if enabled)
    4. Re-embed with OpenAI embeddings (if enabled)
    5. Re-index into ChromaDB
    """
    logger.info("="*60)
    logger.info("Document Migration Script")
    logger.info("="*60)
    logger.info(f"OpenAI Embeddings: {'Enabled' if settings.use_openai_embeddings else 'Disabled'}")
    logger.info(f"Semantic Chunking: {'Enabled' if settings.use_semantic_chunking else 'Disabled'}")
    logger.info(f"Reranking: {'Enabled' if settings.enable_reranking else 'Disabled'}")
    logger.info("="*60)
    
    # Initialize services
    logger.info("Initializing vector database...")
    vector_db = VectorDatabase()
    
    logger.info("Initializing document chunker...")
    chunker = DocumentChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    # Step 1: Get all existing documents
    logger.info("Fetching existing documents...")
    documents = await vector_db.list_documents()
    
    if not documents:
        logger.warning("No documents found in the database. Nothing to migrate.")
        return
    
    logger.info(f"Found {len(documents)} documents to migrate:")
    for doc in documents:
        logger.info(f"  - {doc['filename']} ({doc['chunk_count']} chunks)")
    
    # Ask for confirmation
    print("\n" + "="*60)
    print("WARNING: This will delete the existing collection and re-index all documents.")
    print("Make sure you have:")
    print("  1. OpenAI API key set in .env (if using OpenAI embeddings)")
    print("  2. Original document files available in course_materials/")
    print("="*60)
    response = input("\nProceed with migration? (yes/no): ").strip().lower()
    
    if response != 'yes':
        logger.info("Migration cancelled by user.")
        return
    
    # Step 2: Collect unique filenames
    filenames = set(doc['filename'] for doc in documents)
    logger.info(f"Unique files to process: {len(filenames)}")
    
    # Step 3: Reset database (delete and recreate collection)
    logger.info("Resetting database...")
    success = await vector_db.reset_database()
    if not success:
        logger.error("Failed to reset database. Aborting migration.")
        return
    
    logger.info("Database reset successful. Re-initializing...")
    vector_db = VectorDatabase()  # Reinitialize with new collection
    
    # Step 4: Process each file
    logger.info("Processing files...")
    course_materials_dir = Path(settings.course_materials_directory)
    processed_count = 0
    failed_count = 0
    
    for filename in filenames:
        file_path = course_materials_dir / filename
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}. Skipping.")
            failed_count += 1
            continue
        
        try:
            logger.info(f"Processing: {filename}")
            
            # Re-chunk the file (uses semantic chunking if enabled)
            chunks = chunker.chunk_file(str(file_path))
            
            if not chunks:
                logger.warning(f"No chunks created for {filename}. Skipping.")
                failed_count += 1
                continue
            
            # Add to vector database (will use OpenAI embeddings if enabled)
            success = await vector_db.add_documents(chunks, filename)
            
            if success:
                logger.info(f"✓ Successfully migrated {filename} ({len(chunks)} chunks)")
                processed_count += 1
            else:
                logger.error(f"✗ Failed to add {filename} to database")
                failed_count += 1
                
        except Exception as e:
            logger.error(f"✗ Error processing {filename}: {e}")
            failed_count += 1
    
    # Summary
    logger.info("="*60)
    logger.info("Migration Complete!")
    logger.info(f"Successfully processed: {processed_count} files")
    logger.info(f"Failed: {failed_count} files")
    logger.info("="*60)
    
    # Verify final state
    logger.info("Verifying database state...")
    final_docs = await vector_db.list_documents()
    logger.info(f"Total documents in database: {len(final_docs)}")
    total_chunks = sum(doc['chunk_count'] for doc in final_docs)
    logger.info(f"Total chunks: {total_chunks}")
    
    # Get database stats
    stats = await vector_db.get_database_stats()
    logger.info(f"Database size: {stats.get('disk_usage', 'Unknown')}")


def main():
    """Main entry point."""
    try:
        asyncio.run(migrate_documents())
    except KeyboardInterrupt:
        logger.info("\nMigration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
