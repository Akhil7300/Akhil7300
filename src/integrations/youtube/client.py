from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.config import Settings

YOUTUBE_SCOPES: list[str] = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def load_client_config(settings: Settings) -> dict[str, Any]:
    if settings.YOUTUBE_OAUTH_CLIENT_SECRETS_JSON:
        return json.loads(settings.YOUTUBE_OAUTH_CLIENT_SECRETS_JSON)

    if settings.YOUTUBE_OAUTH_CLIENT_SECRETS_FILE:
        path = Path(settings.YOUTUBE_OAUTH_CLIENT_SECRETS_FILE)
        return json.loads(path.read_text(encoding="utf-8"))

    raise ValueError(
        "Set YOUTUBE_OAUTH_CLIENT_SECRETS_JSON or YOUTUBE_OAUTH_CLIENT_SECRETS_FILE"
    )


def _extract_client_section(client_config: dict[str, Any]) -> dict[str, Any]:
    section = client_config.get("installed") or client_config.get("web")
    if not isinstance(section, dict):
        raise ValueError("Invalid client secrets JSON (expected 'installed' or 'web')")
    return section


def build_credentials_from_refresh_token(
    settings: Settings,
    *,
    refresh_token: str,
    scopes: list[str] | None = None,
) -> Credentials:
    client_config = load_client_config(settings)
    section = _extract_client_section(client_config)

    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=section.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=section["client_id"],
        client_secret=section["client_secret"],
        scopes=scopes or YOUTUBE_SCOPES,
    )


def build_youtube_service(settings: Settings, *, refresh_token: str):
    credentials = build_credentials_from_refresh_token(
        settings, refresh_token=refresh_token, scopes=YOUTUBE_SCOPES
    )

    return build("youtube", "v3", credentials=credentials, cache_discovery=False)
