from __future__ import annotations

from cryptography.fernet import Fernet

from src.config import Settings


def _get_fernet(settings: Settings) -> Fernet:
    if not settings.YOUTUBE_TOKEN_ENCRYPTION_KEY:
        raise ValueError("YOUTUBE_TOKEN_ENCRYPTION_KEY is not set")
    return Fernet(settings.YOUTUBE_TOKEN_ENCRYPTION_KEY)


def encrypt_refresh_token(settings: Settings, refresh_token: str) -> str:
    fernet = _get_fernet(settings)
    return fernet.encrypt(refresh_token.encode("utf-8")).decode("utf-8")


def decrypt_refresh_token(settings: Settings, encrypted_refresh_token: str) -> str:
    fernet = _get_fernet(settings)
    return fernet.decrypt(encrypted_refresh_token.encode("utf-8")).decode("utf-8")
