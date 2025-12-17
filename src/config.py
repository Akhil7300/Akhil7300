from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Backend API"
    ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./backend.db"

    # AI Credentials
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # YouTube Credentials
    YOUTUBE_API_KEY: str | None = None

    # YouTube OAuth (recommended over API key for uploads)
    # Provide either a client secrets file path or the JSON payload.
    YOUTUBE_OAUTH_CLIENT_SECRETS_FILE: str | None = None
    YOUTUBE_OAUTH_CLIENT_SECRETS_JSON: str | None = None
    YOUTUBE_OAUTH_REDIRECT_URI: str = "http://localhost:8000/youtube/callback"

    # Used to encrypt refresh tokens stored in the database (Fernet key)
    YOUTUBE_TOKEN_ENCRYPTION_KEY: str | None = None

    # Optional: used to sign/verify OAuth state
    YOUTUBE_OAUTH_STATE_SECRET: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings():
    return Settings()
