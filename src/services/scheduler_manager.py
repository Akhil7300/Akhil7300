import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select

from src.database import engine
from src.models import ChannelConfig, SchedulePreference
from src.services.scheduler import scheduler

logger = logging.getLogger(__name__)


def calculate_next_run(frequency: str, preferred_time: str, timezone: str) -> datetime:
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        logger.warning(f"Invalid timezone: {timezone}, using UTC")
        tz = ZoneInfo("UTC")

    now = datetime.now(tz)
    hour, minute = map(int, preferred_time.split(":"))

    if frequency == "daily":
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
    elif frequency == "weekly":
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        days_ahead = 7 - now.weekday()
        if days_ahead <= 0 or (days_ahead == 7 and next_run <= now):
            days_ahead += 7
        next_run += timedelta(days=days_ahead)
    else:
        logger.warning(f"Unknown frequency: {frequency}, defaulting to daily")
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)

    return next_run


def register_channel_job(channel_id: int, schedule_pref: SchedulePreference):
    from src.services.coordinator import coordinator_service

    job_id = f"channel_{channel_id}_upload"

    try:
        tz = ZoneInfo(schedule_pref.timezone)
    except Exception:
        logger.warning(f"Invalid timezone: {schedule_pref.timezone}, using UTC")
        tz = ZoneInfo("UTC")

    hour, minute = map(int, schedule_pref.preferred_time.split(":"))

    if schedule_pref.frequency == "daily":
        trigger = CronTrigger(hour=hour, minute=minute, timezone=tz)
    elif schedule_pref.frequency == "weekly":
        trigger = CronTrigger(day_of_week=0, hour=hour, minute=minute, timezone=tz)
    else:
        logger.warning(f"Unknown frequency: {schedule_pref.frequency}, using daily")
        trigger = CronTrigger(hour=hour, minute=minute, timezone=tz)

    existing_job = scheduler.get_job(job_id)
    if existing_job:
        scheduler.remove_job(job_id)
        logger.info(f"Removed existing job: {job_id}")

    scheduler.add_job(
        coordinator_service.execute_upload_job,
        trigger=trigger,
        id=job_id,
        args=[channel_id],
        replace_existing=True,
        name=f"Upload job for channel {channel_id}",
    )

    logger.info(f"Registered job: {job_id} with trigger: {trigger}")


def unregister_channel_job(channel_id: int):
    job_id = f"channel_{channel_id}_upload"
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Unregistered job: {job_id}")
    except Exception as e:
        logger.warning(f"Failed to unregister job {job_id}: {str(e)}")


def sync_all_jobs():
    logger.info("Syncing all scheduled jobs from database")
    with Session(engine) as session:
        statement = (
            select(SchedulePreference, ChannelConfig)
            .join(ChannelConfig, SchedulePreference.channel_id == ChannelConfig.id)
            .where(SchedulePreference.is_active)
        )
        results = session.exec(statement).all()

        for schedule_pref, channel_config in results:
            logger.info(
                f"Syncing job for channel: {channel_config.channel_name} "
                f"(ID: {channel_config.id})"
            )
            try:
                register_channel_job(channel_config.id, schedule_pref)

                if not schedule_pref.next_run:
                    schedule_pref.next_run = calculate_next_run(
                        schedule_pref.frequency,
                        schedule_pref.preferred_time,
                        schedule_pref.timezone,
                    )
                    session.add(schedule_pref)
                    session.commit()
            except Exception as e:
                logger.error(
                    f"Failed to sync job for channel {channel_config.id}: {str(e)}"
                )

    logger.info("Job sync completed")
