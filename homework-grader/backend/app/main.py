"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.core.logging import setup_logging, logger
from app.db.session import engine, Base

# Import API routers
from app.api.v1 import materials, submissions, grading, lists, assignments


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Homework Grading System...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    
    # Create database tables — wrapped so a missing PostgreSQL instance doesn't
    # crash the entire combined application; grading endpoints will return 500
    # until the database is available and the app is restarted.
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as _db_err:
        logger.warning(
            f"PostgreSQL is not available: {_db_err}. "
            "Grading endpoints will not work until a PostgreSQL instance is "
            "running at the configured DATABASE_URL and the service is restarted."
        )
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Homework Grading System...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered homework grading system for SF State CS Department",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan
)

# Setup logging
setup_logging()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# HEALTH CHECK & ROOT ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Homework Grading System API",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": f"{settings.api_prefix}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get(f"{settings.api_prefix}/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "AI Homework Grading System API v1",
        "endpoints": {
            "courses": f"{settings.api_prefix}/courses",
            "assignments": f"{settings.api_prefix}/assignments",
            "submissions": f"{settings.api_prefix}/submissions",
            "materials": f"{settings.api_prefix}/materials",
            "grading": f"{settings.api_prefix}/grading",
            "feedback": f"{settings.api_prefix}/feedback"
        }
    }


# =============================================================================
# INCLUDE API ROUTERS
# =============================================================================

app.include_router(
    materials.router,
    prefix=f"{settings.api_prefix}/materials",
    tags=["materials"]
)

app.include_router(
    submissions.router,
    prefix=f"{settings.api_prefix}/submissions",
    tags=["submissions"]
)

app.include_router(
    grading.router,
    prefix=f"{settings.api_prefix}/grading",
    tags=["grading"]
)

app.include_router(
    lists.router,
    prefix=f"{settings.api_prefix}/lists",
    tags=["lists"]
)

app.include_router(
    assignments.router,
    prefix=f"{settings.api_prefix}/assignments",
    tags=["assignments"]
)
# app.include_router(
#     courses.router,
#     prefix=f"{settings.api_prefix}/courses",
#     tags=["courses"]
# )

# app.include_router(
#     assignments.router,
#     prefix=f"{settings.api_prefix}/assignments",
#     tags=["assignments"]
# )


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
