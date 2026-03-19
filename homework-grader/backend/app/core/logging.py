"""
Logging configuration for the application.
"""

import sys
import logging
from pathlib import Path
from loguru import logger as loguru_logger

from app.config import settings


class InterceptHandler(logging.Handler):
    """
    Intercepts standard logging and redirects to loguru.
    """
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Configure logging for the application.
    """
    # Remove default loguru handler
    loguru_logger.remove()
    
    # Add console handler
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Add file handler if log file is specified (use absolute path)
    if settings.log_file:
        log_path = Path(settings.log_file_abs)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        loguru_logger.add(
            settings.log_file_abs,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Intercept uvicorn and fastapi logs
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
    
    loguru_logger.info("Logging configured successfully")


# Export logger for use in other modules
logger = loguru_logger
