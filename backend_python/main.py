"""
Ai-Tutor FastAPI Backend
Main application entry point with all API routes and WebSocket support.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from services.query_handler import QueryHandler
from services.document_chunker import DocumentChunker
from services.vector_db import VectorDatabase
from models.schemas import ChatRequest, ChatResponse, UploadResponse, HealthResponse
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
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
query_handler = QueryHandler()
document_chunker = DocumentChunker()
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
        # Process query through the query handler
        result = await query_handler.process_query(
            query=request.message,
            user_id=request.user_id,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            response=result["response"],
            query=request.message,
            user_id=request.user_id,
            timestamp=result["timestamp"],
            context_chunks_used=result.get("context_chunks_used", 0),
            status=result["status"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process documents for vector database."""
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
        os.remove(file_path)
        
        return UploadResponse(
            message=f"Successfully processed {file.filename}",
            filename=file.filename,
            chunks_created=len(chunks),
            status="success"
        )
        
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
            conversation_history=request.conversation_history
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
                manager=manager
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
        port=8001,
        reload=True,
        log_level="info"
    )
