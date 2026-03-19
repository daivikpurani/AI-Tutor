#!/usr/bin/env python3
"""
Database initialization script.
Creates all database tables based on SQLAlchemy models.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.db.session import engine, Base
from app.core.logging import setup_logging, logger
from app.config import settings

# Import all models to ensure they are registered
from app.models import (
    Faculty,
    Course,
    Student,
    Enrollment,
    Assignment,
    Material,
    Submission,
    Grade,
    Feedback
)


def init_db():
    """Initialize database tables."""
    try:
        logger.info("=" * 80)
        logger.info("DATABASE INITIALIZATION")
        logger.info("=" * 80)
        logger.info(f"Database URL: {settings.database_url}")
        logger.info(f"Environment: {settings.environment}")
        logger.info("")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # List all created tables
        logger.info("")
        logger.info("Tables created successfully:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  ✓ {table_name}")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("DATABASE INITIALIZATION COMPLETE")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        sys.exit(1)


def drop_all_tables():
    """Drop all database tables (use with caution!)."""
    try:
        logger.warning("=" * 80)
        logger.warning("DROPPING ALL TABLES")
        logger.warning("=" * 80)
        logger.warning("This will delete all data in the database!")
        
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Operation cancelled.")
            return
        
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully.")
        
        logger.warning("=" * 80)
        logger.warning("ALL TABLES DROPPED")
        logger.warning("=" * 80)
        
    except Exception as e:
        logger.error(f"Error dropping tables: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--drop":
            drop_all_tables()
        elif sys.argv[1] == "--reset":
            drop_all_tables()
            init_db()
        else:
            print("Usage:")
            print("  python init_db.py         # Create tables")
            print("  python init_db.py --drop  # Drop all tables")
            print("  python init_db.py --reset # Drop and recreate tables")
            sys.exit(1)
    else:
        init_db()
