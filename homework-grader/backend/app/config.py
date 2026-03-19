"""
Configuration module for the AI Homework Grading System.
Loads environment variables and provides application settings.
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


def find_env_file():
    """Find .env file, always preferring the homework-grader project's own .env."""
    # Always try the absolute path to the homework-grader project root first.
    # This works regardless of the current working directory, which is important
    # when this module is imported as a sub-application from the AI-Tutor project.
    project_root = Path(__file__).parent.parent.parent  # .../homework-grader/
    grader_env = project_root / ".env"
    if grader_env.exists():
        return str(grader_env)
    # Fallbacks for standalone operation
    if os.path.exists(".env"):
        return ".env"
    if os.path.exists("../.env"):
        return "../.env"
    return ".env"  # Default fallback


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    app_name: str = "AI Homework Grading System"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # =============================================================================
    # API SETTINGS
    # =============================================================================
    api_version: str = Field(default="v1", env="API_VERSION")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:8501,http://localhost:3000",
        env="CORS_ORIGINS"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins as list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins
    
    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    database_url: str = Field(
        default="postgresql://keyursavalia:@localhost:5432/homework_grading_system",
        env="DATABASE_URL"
    )
    db_echo: bool = Field(default=False, env="SHOW_SQL")
    
    # Alternative DB settings
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="homework_grading_system", env="DB_NAME")
    db_user: str = Field(default="keyursavalia", env="DB_USER")
    db_password: str = Field(default="", env="DB_PASSWORD")
    
    # =============================================================================
    # GEMINI API SETTINGS
    # =============================================================================
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-pro", env="GEMINI_MODEL")
    llm_temperature: float = Field(default=0.3, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2048, env="LLM_MAX_TOKENS")
    
    # =============================================================================
    # CHROMADB SETTINGS
    # =============================================================================
    chroma_persist_directory: str = Field(
        default="./data/chroma_db",
        env="CHROMA_PERSIST_DIRECTORY"
    )
    chroma_collection_name: str = Field(
        default="course_materials",
        env="CHROMA_COLLECTION_NAME"
    )
    
    # =============================================================================
    # FILE UPLOAD SETTINGS
    # =============================================================================
    max_upload_size_mb: int = Field(default=50, env="MAX_UPLOAD_SIZE_MB")
    allowed_extensions: str = Field(
        default=".pdf,.txt,.doc,.docx",
        env="ALLOWED_EXTENSIONS"
    )
    materials_upload_dir: str = Field(
        default="./data/uploads/materials",
        env="MATERIALS_UPLOAD_DIR"
    )
    submissions_upload_dir: str = Field(
        default="./data/uploads/submissions",
        env="SUBMISSIONS_UPLOAD_DIR"
    )
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions as list."""
        if isinstance(self.allowed_extensions, str):
            return [ext.strip() for ext in self.allowed_extensions.split(",")]
        return self.allowed_extensions
    
    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./data/logs/app.log", env="LOG_FILE")
    
    # =============================================================================
    # DOCUMENT PROCESSING SETTINGS
    # =============================================================================
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # =============================================================================
    # GRADING SETTINGS
    # =============================================================================
    default_max_score: int = Field(default=100, env="DEFAULT_MAX_SCORE")
    
    # =============================================================================
    # SECURITY SETTINGS (Future)
    # =============================================================================
    secret_key: Optional[str] = Field(default=None, env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # =============================================================================
    # ABSOLUTE PATH HELPERS
    # These resolve relative config paths against the homework-grader project root
    # so that the subsystem works correctly regardless of the working directory
    # (e.g. when mounted inside the AI-Tutor application).
    # =============================================================================

    @property
    def _project_root(self) -> Path:
        """Absolute path to the homework-grader project root directory."""
        return Path(__file__).parent.parent.parent

    def _abs(self, rel_or_abs: str) -> str:
        """Return an absolute version of rel_or_abs resolved from the project root."""
        p = Path(rel_or_abs)
        return str(p if p.is_absolute() else self._project_root / p)

    @property
    def chroma_persist_directory_abs(self) -> str:
        return self._abs(self.chroma_persist_directory)

    @property
    def materials_upload_dir_abs(self) -> str:
        return self._abs(self.materials_upload_dir)

    @property
    def submissions_upload_dir_abs(self) -> str:
        return self._abs(self.submissions_upload_dir)

    @property
    def log_file_abs(self) -> str:
        return self._abs(self.log_file)

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert max upload size from MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reloading .env file on every call.
    """
    return Settings()


# Convenience instance for direct import
settings = get_settings()
