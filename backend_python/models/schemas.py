"""
Pydantic Models and Schemas
Data models for API requests and responses.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message or question", max_length=2000)
    user_id: Optional[str] = Field(None, description="Unique user identifier", max_length=50)
    conversation_history: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Previous conversation context",
        max_length=20,
    )
    mode: Optional[str] = Field("exploration", description="Learning mode: 'exploration' or 'assessment'", max_length=20)

    @field_validator("conversation_history")
    @classmethod
    def conversation_history_max_items(cls, v: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        if v is not None and len(v) > 20:
            raise ValueError("conversation_history must contain at most 20 entries")
        return v

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI tutor's response")
    query: str = Field(..., description="Original user query")
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: str = Field(..., description="Response timestamp")
    context_chunks_used: int = Field(0, description="Number of context chunks used")
    status: str = Field(..., description="Response status")
    # Optional routing metadata
    llm_provider: Optional[str] = Field(None, description="Provider used (openai/ollama/mock)")
    llm_model: Optional[str] = Field(None, description="Model used")
    confidence: Optional[float] = Field(None, description="Self-check confidence score")
    escalated: Optional[bool] = Field(None, description="Whether escalation occurred")
    # Enhanced tutor metadata
    citations: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of sources used with optional title, url, and score"
    )
    tldr: Optional[str] = Field(None, description="Short summary of the answer")

class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    message: str = Field(..., description="Upload status message")
    filename: str = Field(..., description="Name of uploaded file")
    chunks_created: int = Field(0, description="Number of chunks created")
    status: str = Field(..., description="Upload status")

class FileUploadResult(BaseModel):
    """Result for a single file upload."""
    filename: str = Field(..., description="Name of uploaded file")
    chunks_created: int = Field(0, description="Number of chunks created")
    status: str = Field(..., description="Upload status (success/error)")
    error: Optional[str] = Field(None, description="Error message if status is error")

class MultipleUploadResponse(BaseModel):
    """Response model for multiple file upload endpoint."""
    message: str = Field(..., description="Overall status message")
    total_files: int = Field(..., description="Total number of files processed")
    successful: int = Field(..., description="Number of successfully uploaded files")
    failed: int = Field(..., description="Number of failed uploads")
    results: List[FileUploadResult] = Field(..., description="Individual file upload results")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Overall health status")
    timestamp: str = Field(..., description="Health check timestamp")
    services: Dict[str, str] = Field(..., description="Individual service statuses")

class DocumentInfo(BaseModel):
    """Model for document information."""
    filename: str = Field(..., description="Document filename")
    file_type: str = Field(..., description="File type/extension")
    chunk_count: int = Field(..., description="Number of chunks")
    total_size: int = Field(..., description="Total document size")

class ChunkInfo(BaseModel):
    """Model for document chunk information."""
    text: str = Field(..., description="Chunk text content")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")
    id: Optional[str] = Field(None, description="Chunk unique identifier")
    distance: Optional[float] = Field(None, description="Similarity distance")

class ConversationEntry(BaseModel):
    """Model for conversation history entry."""
    message: str = Field(..., description="Message content")
    role: str = Field(..., description="Message role (user/assistant)")
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: str = Field(..., description="Message timestamp")

class LearningSuggestion(BaseModel):
    """Model for learning suggestions."""
    suggestion: str = Field(..., description="Learning suggestion text")
    category: str = Field(..., description="Suggestion category")
    priority: int = Field(1, description="Suggestion priority (1-5)")

class WebSocketMessage(BaseModel):
    """Model for WebSocket messages."""
    type: str = Field(..., description="Message type")
    message: str = Field(..., description="Message content")
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: Optional[str] = Field(None, description="Message timestamp")

class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class SearchRequest(BaseModel):
    """Request model for document search."""
    query: str = Field(..., description="Search query")
    n_results: int = Field(5, description="Number of results to return")
    filter_metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Metadata filters"
    )

class SearchResponse(BaseModel):
    """Response model for document search."""
    results: List[ChunkInfo] = Field(..., description="Search results")
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of results")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
