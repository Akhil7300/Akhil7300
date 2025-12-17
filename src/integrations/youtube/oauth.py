from __future__ import annotations

import base64
import hmac
import json
import logging
import time
from hashlib import sha256
from typing import Any

from google_auth_oauthlib.flow import Flow
from sqlmodel import Session

from src.config import Settings
from src.integrations.youtube.client import YOUTUBE_SCOPES, load_client_config
from src.integrations.youtube.exceptions import YouTubeAuthError
from src.integrations.youtube.token_store import get_refresh_token, upsert_refresh_token

logger = logging.getLogger(__name__)


def _sign_state(secret: str, payload_b64: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"), payload_b64.encode("utf-8"), sha256
    ).hexdigest()
    return digest


def create_oauth_state(settings: Settings, *, account_key: str) -> str:
    payload = {"account_key": account_key, "ts": int(time.time())}
    payload_json = json.dumps(payload).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8")

    if not settings.YOUTUBE_OAUTH_STATE_SECRET:
        return payload_b64

    signature = _sign_state(settings.YOUTUBE_OAUTH_STATE_SECRET, payload_b64)
    return f"{payload_b64}.{signature}"


def parse_oauth_state(settings: Settings, state: str) -> dict[str, Any]:
    if "." in state:
        payload_b64, signature = state.split(".", 1)
    else:
        payload_b64, signature = state, None

    if settings.YOUTUBE_OAUTH_STATE_SECRET:
        if not signature:
            raise YouTubeAuthError("Missing OAuth state signature")

        expected = _sign_state(settings.YOUTUBE_OAUTH_STATE_SECRET, payload_b64)
        if not hmac.compare_digest(signature, expected):
            raise YouTubeAuthError("Invalid OAuth state signature")

    try:
        raw = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
        payload = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        raise YouTubeAuthError("Malformed OAuth state") from exc

    ts = payload.get("ts")
    if isinstance(ts, int) and ts < int(time.time()) - 60 * 60 * 24:
        raise YouTubeAuthError("OAuth state expired")

    return payload


def _build_flow(settings: Settings) -> Flow:
    client_config = load_client_config(settings)
    return Flow.from_client_config(
        client_config,
        scopes=YOUTUBE_SCOPES,
        redirect_uri=settings.YOUTUBE_OAUTH_REDIRECT_URI,
    )


def get_authorization_url(
    settings: Settings,
    *,
    account_key: str = "default",
) -> dict[str, str]:
    flow = _build_flow(settings)
    state = create_oauth_state(settings, account_key=account_key)

    url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )

    return {"authorization_url": url, "state": state}


def handle_oauth_callback(
    session: Session,
    settings: Settings,
    *,
    code: str,
    state: str,
) -> dict[str, Any]:
    payload = parse_oauth_state(settings, state)
    account_key = payload.get("account_key") or "default"

    flow = _build_flow(settings)

    flow.fetch_token(code=code)
    credentials = flow.credentials

    refresh_token = credentials.refresh_token
    if not refresh_token:
        existing = get_refresh_token(session, settings, account_key=account_key)
        if not existing:
            raise YouTubeAuthError(
                "Google did not return a refresh_token. "
                "Re-run the flow with prompt=consent and access_type=offline."
            )
        refresh_token = existing

    upsert_refresh_token(
        session,
        settings,
        refresh_token=refresh_token,
        scopes=list(credentials.scopes or []),
        account_key=account_key,
    )

    logger.info("Stored YouTube refresh token", extra={"account_key": account_key})

    return {"account_key": account_key}
