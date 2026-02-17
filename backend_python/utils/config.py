"""
Configuration settings for the AI Tutor backend.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_title: str = "Ai-Tutor API"
    api_version: str = "1.0.0"
    api_description: str = "AI-powered tutoring system with vector database and real-time chat"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "development"
    
    # Database Configuration
    chroma_persist_directory: str = "./chroma_db"
    vector_db_collection_name: str = "ai_tutor_documents"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    # Default hosted model for balance
    openai_model: str = "gpt-4o-mini"
    # Premium model for rare escalations
    openai_premium_model: str = "gpt-4o"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    
    # OpenAI Embeddings Configuration
    use_openai_embeddings: bool = False  # Temporarily disabled - need to re-index documents first
    openai_embedding_model: str = "text-embedding-3-small"  # Best price/performance ($0.02/1M tokens)
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    # Primary local model
    ollama_default_model: str = "llama3.3:latest"
    
    # Document Processing
    # Optimized for academic papers and PDF slides/decks
    chunk_size: int = 1500  # Larger chunks for better context (papers: 1500-2000, slides: 1200-1500)
    chunk_overlap: int = 200  # Reduced from 250 for semantic chunking
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    use_semantic_chunking: bool = True  # Use LangChain RecursiveCharacterTextSplitter
    
    # Vector Search Configuration
    similarity_threshold: float = 2.0  # Very relaxed for better recall (cosine distance can go up to 2)
    max_context_chunks: int = 5
    
    # Advanced Retrieval Configuration
    enable_reranking: bool = True  # Enable cross-encoder reranking (local, free)
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Local reranker
    retrieval_top_k: int = 12  # Retrieve more candidates before reranking
    rerank_top_k: int = 6  # Final number after reranking
    max_context_chars: int = 4500  # Increased from 2000 for better context
    
    # Multi-Query Configuration
    enable_multi_query: bool = True  # Generate query variants for better recall
    multi_query_provider: str = "ollama"  # Use ollama for free multi-query generation
    
    # Relaxed Quality Thresholds (trust the reranker)
    good_retrieval_distance: float = 2.5  # Very relaxed - trust reranker to filter
    good_retrieval_similarity: float = 0.40  # Very relaxed - trust reranker to filter
    
    # Debug Logging Configuration
    debug_log_path: Optional[str] = None  # If None, uses .cursor/debug.log relative to project root

    # Hybrid Routing Configuration
    # Thresholds and guards used by the hybrid router
    assessment_min_conf: float = 0.72
    exploration_min_conf: float = 0.55
    min_retrieval_k: int = 2
    min_retrieval_similarity: float = 0.75
    max_history_tokens: int = 2000
    max_context_tokens: int = 3000

    # Mode Budgets and generation defaults
    assessment_max_ctx_tokens: int = 6000
    assessment_max_gen_tokens: int = 600
    assessment_temperature: float = 0.2

    exploration_max_ctx_tokens: int = 2500
    exploration_max_gen_tokens: int = 400
    exploration_temperature: float = 0.7

    # Model Registry (explicit for clarity and future extensions)
    model_registry_ollama_default: str = "llama3.3:latest"
    model_registry_openai_default: str = "gpt-4o-mini"
    model_registry_openai_premium: str = "gpt-4o"
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    
    def get_cors_origins(self) -> list:
        """Convert comma-separated CORS origins to list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    # File Upload Configuration
    upload_directory: str = "temp_uploads"
    allowed_file_types: list = [".txt", ".md", ".pdf", ".docx", ".doc"]
    
    # Course Materials Configuration
    course_materials_directory: str = "course_materials"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    rate_limit_chat: str = "60/minute"
    rate_limit_upload: str = "10/minute"
    # Prompt security: if True, reject requests when injection patterns detected
    reject_on_injection: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_debug_log_path() -> str:
    """Get the debug log file path, using configurable path or default relative path."""
    if settings.debug_log_path:
        return settings.debug_log_path
    
    # Default: use .cursor/debug.log relative to the project root
    # File is at: backend_python/utils/config.py
    # Need: project_root/.cursor/debug.log
    import os
    utils_dir = os.path.dirname(os.path.abspath(__file__))  # backend_python/utils
    backend_dir = os.path.dirname(utils_dir)  # backend_python
    project_root = os.path.dirname(backend_dir)  # project root
    return os.path.join(project_root, ".cursor", "debug.log")

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.log_level = "DEBUG"
elif os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
    settings.log_level = "WARNING"
    settings.cors_origins = "https://yourdomain.com"  # Update for production
