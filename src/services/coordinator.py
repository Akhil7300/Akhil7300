import logging
from datetime import datetime

from sqlmodel import Session, select

from src.config import get_settings
from src.database import engine
from src.models import ChannelConfig, ContentConfig, JobRunHistory, SchedulePreference
from src.services.ai_generator import AIGenerationError, AIGenerator
from src.services.alert_service import AlertService
from src.services.youtube_client import YouTubeClient, YouTubeUploadError

logger = logging.getLogger(__name__)
settings = get_settings()


class CoordinatorService:
    def __init__(self):
        self.ai_generator = AIGenerator(
            api_key=settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY
        )
        self.youtube_client = YouTubeClient(api_key=settings.YOUTUBE_API_KEY)
        self.alert_service = AlertService()
        logger.info("CoordinatorService initialized")

    async def execute_upload_job(self, channel_id: int):
        job_name = f"upload_job_channel_{channel_id}"
        logger.info(f"Starting job: {job_name}")

        with Session(engine) as session:
            job_history = JobRunHistory(
                job_name=job_name,
                channel_id=channel_id,
                status="running",
                start_time=datetime.utcnow(),
            )
            session.add(job_history)
            session.commit()
            session.refresh(job_history)
            job_history_id = job_history.id

        try:
            channel_config = await self._get_channel_config(channel_id)
            if not channel_config:
                error_msg = f"Channel config not found for channel_id: {channel_id}"
                raise ValueError(error_msg)

            content_config = await self._get_content_config(channel_id)

            logger.info(
                f"Generating content for channel: {channel_config.channel_name}"
            )
            template = content_config.content_template if content_config else None
            content = await self.ai_generator.generate_content(
                channel_name=channel_config.channel_name,
                content_template=template,
            )

            logger.info(f"Uploading video for channel: {channel_config.channel_name}")
            video_url = await self.youtube_client.upload_video(
                channel_id=channel_config.channel_id, content=content
            )

            details = f"Successfully uploaded video: {content.get('title')}"
            await self._update_job_success(job_history_id, video_url, details)

            await self.alert_service.send_success_alert(
                channel_name=channel_config.channel_name,
                video_url=video_url,
                job_name=job_name,
            )

            await self._update_next_run(channel_id)

            logger.info(f"Job completed successfully: {job_name}")

        except (AIGenerationError, YouTubeUploadError, ValueError) as e:
            error_message = f"Job failed: {str(e)}"
            logger.error(error_message, exc_info=True)
            await self._update_job_failure(job_history_id, error_message)

            channel_config = await self._get_channel_config(channel_id)
            if channel_config:
                await self.alert_service.send_failure_alert(
                    channel_name=channel_config.channel_name,
                    error_message=error_message,
                    job_name=job_name,
                )
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(error_message, exc_info=True)
            await self._update_job_failure(job_history_id, error_message)

    async def _get_channel_config(self, channel_id: int) -> ChannelConfig | None:
        with Session(engine) as session:
            statement = select(ChannelConfig).where(ChannelConfig.id == channel_id)
            return session.exec(statement).first()

    async def _get_content_config(self, channel_id: int) -> ContentConfig | None:
        with Session(engine) as session:
            statement = select(ContentConfig).where(
                ContentConfig.channel_id == channel_id
            )
            return session.exec(statement).first()

    async def _update_job_success(
        self, job_history_id: int, video_url: str, details: str
    ):
        with Session(engine) as session:
            statement = select(JobRunHistory).where(JobRunHistory.id == job_history_id)
            job_history = session.exec(statement).first()
            if job_history:
                job_history.status = "success"
                job_history.end_time = datetime.utcnow()
                job_history.video_url = video_url
                job_history.details = details
                session.add(job_history)
                session.commit()
                logger.info(f"Job history updated: {job_history_id} - success")

    async def _update_job_failure(self, job_history_id: int, error_message: str):
        with Session(engine) as session:
            statement = select(JobRunHistory).where(JobRunHistory.id == job_history_id)
            job_history = session.exec(statement).first()
            if job_history:
                job_history.status = "failure"
                job_history.end_time = datetime.utcnow()
                job_history.error_message = error_message
                session.add(job_history)
                session.commit()
                logger.info(f"Job history updated: {job_history_id} - failure")

    async def _update_next_run(self, channel_id: int):
        with Session(engine) as session:
            statement = select(SchedulePreference).where(
                SchedulePreference.channel_id == channel_id
            )
            schedule = session.exec(statement).first()
            if schedule:
                from src.services.scheduler_manager import calculate_next_run

                schedule.next_run = calculate_next_run(
                    schedule.frequency, schedule.preferred_time, schedule.timezone
                )
                session.add(schedule)
                session.commit()
                logger.info(
                    f"Next run updated for channel {channel_id}: "
                    f"{schedule.next_run}"
                )


coordinator_service = CoordinatorService()
