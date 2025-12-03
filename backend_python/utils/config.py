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
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    # Primary local model
    ollama_default_model: str = "llama3.1:8b-instruct"
    
    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Vector Search Configuration
    similarity_threshold: float = 0.8
    max_context_chunks: int = 5

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
    model_registry_ollama_default: str = "llama3.1:8b-instruct"
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.log_level = "DEBUG"
elif os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
    settings.log_level = "WARNING"
    settings.cors_origins = "https://yourdomain.com"  # Update for production
