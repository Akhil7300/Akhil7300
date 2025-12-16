from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Backend API"
    ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./backend.db"
    
    # Admin Dashboard Authentication
    ADMIN_API_KEY: str = "change-me-in-production"
    
    # AI Credentials
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    
    # YouTube Credentials
    YOUTUBE_API_KEY: str | None = None
    YOUTUBE_CLIENT_ID: str | None = None
    YOUTUBE_CLIENT_SECRET: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings():
    return Settings()
