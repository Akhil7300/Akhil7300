import pytest

from src.services.alert_service import AlertService


@pytest.mark.asyncio
async def test_send_success_alert():
    service = AlertService(email_enabled=True, webhook_url="https://example.com/webhook")

    await service.send_success_alert(
        channel_name="Test Channel",
        video_url="https://youtube.com/watch?v=test123",
        job_name="test_job",
    )


@pytest.mark.asyncio
async def test_send_failure_alert():
    service = AlertService(email_enabled=True, webhook_url="https://example.com/webhook")

    await service.send_failure_alert(
        channel_name="Test Channel",
        error_message="Test error message",
        job_name="test_job",
    )


@pytest.mark.asyncio
async def test_alert_service_without_email():
    service = AlertService(email_enabled=False, webhook_url=None)

    await service.send_success_alert(
        channel_name="Test Channel",
        video_url="https://youtube.com/watch?v=test123",
        job_name="test_job",
    )


def test_alert_service_initialization():
    service = AlertService(email_enabled=True, webhook_url="https://example.com/webhook")

    assert service.email_enabled is True
    assert service.webhook_url == "https://example.com/webhook"
