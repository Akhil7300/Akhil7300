import pytest

from src.services.youtube_client import YouTubeClient


@pytest.mark.asyncio
async def test_upload_video_without_api_key():
    client = YouTubeClient(api_key=None)
    content = {
        "title": "Test Video",
        "description": "Test Description",
        "script": "Test Script",
        "tags": ["test"],
    }

    video_url = await client.upload_video("test_channel_123", content)

    assert video_url.startswith("https://youtube.com/watch?v=")
    assert "mock_video" in video_url


@pytest.mark.asyncio
async def test_upload_video_with_api_key():
    client = YouTubeClient(api_key="test_key")
    content = {
        "title": "Test Video",
        "description": "Test Description",
    }

    video_url = await client.upload_video("test_channel_123", content)

    assert video_url.startswith("https://youtube.com/watch?v=")


@pytest.mark.asyncio
async def test_verify_credentials_without_key():
    client = YouTubeClient(api_key=None)
    result = await client.verify_credentials()

    assert result is False


@pytest.mark.asyncio
async def test_verify_credentials_with_key():
    client = YouTubeClient(api_key="test_key")
    result = await client.verify_credentials()

    assert result is True


def test_youtube_client_authentication():
    client_unauthenticated = YouTubeClient(api_key=None)
    client_authenticated = YouTubeClient(api_key="test_key")

    assert client_unauthenticated.authenticated is False
    assert client_authenticated.authenticated is True
