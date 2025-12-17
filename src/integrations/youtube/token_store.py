from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from src.config import Settings
from src.integrations.youtube.crypto import decrypt_refresh_token, encrypt_refresh_token
from src.models import YouTubeOAuthToken


def _token_stmt(account_key: str):
    return select(YouTubeOAuthToken).where(
        YouTubeOAuthToken.account_key == account_key
    )


def get_refresh_token(
    session: Session,
    settings: Settings,
    *,
    account_key: str = "default",
) -> str | None:
    token_row = session.exec(_token_stmt(account_key)).first()
    if not token_row:
        return None
    return decrypt_refresh_token(settings, token_row.encrypted_refresh_token)


def upsert_refresh_token(
    session: Session,
    settings: Settings,
    *,
    refresh_token: str,
    scopes: list[str] | None = None,
    account_key: str = "default",
) -> YouTubeOAuthToken:
    encrypted = encrypt_refresh_token(settings, refresh_token)
    scopes_value = ",".join(scopes) if scopes else None

    token_row = session.exec(_token_stmt(account_key)).first()

    if token_row:
        token_row.encrypted_refresh_token = encrypted
        token_row.scopes = scopes_value
        token_row.updated_at = datetime.utcnow()
    else:
        token_row = YouTubeOAuthToken(
            account_key=account_key,
            encrypted_refresh_token=encrypted,
            scopes=scopes_value,
        )
        session.add(token_row)

    session.commit()
    session.refresh(token_row)
    return token_row


def delete_refresh_token(session: Session, *, account_key: str = "default") -> bool:
    token_row = session.exec(_token_stmt(account_key)).first()
    if not token_row:
        return False

    session.delete(token_row)
    session.commit()
    return True
