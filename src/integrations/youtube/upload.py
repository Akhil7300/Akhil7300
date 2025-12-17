from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from src.integrations.youtube.exceptions import (
    YouTubeQuotaExceededError,
    YouTubeUploadError,
)

logger = logging.getLogger(__name__)

PrivacyStatus = Literal["private", "public", "unlisted"]


@dataclass(frozen=True)
class YouTubeVideoMetadata:
    title: str
    description: str | None = None
    tags: list[str] | None = None
    category_id: str | None = None
    default_language: str | None = None


def _to_rfc3339(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.isoformat().replace("+00:00", "Z")


def _parse_http_error_reason(exc: HttpError) -> str | None:
    content: Any = getattr(exc, "content", None)
    if not content:
        return None

    try:
        if isinstance(content, (bytes, bytearray)):
            payload = json.loads(content.decode("utf-8"))
        elif isinstance(content, str):
            payload = json.loads(content)
        else:
            return None

        errors = payload.get("error", {}).get("errors")
        if isinstance(errors, list) and errors:
            reason = errors[0].get("reason")
            if isinstance(reason, str):
                return reason
    except Exception:  # noqa: BLE001
        return None

    return None


def _is_quota_error(exc: HttpError) -> bool:
    if getattr(exc.resp, "status", None) != 403:
        return False
    return _parse_http_error_reason(exc) in {
        "quotaExceeded",
        "dailyLimitExceeded",
    }


def _is_retriable_error(exc: HttpError) -> bool:
    status = getattr(exc.resp, "status", None)
    if status in {500, 502, 503, 504}:
        return True

    if status == 403:
        return _parse_http_error_reason(exc) in {
            "rateLimitExceeded",
            "userRateLimitExceeded",
        }

    return False


def _sleep_backoff(attempt: int) -> None:
    delay = min(2**attempt, 60)
    time.sleep(delay)


def _execute_with_retries(request, *, max_retries: int = 5):
    attempt = 0
    while True:
        try:
            return request.execute()
        except HttpError as exc:
            if _is_quota_error(exc):
                raise YouTubeQuotaExceededError(str(exc)) from exc

            if attempt >= max_retries or not _is_retriable_error(exc):
                raise YouTubeUploadError(str(exc)) from exc

            reason = _parse_http_error_reason(exc)
            logger.warning(
                "Retrying YouTube API call",
                extra={
                    "attempt": attempt + 1,
                    "status": getattr(exc.resp, "status", None),
                    "reason": reason,
                },
            )
            _sleep_backoff(attempt)
            attempt += 1


def _resumable_upload(request, *, max_retries: int = 8) -> dict[str, Any]:
    response = None
    attempt = 0

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                logger.info(
                    "YouTube upload progress",
                    extra={"progress": round(status.progress() * 100, 2)},
                )
        except HttpError as exc:
            if _is_quota_error(exc):
                raise YouTubeQuotaExceededError(str(exc)) from exc

            if attempt >= max_retries or not _is_retriable_error(exc):
                raise YouTubeUploadError(str(exc)) from exc

            reason = _parse_http_error_reason(exc)
            logger.warning(
                "Retrying YouTube resumable upload",
                extra={
                    "attempt": attempt + 1,
                    "status": getattr(exc.resp, "status", None),
                    "reason": reason,
                },
            )
            _sleep_backoff(attempt)
            attempt += 1

    if not isinstance(response, dict):
        raise YouTubeUploadError("Unexpected YouTube upload response")

    return response


def upload_video(
    youtube,
    *,
    video_path: str | Path,
    metadata: YouTubeVideoMetadata,
    privacy_status: PrivacyStatus = "private",
    publish_at: datetime | None = None,
    thumbnail_path: str | Path | None = None,
    captions_path: str | Path | None = None,
    captions_language: str = "en",
) -> str:
    video_path = Path(video_path)

    status: dict[str, Any] = {"privacyStatus": privacy_status}
    if publish_at:
        if privacy_status != "private":
            logger.info(
                "Overriding privacyStatus to 'private' for scheduled publish",
                extra={"requested_privacy": privacy_status},
            )
            status["privacyStatus"] = "private"
        status["publishAt"] = _to_rfc3339(publish_at)

    snippet: dict[str, Any] = {"title": metadata.title}
    if metadata.description is not None:
        snippet["description"] = metadata.description
    if metadata.tags:
        snippet["tags"] = metadata.tags
    if metadata.category_id:
        snippet["categoryId"] = metadata.category_id
    if metadata.default_language:
        snippet["defaultLanguage"] = metadata.default_language

    body = {
        "snippet": snippet,
        "status": status,
    }

    media = MediaFileUpload(
        str(video_path),
        resumable=True,
        mimetype="video/*",
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )
    response = _resumable_upload(request)

    video_id = response.get("id")
    if not isinstance(video_id, str) or not video_id:
        raise YouTubeUploadError("Upload succeeded but no video ID returned")

    logger.info("Uploaded YouTube video", extra={"video_id": video_id})

    if thumbnail_path:
        thumbnail_path = Path(thumbnail_path)
        thumb_media = MediaFileUpload(str(thumbnail_path), mimetype="image/*")
        thumb_request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=thumb_media,
        )
        thumb_response = _execute_with_retries(thumb_request)
        logger.info(
            "Uploaded YouTube thumbnail",
            extra={"video_id": video_id, "response": thumb_response},
        )

    if captions_path:
        captions_path = Path(captions_path)
        cap_media = MediaFileUpload(str(captions_path))
        cap_body = {
            "snippet": {
                "videoId": video_id,
                "language": captions_language,
                "name": "captions",
                "isDraft": False,
            }
        }
        cap_request = youtube.captions().insert(
            part="snippet", body=cap_body, media_body=cap_media
        )
        cap_response = _execute_with_retries(cap_request)
        logger.info(
            "Uploaded YouTube captions",
            extra={"video_id": video_id, "response": cap_response},
        )

    return video_id
