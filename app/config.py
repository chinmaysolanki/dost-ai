from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database settings
    database_url: str = "sqlite:///./dost.db"
    
    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    
    # Voice processing settings
    whisper_model: str = "whisper-1"
    tts_voice: str = "alloy"
    
    # Redis settings for caching and sessions
    redis_url: str = "redis://localhost:6379"
    
    # Security settings
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30
    
    # Application settings
    app_name: str = "DOST - AI Assistant"
    debug: bool = True
    
    # Google Calendar API settings
    google_calendar_credentials_file: Optional[str] = None
    google_calendar_token_file: Optional[str] = None
    
    # Voice processing settings
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    max_audio_duration: int = 300  # 5 minutes
    
    # AI Brain settings
    max_context_length: int = 4000
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Learning system settings
    learning_rate: float = 0.1
    memory_retention_days: int = 90
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_folder: str = "uploads"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

# Create upload directory if it doesn't exist
settings = get_settings()
os.makedirs(settings.upload_folder, exist_ok=True) 