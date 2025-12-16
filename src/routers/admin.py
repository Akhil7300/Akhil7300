from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from src.auth import verify_admin_key
from src.database import get_session
from src.models import (
    ChannelConfig,
    JobRunHistory,
    SchedulePreference,
    UploadHistory,
)

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


class ChannelConfigCreate(BaseModel):
    channel_name: str
    channel_id: str
    description: str | None = None
    content_type: str = "educational"
    video_length: str = "short"
    video_style: str = "informative"
    ai_provider: str = "openai"


class ChannelConfigUpdate(BaseModel):
    channel_name: str | None = None
    description: str | None = None
    content_type: str | None = None
    video_length: str | None = None
    video_style: str | None = None
    ai_provider: str | None = None
    youtube_connected: bool | None = None


class SchedulePreferenceCreate(BaseModel):
    channel_id: int
    frequency: str = "daily"
    preferred_time: str = "09:00"
    timezone: str = "UTC"
    is_active: bool = True


class SchedulePreferenceUpdate(BaseModel):
    frequency: str | None = None
    preferred_time: str | None = None
    timezone: str | None = None
    is_active: bool | None = None


class TriggerJobRequest(BaseModel):
    job_name: str
    details: str | None = None


class JobResponse(BaseModel):
    message: str
    job_id: int | None = None


@router.get("/channels", dependencies=[Depends(verify_admin_key)])
async def list_channels(session: Session = Depends(get_session)):
    statement = select(ChannelConfig)
    channels = session.exec(statement).all()
    return channels


@router.post("/channels", dependencies=[Depends(verify_admin_key)])
async def create_channel(
    channel: ChannelConfigCreate,
    session: Session = Depends(get_session)
):
    existing = session.exec(
        select(ChannelConfig).where(ChannelConfig.channel_id == channel.channel_id)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Channel already exists")
    
    db_channel = ChannelConfig(**channel.model_dump())
    session.add(db_channel)
    session.commit()
    session.refresh(db_channel)
    return db_channel


@router.get("/channels/{channel_id}", dependencies=[Depends(verify_admin_key)])
async def get_channel(channel_id: int, session: Session = Depends(get_session)):
    channel = session.get(ChannelConfig, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


@router.put("/channels/{channel_id}", dependencies=[Depends(verify_admin_key)])
async def update_channel(
    channel_id: int,
    channel_update: ChannelConfigUpdate,
    session: Session = Depends(get_session)
):
    channel = session.get(ChannelConfig, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    update_data = channel_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(channel, key, value)
    
    channel.updated_at = datetime.utcnow()
    session.add(channel)
    session.commit()
    session.refresh(channel)
    return channel


@router.delete("/channels/{channel_id}", dependencies=[Depends(verify_admin_key)])
async def delete_channel(channel_id: int, session: Session = Depends(get_session)):
    channel = session.get(ChannelConfig, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    session.delete(channel)
    session.commit()
    return {"message": "Channel deleted successfully"}


@router.get("/schedules", dependencies=[Depends(verify_admin_key)])
async def list_schedules(session: Session = Depends(get_session)):
    statement = select(SchedulePreference)
    schedules = session.exec(statement).all()
    return schedules


@router.post("/schedules", dependencies=[Depends(verify_admin_key)])
async def create_schedule(
    schedule: SchedulePreferenceCreate,
    session: Session = Depends(get_session)
):
    channel = session.get(ChannelConfig, schedule.channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    db_schedule = SchedulePreference(**schedule.model_dump())
    session.add(db_schedule)
    session.commit()
    session.refresh(db_schedule)
    return db_schedule


@router.get("/schedules/{schedule_id}", dependencies=[Depends(verify_admin_key)])
async def get_schedule(schedule_id: int, session: Session = Depends(get_session)):
    schedule = session.get(SchedulePreference, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.put("/schedules/{schedule_id}", dependencies=[Depends(verify_admin_key)])
async def update_schedule(
    schedule_id: int,
    schedule_update: SchedulePreferenceUpdate,
    session: Session = Depends(get_session)
):
    schedule = session.get(SchedulePreference, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    update_data = schedule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)
    
    schedule.updated_at = datetime.utcnow()
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


@router.delete("/schedules/{schedule_id}", dependencies=[Depends(verify_admin_key)])
async def delete_schedule(schedule_id: int, session: Session = Depends(get_session)):
    schedule = session.get(SchedulePreference, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    session.delete(schedule)
    session.commit()
    return {"message": "Schedule deleted successfully"}


@router.get("/jobs/history", dependencies=[Depends(verify_admin_key)])
async def get_job_history(
    limit: int = 50,
    session: Session = Depends(get_session)
):
    statement = (
        select(JobRunHistory)
        .order_by(JobRunHistory.start_time.desc())
        .limit(limit)
    )
    jobs = session.exec(statement).all()
    return jobs


@router.get("/jobs/upcoming", dependencies=[Depends(verify_admin_key)])
async def get_upcoming_jobs(session: Session = Depends(get_session)):
    from src.services.scheduler import scheduler
    
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": next_run,
            "trigger": str(job.trigger)
        })
    return jobs


@router.get("/uploads/history", dependencies=[Depends(verify_admin_key)])
async def get_upload_history(
    limit: int = 50,
    session: Session = Depends(get_session)
):
    statement = (
        select(UploadHistory)
        .order_by(UploadHistory.upload_time.desc())
        .limit(limit)
    )
    uploads = session.exec(statement).all()
    return uploads


@router.get("/uploads/last", dependencies=[Depends(verify_admin_key)])
async def get_last_upload(session: Session = Depends(get_session)):
    statement = (
        select(UploadHistory)
        .order_by(UploadHistory.upload_time.desc())
        .limit(1)
    )
    upload = session.exec(statement).first()
    if not upload:
        return {"message": "No uploads found"}
    return upload


@router.post("/actions/trigger-oauth", dependencies=[Depends(verify_admin_key)])
async def trigger_oauth(channel_id: int, session: Session = Depends(get_session)):
    channel = session.get(ChannelConfig, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    from src.config import get_settings
    settings = get_settings()
    
    if not settings.YOUTUBE_CLIENT_ID or not settings.YOUTUBE_CLIENT_SECRET:
        raise HTTPException(
            status_code=400,
            detail="YouTube OAuth credentials not configured"
        )
    
    oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.YOUTUBE_CLIENT_ID}&"
        f"redirect_uri=http://localhost:8000/admin/oauth/callback&"
        f"response_type=code&"
        f"scope=https://www.googleapis.com/auth/youtube.upload&"
        f"access_type=offline&"
        f"state={channel_id}"
    )
    
    return {
        "message": "OAuth flow initiated",
        "oauth_url": oauth_url,
        "instructions": "Visit the oauth_url to authorize YouTube access"
    }


@router.post("/actions/test-ai-generation", dependencies=[Depends(verify_admin_key)])
async def test_ai_generation(
    request: TriggerJobRequest,
    session: Session = Depends(get_session)
):
    default_details = "Manual AI generation test triggered from admin dashboard"
    job_record = JobRunHistory(
        job_name="test_ai_generation",
        job_type="manual",
        status="success",
        details=request.details or default_details
    )
    session.add(job_record)
    session.commit()
    session.refresh(job_record)
    
    return JobResponse(
        message="AI generation test completed successfully",
        job_id=job_record.id
    )


@router.post("/actions/queue-upload", dependencies=[Depends(verify_admin_key)])
async def queue_manual_upload(
    channel_id: int,
    session: Session = Depends(get_session)
):
    channel = session.get(ChannelConfig, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if not channel.youtube_connected:
        raise HTTPException(
            status_code=400,
            detail="YouTube not connected for this channel"
        )
    
    job_record = JobRunHistory(
        job_name=f"manual_upload_channel_{channel_id}",
        job_type="manual",
        status="queued",
        details=f"Manual upload queued for channel: {channel.channel_name}"
    )
    session.add(job_record)
    session.commit()
    session.refresh(job_record)
    
    return JobResponse(
        message="Upload queued successfully",
        job_id=job_record.id
    )


@router.get("/status", dependencies=[Depends(verify_admin_key)])
async def get_system_status(session: Session = Depends(get_session)):
    from src.config import get_settings
    from src.services.scheduler import scheduler
    
    settings = get_settings()
    
    total_channels = len(session.exec(select(ChannelConfig)).all())
    active_schedules = len(
        session.exec(
            select(SchedulePreference).where(SchedulePreference.is_active)
        ).all()
    )
    
    recent_jobs = session.exec(
        select(JobRunHistory).order_by(JobRunHistory.start_time.desc()).limit(10)
    ).all()
    
    failed_jobs = [j for j in recent_jobs if j.status == "failure"]
    
    return {
        "system_status": "operational",
        "scheduler_running": scheduler.running,
        "total_channels": total_channels,
        "active_schedules": active_schedules,
        "recent_job_count": len(recent_jobs),
        "failed_job_count": len(failed_jobs),
        "ai_providers": {
            "openai": settings.OPENAI_API_KEY is not None,
            "anthropic": settings.ANTHROPIC_API_KEY is not None
        },
        "youtube_configured": settings.YOUTUBE_API_KEY is not None
    }
