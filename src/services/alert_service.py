import logging
from typing import Dict

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(
        self,
        email_enabled: bool = False,
        webhook_url: str | None = None,
    ):
        self.email_enabled = email_enabled
        self.webhook_url = webhook_url
        has_webhook = webhook_url is not None
        logger.info(
            f"AlertService initialized (email: {email_enabled}, "
            f"webhook: {has_webhook})"
        )

    async def send_success_alert(
        self, channel_name: str, video_url: str, job_name: str
    ):
        logger.info(f"Sending success alert for job: {job_name}")
        message = (
            f"Video successfully uploaded for channel '{channel_name}': "
            f"{video_url}"
        )

        if self.email_enabled:
            await self._send_email_alert("SUCCESS", message)

        if self.webhook_url:
            await self._send_webhook_alert(
                {
                    "event": "job_success",
                    "job_name": job_name,
                    "channel": channel_name,
                    "video_url": video_url,
                    "status": "success",
                }
            )

        logger.info(f"Success alert sent for job: {job_name}")

    async def send_failure_alert(
        self, channel_name: str, error_message: str, job_name: str
    ):
        logger.info(f"Sending failure alert for job: {job_name}")
        message = f"Video upload failed for channel '{channel_name}': {error_message}"

        if self.email_enabled:
            await self._send_email_alert("FAILURE", message)

        if self.webhook_url:
            await self._send_webhook_alert(
                {
                    "event": "job_failure",
                    "job_name": job_name,
                    "channel": channel_name,
                    "error": error_message,
                    "status": "failure",
                }
            )

        logger.info(f"Failure alert sent for job: {job_name}")

    async def _send_email_alert(self, subject: str, message: str):
        logger.info(f"[EMAIL PLACEHOLDER] Subject: {subject}")
        logger.info(f"[EMAIL PLACEHOLDER] Message: {message}")

    async def _send_webhook_alert(self, payload: Dict):
        logger.info(f"[WEBHOOK PLACEHOLDER] URL: {self.webhook_url}")
        logger.info(f"[WEBHOOK PLACEHOLDER] Payload: {payload}")
