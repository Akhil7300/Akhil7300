from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.models import ChannelConfig, ContentConfig, JobRunHistory, SchedulePreference
from src.services.coordinator import CoordinatorService


@pytest.fixture(scope="function")
def test_db_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def test_session(test_db_engine):
    with Session(test_db_engine) as session:
        yield session


@pytest.fixture
def coordinator():
    coordinator = CoordinatorService()
    coordinator.ai_generator.generate_content = AsyncMock(
        return_value={
            "title": "Test Video",
            "description": "Test Description",
            "script": "Test Script",
            "tags": ["test"],
        }
    )
    coordinator.youtube_client.upload_video = AsyncMock(
        return_value="https://youtube.com/watch?v=test123"
    )
    coordinator.alert_service.send_success_alert = AsyncMock()
    coordinator.alert_service.send_failure_alert = AsyncMock()
    return coordinator


@pytest.fixture
def sample_channel(test_session):
    channel = ChannelConfig(
        channel_name="Test Channel",
        channel_id="test_channel_123",
        description="Test channel description",
    )
    test_session.add(channel)
    test_session.commit()
    test_session.refresh(channel)
    return channel


@pytest.fixture
def sample_content_config(test_session, sample_channel):
    content = ContentConfig(
        channel_id=sample_channel.id,
        content_template="Test template",
        ai_model="gpt-4",
    )
    test_session.add(content)
    test_session.commit()
    test_session.refresh(content)
    return content


@pytest.fixture
def sample_schedule(test_session, sample_channel):
    schedule = SchedulePreference(
        channel_id=sample_channel.id,
        frequency="daily",
        preferred_time="09:00",
        timezone="UTC",
        is_active=True,
    )
    test_session.add(schedule)
    test_session.commit()
    test_session.refresh(schedule)
    return schedule


@pytest.mark.asyncio
async def test_execute_upload_job_success(
    coordinator, sample_channel, sample_content_config, test_db_engine
):
    with patch("src.services.coordinator.engine", test_db_engine):
        await coordinator.execute_upload_job(sample_channel.id)

    coordinator.ai_generator.generate_content.assert_called_once()
    coordinator.youtube_client.upload_video.assert_called_once()
    coordinator.alert_service.send_success_alert.assert_called_once()

    with Session(test_db_engine) as session:
        from sqlmodel import select

        job_history = session.exec(select(JobRunHistory)).first()
        assert job_history is not None
        assert job_history.status == "success"
        assert job_history.channel_id == sample_channel.id
        assert job_history.video_url == "https://youtube.com/watch?v=test123"
        assert job_history.end_time is not None


@pytest.mark.asyncio
async def test_execute_upload_job_ai_generation_failure(
    coordinator, sample_channel, sample_content_config, test_db_engine
):
    from src.services.ai_generator import AIGenerationError

    coordinator.ai_generator.generate_content = AsyncMock(
        side_effect=AIGenerationError("AI generation failed")
    )

    with patch("src.services.coordinator.engine", test_db_engine):
        await coordinator.execute_upload_job(sample_channel.id)

    coordinator.youtube_client.upload_video.assert_not_called()
    coordinator.alert_service.send_failure_alert.assert_called_once()

    with Session(test_db_engine) as session:
        from sqlmodel import select

        job_history = session.exec(select(JobRunHistory)).first()
        assert job_history is not None
        assert job_history.status == "failure"
        assert "AI generation failed" in job_history.error_message


@pytest.mark.asyncio
async def test_execute_upload_job_youtube_upload_failure(
    coordinator, sample_channel, sample_content_config, test_db_engine
):
    from src.services.youtube_client import YouTubeUploadError

    coordinator.youtube_client.upload_video = AsyncMock(
        side_effect=YouTubeUploadError("Upload failed")
    )

    with patch("src.services.coordinator.engine", test_db_engine):
        await coordinator.execute_upload_job(sample_channel.id)

    coordinator.ai_generator.generate_content.assert_called_once()
    coordinator.alert_service.send_failure_alert.assert_called_once()

    with Session(test_db_engine) as session:
        from sqlmodel import select

        job_history = session.exec(select(JobRunHistory)).first()
        assert job_history is not None
        assert job_history.status == "failure"
        assert "Upload failed" in job_history.error_message


@pytest.mark.asyncio
async def test_execute_upload_job_channel_not_found(coordinator, test_db_engine):
    with patch("src.services.coordinator.engine", test_db_engine):
        await coordinator.execute_upload_job(999)

    coordinator.ai_generator.generate_content.assert_not_called()
    coordinator.youtube_client.upload_video.assert_not_called()

    with Session(test_db_engine) as session:
        from sqlmodel import select

        job_history = session.exec(select(JobRunHistory)).first()
        assert job_history is not None
        assert job_history.status == "failure"
        assert "Channel config not found" in job_history.error_message
