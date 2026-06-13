"""
Configuration Management
Loads and validates environment variables at startup using pydantic-settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Required settings - will fail fast if missing
    OPENAI_API_KEY: str
    DATABASE_URL: str
    
    # Environment
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Document limits
    MAX_DOCUMENTS: int = 20
    
    # Chunking settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # AI models
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.0
    
    # Retrieval settings
    TOP_K_RESULTS: int = 5
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    
    # Mock mode for demo/testing without API calls
    USE_MOCK_LLM: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
