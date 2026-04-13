"""
Application configuration using Pydantic Settings.

Loads all configuration from environment variables with sensible defaults.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "NovelAI Forge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"
    DATABASE_ECHO: bool = False
    
    # Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    GROK_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    QWEN_EMAIL: Optional[str] = None
    QWEN_PASSWORD: Optional[str] = None
    
    # AI Defaults
    DEFAULT_AI_MODEL: str = "gpt-4o"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 4000
    
    # Paths
    PROMPTS_DIR: str = "backend/prompts"
    EXPORT_DIR: str = "exports"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings()
