from __future__ import annotations

import logging
from typing import Any

from googleapiclient.errors import HttpError
from sqlmodel import Session

from src.config import Settings
from src.integrations.youtube.client import build_youtube_service
from src.integrations.youtube.token_store import get_refresh_token

logger = logging.getLogger(__name__)


def get_connection_status(
    session: Session,
    settings: Settings,
    *,
    account_key: str = "default",
) -> dict[str, Any]:
    refresh_token = get_refresh_token(session, settings, account_key=account_key)
    if not refresh_token:
        return {"connected": False, "account_key": account_key}

    try:
        youtube = build_youtube_service(settings, refresh_token=refresh_token)
        response = (
            youtube.channels()
            .list(part="snippet", mine=True, maxResults=1)
            .execute()
        )
        items = response.get("items", [])
        channel = items[0] if items else None
        snippet = channel.get("snippet", {}) if channel else {}

        return {
            "connected": True,
            "account_key": account_key,
            "channel": {
                "id": channel.get("id") if channel else None,
                "title": snippet.get("title"),
            },
        }
    except HttpError as exc:
        logger.warning(
            "Failed to verify YouTube connection",
            extra={"account_key": account_key, "status": exc.resp.status},
        )
        return {
            "connected": False,
            "account_key": account_key,
            "error": "youtube_api_error",
            "status": getattr(exc.resp, "status", None),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "Unexpected error verifying YouTube connection",
            extra={"account_key": account_key},
        )
        return {
            "connected": False,
            "account_key": account_key,
            "error": "unexpected_error",
            "detail": str(exc),
        }
