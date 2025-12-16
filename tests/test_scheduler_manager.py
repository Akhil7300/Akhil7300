from datetime import datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.models import ChannelConfig, SchedulePreference
from src.services.scheduler_manager import (
    calculate_next_run,
    register_channel_job,
    sync_all_jobs,
    unregister_channel_job,
)


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


def test_calculate_next_run_daily():
    frequency = "daily"
    preferred_time = "15:30"
    timezone = "UTC"

    next_run = calculate_next_run(frequency, preferred_time, timezone)

    assert next_run.hour == 15
    assert next_run.minute == 30
    assert next_run > datetime.now(ZoneInfo("UTC"))


def test_calculate_next_run_weekly():
    frequency = "weekly"
    preferred_time = "10:00"
    timezone = "UTC"

    next_run = calculate_next_run(frequency, preferred_time, timezone)

    assert next_run.hour == 10
    assert next_run.minute == 0
    assert next_run > datetime.now(ZoneInfo("UTC"))


def test_calculate_next_run_invalid_timezone():
    frequency = "daily"
    preferred_time = "12:00"
    timezone = "Invalid/Timezone"

    next_run = calculate_next_run(frequency, preferred_time, timezone)

    assert next_run is not None
    assert next_run.hour == 12
    assert next_run.minute == 0


def test_calculate_next_run_with_timezone():
    frequency = "daily"
    preferred_time = "09:00"
    timezone = "America/New_York"

    next_run = calculate_next_run(frequency, preferred_time, timezone)

    assert next_run.hour == 9
    assert next_run.minute == 0


def test_register_channel_job():
    mock_scheduler = MagicMock()

    schedule_pref = SchedulePreference(
        id=1,
        channel_id=1,
        frequency="daily",
        preferred_time="09:00",
        timezone="UTC",
        is_active=True,
    )

    with patch("src.services.scheduler_manager.scheduler", mock_scheduler):
        register_channel_job(1, schedule_pref)

    mock_scheduler.add_job.assert_called_once()
    call_args = mock_scheduler.add_job.call_args

    assert call_args.kwargs["id"] == "channel_1_upload"
    assert call_args.kwargs["replace_existing"] is True


def test_register_channel_job_replaces_existing():
    mock_scheduler = MagicMock()
    mock_scheduler.get_job.return_value = MagicMock()

    schedule_pref = SchedulePreference(
        id=1,
        channel_id=1,
        frequency="daily",
        preferred_time="09:00",
        timezone="UTC",
        is_active=True,
    )

    with patch("src.services.scheduler_manager.scheduler", mock_scheduler):
        register_channel_job(1, schedule_pref)

    mock_scheduler.remove_job.assert_called_once_with("channel_1_upload")
    mock_scheduler.add_job.assert_called_once()


def test_unregister_channel_job():
    mock_scheduler = MagicMock()

    with patch("src.services.scheduler_manager.scheduler", mock_scheduler):
        unregister_channel_job(1)

    mock_scheduler.remove_job.assert_called_once_with("channel_1_upload")


def test_sync_all_jobs(test_db_engine, test_session):
    channel = ChannelConfig(
        channel_name="Test Channel",
        channel_id="test_123",
    )
    test_session.add(channel)
    test_session.commit()
    test_session.refresh(channel)

    schedule = SchedulePreference(
        channel_id=channel.id,
        frequency="daily",
        preferred_time="09:00",
        timezone="UTC",
        is_active=True,
    )
    test_session.add(schedule)
    test_session.commit()

    mock_scheduler = MagicMock()

    with patch("src.services.scheduler_manager.engine", test_db_engine):
        with patch("src.services.scheduler_manager.scheduler", mock_scheduler):
            sync_all_jobs()

    mock_scheduler.add_job.assert_called()

    with Session(test_db_engine) as session:
        from sqlmodel import select

        updated_schedule = session.exec(
            select(SchedulePreference).where(SchedulePreference.id == schedule.id)
        ).first()
        assert updated_schedule.next_run is not None


def test_sync_all_jobs_only_active(test_db_engine, test_session):
    channel1 = ChannelConfig(
        channel_name="Active Channel",
        channel_id="active_123",
    )
    channel2 = ChannelConfig(
        channel_name="Inactive Channel",
        channel_id="inactive_456",
    )
    test_session.add(channel1)
    test_session.add(channel2)
    test_session.commit()
    test_session.refresh(channel1)
    test_session.refresh(channel2)

    schedule1 = SchedulePreference(
        channel_id=channel1.id,
        frequency="daily",
        preferred_time="09:00",
        timezone="UTC",
        is_active=True,
    )
    schedule2 = SchedulePreference(
        channel_id=channel2.id,
        frequency="daily",
        preferred_time="10:00",
        timezone="UTC",
        is_active=False,
    )
    test_session.add(schedule1)
    test_session.add(schedule2)
    test_session.commit()

    mock_scheduler = MagicMock()

    with patch("src.services.scheduler_manager.engine", test_db_engine):
        with patch("src.services.scheduler_manager.scheduler", mock_scheduler):
            sync_all_jobs()

    assert mock_scheduler.add_job.call_count == 1
