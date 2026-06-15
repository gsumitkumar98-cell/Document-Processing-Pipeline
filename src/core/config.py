from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache
from pathlib import Path
from typing import Literal


class Settings(BaseSettings):
    """
    Application configuration with validation.
    
    All settings can be overridden via environment variables.
    Validates constraints on numeric values and path existence.
    
    Configuration:
    - APP_NAME: Application display name
    - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - CHUNK_SIZE: Number of words per document chunk (must be 1-10000)
    - MAX_RESULTS: Maximum search results to return (must be 1-1000)
    - DOCUMENT_PATH: Path to document directory (relative or absolute)
    
    Environment Variables:
    - Set any field via env var (e.g., CHUNK_SIZE=100)
    - Loads from .env file if present
    """

    APP_NAME: str = Field(
        default="Document Processing Pipeline",
        description="Application display name"
    )

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level for application"
    )

    CHUNK_SIZE: int = Field(
        default=50,
        ge=1,
        le=10000,
        description="Number of words per document chunk (1-10000)"
    )

    MAX_RESULTS: int = Field(
        default=5,
        ge=1,
        le=1000,
        description="Maximum number of search results to return (1-1000)"
    )

    DOCUMENT_PATH: Path = Field(
        default=Path("documents"),
        description="Path to document directory (relative or absolute)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("DOCUMENT_PATH", mode="before")
    @classmethod
    def validate_document_path(cls, value) -> Path:
        """
        Convert string path to Path object and validate basic format.
        
        Note: Does not check existence at validation time to allow
        creating the directory after config initialization.
        """
        if isinstance(value, str):
            return Path(value)
        if isinstance(value, Path):
            return value
        raise ValueError(f"DOCUMENT_PATH must be string or Path, got {type(value).__name__}")

    @field_validator("CHUNK_SIZE")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        """Ensure chunk size is positive and reasonable."""
        if value <= 0:
            raise ValueError("CHUNK_SIZE must be positive")
        if value > 10000:
            raise ValueError("CHUNK_SIZE too large (max 10000)")
        return value

    @field_validator("MAX_RESULTS")
    @classmethod
    def validate_max_results(cls, value: int) -> int:
        """Ensure max results is positive and reasonable."""
        if value <= 0:
            raise ValueError("MAX_RESULTS must be positive")
        if value > 1000:
            raise ValueError("MAX_RESULTS too large (max 1000)")
        return value


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses LRU cache to ensure single instance across application.
    For testing, clear cache with get_settings.cache_clear().
    
    Returns:
        Validated Settings instance
    """
    return Settings()


# Module-level settings for convenience
# For tests that need to override settings, use get_settings.cache_clear()
# and set environment variables before calling get_settings() again
settings = get_settings()