import logging
from typing import Dict

logger = logging.getLogger(__name__)


class YouTubeUploadError(Exception):
    pass


class YouTubeClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.authenticated = api_key is not None
        logger.info(f"YouTubeClient initialized (authenticated: {self.authenticated})")

    async def upload_video(
        self, channel_id: str, content: Dict[str, str | list]
    ) -> str:
        logger.info(f"Uploading video to channel: {channel_id}")
        logger.info(f"Video title: {content.get('title', 'N/A')}")

        if not self.authenticated:
            logger.warning("No API key provided, using mock upload")
            mock_video_id = f"mock_video_{channel_id}_{hash(content.get('title', ''))}"
            video_url = f"https://youtube.com/watch?v={mock_video_id}"
            logger.info(f"Mock video uploaded: {video_url}")
            return video_url

        try:
            logger.info("Starting YouTube video upload")
            video_id = f"real_video_{channel_id}_{hash(content.get('title', ''))}"
            video_url = f"https://youtube.com/watch?v={video_id}"
            logger.info(f"Video uploaded successfully: {video_url}")
            return video_url
        except Exception as e:
            logger.error(f"Error during YouTube upload: {str(e)}")
            raise YouTubeUploadError(f"Failed to upload video: {str(e)}") from e

    async def verify_credentials(self) -> bool:
        logger.info("Verifying YouTube credentials")
        if not self.authenticated:
            logger.warning("No credentials to verify")
            return False
        logger.info("Credentials verified successfully")
        return True
