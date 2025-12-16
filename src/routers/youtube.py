import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.config import get_settings
from src.database import get_session
from src.integrations.youtube.exceptions import YouTubeAuthError
from src.integrations.youtube.oauth import get_authorization_url, handle_oauth_callback
from src.integrations.youtube.status import get_connection_status
from src.integrations.youtube.token_store import delete_refresh_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/youtube", tags=["youtube"])


@router.get("/auth-url")
def youtube_auth_url(account_key: str = "default"):
    settings = get_settings()
    try:
        return get_authorization_url(settings, account_key=account_key)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to create YouTube authorization URL")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/callback")
def youtube_oauth_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    session: Session = Depends(get_session),
):
    if error:
        raise HTTPException(status_code=400, detail={"error": error})
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing 'code' or 'state'")

    settings = get_settings()

    try:
        result = handle_oauth_callback(session, settings, code=code, state=state)
        status = get_connection_status(
            session, settings, account_key=result.get("account_key", "default")
        )
        return {"ok": True, **status}
    except YouTubeAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("YouTube OAuth callback failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/status")
def youtube_status(
    account_key: str = "default",
    session: Session = Depends(get_session),
):
    settings = get_settings()
    return get_connection_status(session, settings, account_key=account_key)


@router.delete("/token")
def youtube_disconnect(
    account_key: str = "default",
    session: Session = Depends(get_session),
):
    deleted = delete_refresh_token(session, account_key=account_key)
    return {"deleted": deleted, "account_key": account_key}
