"""
Ai-Tutor FastAPI Backend
Main application entry point with all API routes and WebSocket support.
"""

import os
import sys
import logging
from pathlib import Path

# Add the script's directory to Python path to ensure imports work
script_dir = Path(__file__).parent.absolute()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form, Request
from fastapi.datastructures import FormData
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import json

logger = logging.getLogger(__name__)

from services.query_handler import QueryHandler
from services.document_chunker import DocumentChunker
from services.vector_db import VectorDatabase
from services.benchmark_config import BenchmarkConfig
from services.llm_service import HybridLLMService, LLMProvider
from services.relevance_scorer import RelevanceScorer
from models.schemas import ChatRequest, ChatResponse, UploadResponse, HealthResponse, SearchRequest, SearchResponse, MultipleUploadResponse, FileUploadResult
from utils.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Ai-Tutor API",
    description="AI-powered tutoring system with vector database and real-time chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
query_handler = QueryHandler()
document_chunker = DocumentChunker(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)
vector_db = VectorDatabase()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Ai-Tutor Backend API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services={
            "vector_db": await vector_db.health_check(),
            "query_handler": "healthy"
        }
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for processing user queries."""
    try:
        # Process query through the query handler with metadata for richer response
        result = await query_handler.process_query_with_metadata(
            query=request.message,
            user_id=request.user_id,
            conversation_history=request.conversation_history,
            mode=request.mode
        )

        return ChatResponse(
            response=result.get("response", ""),
            query=request.message,
            user_id=request.user_id,
            timestamp=result.get("timestamp", datetime.now().isoformat()),
            context_chunks_used=result.get("context_chunks_used", 0),
            status=result.get("status", "success"),
            llm_provider=result.get("llm_provider"),
            llm_model=result.get("llm_model"),
            confidence=result.get("llm_metadata", {}).get("confidence"),
            escalated=result.get("llm_metadata", {}).get("escalated"),
            citations=result.get("citations"),
            tldr=result.get("tldr")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/api/chat_benchmark")
async def chat_benchmark_endpoint(request: ChatRequest):
    """Benchmark chat endpoint: returns response plus provider/model/usage/metadata."""
    try:
        result = await query_handler.process_query_with_metadata(
            query=request.message,
            user_id=request.user_id,
            conversation_history=request.conversation_history,
            mode=request.mode
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing benchmark query: {str(e)}")

@app.post("/api/upload")
async def upload_file(request: Request):
    """
    Upload and process one or multiple documents for vector database.
    
    - Single file: Use field name 'file' (backward compatible) or 'files' with one file
      Returns UploadResponse
    - Multiple files: Use field name 'files' with multiple files (send multiple form fields with same name)
      Returns MultipleUploadResponse with per-file results
    
    Individual file failures don't stop the entire batch when uploading multiple files.
    """
    # Parse form data manually to handle both single and multiple files
    form = await request.form()
    
    files_list = []
    
    # Build list of file-like objects: must have .read and .filename (Starlette UploadFile interface)
    def is_upload_file(obj: Any) -> bool:
        return (
            hasattr(obj, "read") and callable(getattr(obj, "read"))
            and hasattr(obj, "filename") and obj.filename is not None
        )
    
    # Method 1: Use form._list first (most reliable for multipart; handles curl and requests)
    if hasattr(form, "_list"):
        for key, value in form._list:
            if (key == "file" or key == "files") and is_upload_file(value):
                files_list.append(value)
    
    # Method 2: Fallback - form['file'] or form['files']
    if not files_list and "file" in form:
        f = form["file"]
        if is_upload_file(f):
            files_list = [f]
    if not files_list and "files" in form:
        f = form["files"]
        if is_upload_file(f):
            files_list = [f] if not isinstance(f, list) else [x for x in f if is_upload_file(x)]
    
    if not files_list:
        # Log form structure for debugging
        logger.warning(f"Form keys: {list(form.keys()) if hasattr(form, 'keys') else 'N/A'}")
        logger.warning(f"Form has _list: {hasattr(form, '_list')}")
        if hasattr(form, '_list'):
            logger.warning(f"Form _list items: {[(k, type(v).__name__ if hasattr(v, '__class__') else str(type(v))) for k, v in form._list]}")
        raise HTTPException(status_code=400, detail="No files provided. Use 'file' for single upload or 'files' for multiple uploads.")
    
    files = files_list
    
    # Single file upload - return simple response for backward compatibility
    if len(files) == 1:
        file = files[0]
        file_path = None
        try:
            # Save uploaded file temporarily
            file_path = f"temp_uploads/{file.filename}"
            os.makedirs("temp_uploads", exist_ok=True)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Chunk the document
            chunks = document_chunker.chunk_file(file_path)
            
            # Store chunks in vector database
            await vector_db.add_documents(chunks, file.filename)
            
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return UploadResponse(
                message=f"Successfully processed {file.filename}",
                filename=file.filename,
                chunks_created=len(chunks),
                status="success"
            )
            
        except Exception as e:
            # Clean up temporary file if it exists
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    # Multiple files upload - return detailed response
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        file_path = None
        try:
            # Save uploaded file temporarily
            file_path = f"temp_uploads/{file.filename}"
            os.makedirs("temp_uploads", exist_ok=True)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Chunk the document
            chunks = document_chunker.chunk_file(file_path)
            
            # Store chunks in vector database
            await vector_db.add_documents(chunks, file.filename)
            
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            results.append(FileUploadResult(
                filename=file.filename,
                chunks_created=len(chunks),
                status="success"
            ))
            successful += 1
            logger.info(f"Successfully processed {file.filename}: {len(chunks)} chunks")
            
        except Exception as e:
            # Clean up temporary file if it exists
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            error_msg = str(e)
            results.append(FileUploadResult(
                filename=file.filename,
                chunks_created=0,
                status="error",
                error=error_msg
            ))
            failed += 1
            logger.error(f"Failed to process {file.filename}: {error_msg}")
    
    return MultipleUploadResponse(
        message=f"Processed {len(files)} files: {successful} successful, {failed} failed",
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results
    )

@app.post("/api/upload-direct")
async def upload_document_direct(
    text: str = Form(...),
    filename: str = Form(...),
    file_type: str = Form("text"),
    source: str = Form("direct_upload")
):
    """
    Upload document text directly to the main collection without chunking.
    Useful for adding structured content, notes, or small documents.
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text content cannot be empty")
        
        if not filename.strip():
            raise HTTPException(status_code=400, detail="Filename cannot be empty")
        
        # Prepare metadata
        metadata = {
            "file_type": file_type,
            "source": source,
            "upload_method": "direct_api"
        }
        
        # Add document directly to collection
        success = await vector_db.add_document_direct(
            text=text,
            filename=filename,
            metadata=metadata
        )
        
        if success:
            return {
                "message": f"Successfully uploaded '{filename}' directly to collection",
                "filename": filename,
                "content_length": len(text),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload document")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/upload-text")
async def upload_text_content(
    content: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form("general")
):
    """
    Upload text content with structured metadata.
    Alternative endpoint for uploading formatted text content.
    """
    try:
        if not content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        if not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        
        # Create filename from title
        filename = f"{title.replace(' ', '_').lower()}.txt"
        
        # Prepare metadata
        metadata = {
            "file_type": "text",
            "source": "text_upload",
            "title": title,
            "description": description,
            "category": category,
            "upload_method": "text_api"
        }
        
        # Add document directly to collection
        success = await vector_db.add_document_direct(
            text=content,
            filename=filename,
            metadata=metadata
        )
        
        if success:
            return {
                "message": f"Successfully uploaded text content '{title}'",
                "filename": filename,
                "title": title,
                "content_length": len(content),
                "category": category,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload text content")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents."""
    try:
        documents = await vector_db.list_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.get("/api/db-stats")
async def get_database_stats():
    """Get comprehensive database statistics."""
    try:
        stats = await vector_db.get_database_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")

@app.post("/api/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search for document chunks related to a query.
    Returns raw chunks with metadata, distance scores, and text content.
    This endpoint returns the actual chunks without LLM processing.
    """
    try:
        # Search for similar chunks using vector similarity search
        chunks = await vector_db.search_similar(
            query=request.query,
            n_results=request.n_results,
            filter_metadata=request.filter_metadata
        )
        
        # Format chunks for response
        results = []
        for chunk in chunks:
            results.append({
                "text": chunk.get("text", ""),
                "metadata": chunk.get("metadata", {}),
                "id": chunk.get("id"),
                "distance": chunk.get("distance")
            })
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.get("/api/test-db")
async def test_database_connection():
    """Test database connection and functionality."""
    try:
        # Test basic database operations
        test_results = {
            "database_status": "connected",
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test 1: Check if database is accessible
        try:
            health_status = await vector_db.health_check()
            test_results["tests"]["health_check"] = {
                "status": "passed",
                "result": health_status
            }
        except Exception as e:
            test_results["tests"]["health_check"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Test 2: List documents
        try:
            documents = await vector_db.list_documents()
            test_results["tests"]["list_documents"] = {
                "status": "passed",
                "document_count": len(documents),
                "documents": documents[:5]  # Show first 5 documents
            }
        except Exception as e:
            test_results["tests"]["list_documents"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Test 3: Test search functionality
        try:
            test_query = "test query"
            search_results = await vector_db.search_similar(test_query, 3)
            test_results["tests"]["search_functionality"] = {
                "status": "passed",
                "query": test_query,
                "results_count": len(search_results),
                "sample_results": search_results[:2] if search_results else []
            }
        except Exception as e:
            test_results["tests"]["search_functionality"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Test 4: Test query handler
        try:
            test_response = await query_handler.process_query(
                query="What is this about?",
                user_id="test-user"
            )
            test_results["tests"]["query_handler"] = {
                "status": "passed",
                "response_length": len(test_response.get("response", "")),
                "context_chunks_used": test_response.get("context_chunks_used", 0)
            }
        except Exception as e:
            test_results["tests"]["query_handler"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Overall status
        all_passed = all(test["status"] == "passed" for test in test_results["tests"].values())
        test_results["overall_status"] = "passed" if all_passed else "partial"
        
        return test_results
        
    except Exception as e:
        return {
            "database_status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "overall_status": "failed"
        }

@app.post("/api/test-query")
async def test_query_endpoint(request: ChatRequest):
    """Test endpoint for query processing - useful for testing database connection."""
    try:
        # Process query through the query handler
        result = await query_handler.process_query(
            query=request.message,
            user_id=request.user_id or "test-user",
            conversation_history=request.conversation_history,
            mode=request.mode
        )
        
        return {
            "test_status": "success",
            "query": request.message,
            "response": result["response"],
            "context_chunks_used": result.get("context_chunks_used", 0),
            "timestamp": result["timestamp"],
            "processing_time": "calculated_in_backend"
        }
        
    except Exception as e:
        return {
            "test_status": "error",
            "query": request.message,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the vector database."""
    try:
        await vector_db.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.post("/api/backup-db")
async def backup_database():
    """Create a backup of the ChromaDB database."""
    try:
        backup_path = f"backups/chromadb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs("backups", exist_ok=True)
        
        success = await vector_db.backup_database(backup_path)
        if success:
            return {
                "message": "Database backup created successfully",
                "backup_path": backup_path,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

@app.post("/api/reset-db")
async def reset_database():
    """Reset the entire database (delete all data)."""
    try:
        success = await vector_db.reset_database()
        if success:
            return {
                "message": "Database reset successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reset database")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

# Benchmark API endpoints
@app.get("/api/benchmark/models")
async def get_benchmark_models():
    """Get list of available models for benchmarking."""
    try:
        config = BenchmarkConfig()
        import asyncio
        available_models = await config.detect_available_models()
        
        models_list = []
        for model in available_models:
            models_list.append({
                "provider": model.provider,
                "model": model.model_name,
                "display_name": model.display_name,
                "available": model.is_available
            })
        
        return {
            "models": models_list,
            "total": len(models_list),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")

@app.post("/api/benchmark/run")
async def run_benchmark_endpoint(
    query: str = Form(...),
    provider: str = Form(...),
    model: str = Form(...),
    mode: str = Form("exploration")
):
    """
    Run a benchmark for a specific model with a single query.
    Returns comprehensive metrics.
    """
    try:
        # Initialize services
        llm_service = HybridLLMService()
        await llm_service.initialize()
        
        query_handler = QueryHandler()
        await query_handler._ensure_llm_service_initialized()
        
        relevance_scorer = RelevanceScorer()
        
        # Map provider string to enum
        provider_enum = None
        if provider.lower() == "ollama":
            provider_enum = LLMProvider.OLLAMA
        elif provider.lower() == "openai":
            provider_enum = LLMProvider.OPENAI
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        # Get context
        context_chunks = await query_handler._get_relevant_context(query)
        context_text = query_handler._build_context_text(context_chunks)
        
        # Build prompt
        prompt = query_handler.prompt_templates.create_tutor_prompt(
            query=query,
            context=context_text,
            conversation_history="",
            mode=mode
        )
        
        # Prepare messages
        system_prompt = (
            query_handler.prompt_templates.SYSTEM_ASSESSMENT 
            if mode == "assessment" 
            else query_handler.prompt_templates.SYSTEM_EXPLORATION
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Measure latency
        start_time = datetime.now()
        
        # Generate response
        response = await llm_service.generate_response_with_provider(
            messages=messages,
            provider=provider_enum,
            model=model,
            max_tokens=1000,
            temperature=0.7
        )
        
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000.0
        
        # Build citations
        citations = []
        for chunk in context_chunks:
            meta = chunk.get('metadata', {}) if isinstance(chunk, dict) else {}
            citations.append({
                'title': meta.get('title') or meta.get('filename') or 'Source',
                'url': meta.get('url') or meta.get('source_url'),
                'score': None
            })
        
        # Calculate relevance scores
        self_check_confidence = response.metadata.get('confidence', 0.0) if response.metadata else 0.0
        scores = relevance_scorer.score_response(
            response=response.content,
            query=query,
            self_check_confidence=self_check_confidence,
            citations=citations
        )
        
        return {
            "query": query,
            "provider": provider,
            "model": model,
            "response": response.content,
            "latency_ms": round(latency_ms, 2),
            "response_length": len(response.content),
            "prompt_tokens": response.usage.get("prompt_tokens", 0),
            "completion_tokens": response.usage.get("completion_tokens", 0),
            "total_tokens": response.usage.get("total_tokens", 0),
            "self_check_confidence": scores["self_check_confidence"],
            "citation_score": scores["citation_score"],
            "completeness_score": scores["completeness_score"],
            "quality_score": scores["quality_score"],
            "overall_score": scores["overall_score"],
            "citations": citations,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark failed: {str(e)}")

@app.post("/api/benchmark/compare")
async def compare_models_endpoint(
    query: str = Form(...),
    models: Optional[str] = Form(None),  # JSON array of {"provider": "...", "model": "..."}
    mode: str = Form("exploration")
):
    """
    Compare multiple models with a single query.
    If models not specified, compares all available models.
    """
    try:
        # Initialize services
        llm_service = HybridLLMService()
        await llm_service.initialize()
        
        query_handler = QueryHandler()
        await query_handler._ensure_llm_service_initialized()
        
        relevance_scorer = RelevanceScorer()
        
        # Parse models or get all available
        if models:
            import json
            models_to_test = json.loads(models)
        else:
            config = BenchmarkConfig()
            available_models = await config.detect_available_models()
            models_to_test = [
                {"provider": m.provider, "model": m.model_name}
                for m in available_models if m.is_available
            ]
        
        results = []
        
        for model_info in models_to_test:
            provider_str = model_info["provider"]
            model_name = model_info["model"]
            
            try:
                # Map provider
                provider_enum = None
                if provider_str.lower() == "ollama":
                    provider_enum = LLMProvider.OLLAMA
                elif provider_str.lower() == "openai":
                    provider_enum = LLMProvider.OPENAI
                else:
                    continue
                
                # Get context
                context_chunks = await query_handler._get_relevant_context(query)
                context_text = query_handler._build_context_text(context_chunks)
                
                # Build prompt
                prompt = query_handler.prompt_templates.create_tutor_prompt(
                    query=query,
                    context=context_text,
                    conversation_history="",
                    mode=mode
                )
                
                # Prepare messages
                system_prompt = (
                    query_handler.prompt_templates.SYSTEM_ASSESSMENT 
                    if mode == "assessment" 
                    else query_handler.prompt_templates.SYSTEM_EXPLORATION
                )
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                
                # Measure latency
                start_time = datetime.now()
                
                # Generate response
                response = await llm_service.generate_response_with_provider(
                    messages=messages,
                    provider=provider_enum,
                    model=model_name,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000.0
                
                # Build citations
                citations = []
                for chunk in context_chunks:
                    meta = chunk.get('metadata', {}) if isinstance(chunk, dict) else {}
                    citations.append({
                        'title': meta.get('title') or meta.get('filename') or 'Source',
                        'url': meta.get('url') or meta.get('source_url'),
                        'score': None
                    })
                
                # Calculate relevance scores
                self_check_confidence = response.metadata.get('confidence', 0.0) if response.metadata else 0.0
                scores = relevance_scorer.score_response(
                    response=response.content,
                    query=query,
                    self_check_confidence=self_check_confidence,
                    citations=citations
                )
                
                results.append({
                    "provider": provider_str,
                    "model": model_name,
                    "response": response.content,
                    "latency_ms": round(latency_ms, 2),
                    "response_length": len(response.content),
                    "prompt_tokens": response.usage.get("prompt_tokens", 0),
                    "completion_tokens": response.usage.get("completion_tokens", 0),
                    "total_tokens": response.usage.get("total_tokens", 0),
                    "self_check_confidence": scores["self_check_confidence"],
                    "citation_score": scores["citation_score"],
                    "completeness_score": scores["completeness_score"],
                    "quality_score": scores["quality_score"],
                    "overall_score": scores["overall_score"],
                    "citations_count": len(citations),
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "provider": provider_str,
                    "model": model_name,
                    "error": str(e),
                    "status": "error"
                })
        
        return {
            "query": query,
            "models_tested": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

# WebSocket endpoint for real-time chat with streaming
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with streaming responses."""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Send initial processing message
            processing_msg = {
                "type": "processing",
                "message": "Processing your question...",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(processing_msg), websocket)
            
            # Process the message with streaming
            await query_handler.process_query_streaming(
                query=message_data["message"],
                user_id=message_data.get("user_id", "websocket_user"),
                websocket=websocket,
                manager=manager,
                mode=message_data.get("mode", "exploration")
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Route not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,  # Fixed port to 8000
        reload=True,
        log_level="info"
    )
