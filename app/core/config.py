import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Server settings
    PORT: int = int(os.getenv("PORT", "5175"))
    
    # STT settings
    WHISPER_API_KEY: Optional[str] = os.getenv("WHISPER_API_KEY")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "whisper-1")
    WHISPER_PROVIDER: str = os.getenv("WHISPER_PROVIDER", "openai")  # "openai" or "local"
    WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "float32")  # For faster-whisper: float32, float16, int8
    
    # LLM settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/saywrite_db")
    ALEMBIC_DATABASE_URL: Optional[str] = os.getenv("ALEMBIC_DATABASE_URL")
    
    # Authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "your-refresh-secret-key-change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Misc settings
    ENABLE_REDACTION: bool = os.getenv("ENABLE_REDACTION", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
