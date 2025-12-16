import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from src.database import get_session
from src.models import JobRunHistory, SchedulePreference
from src.services.coordinator import coordinator_service
from src.services.scheduler_manager import register_channel_job, unregister_channel_job

router = APIRouter(prefix="/coordinator", tags=["coordinator"])
logger = logging.getLogger(__name__)


class ManualTriggerRequest(BaseModel):
    channel_id: int


class ManualTriggerResponse(BaseModel):
    message: str
    channel_id: int


class JobStatusResponse(BaseModel):
    id: int
    job_name: str
    channel_id: int | None
    status: str
    start_time: str
    end_time: str | None
    video_url: str | None
    error_message: str | None


@router.post("/trigger", response_model=ManualTriggerResponse)
async def manual_trigger(
    request: ManualTriggerRequest,
    session: Session = Depends(get_session),
):
    logger.info(f"Manual trigger requested for channel_id: {request.channel_id}")

    statement = select(SchedulePreference).where(
        SchedulePreference.channel_id == request.channel_id
    )
    schedule = session.exec(statement).first()

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail=f"No schedule found for channel_id: {request.channel_id}",
        )

    try:
        await coordinator_service.execute_upload_job(request.channel_id)
        logger.info(f"Manual trigger completed for channel_id: {request.channel_id}")
        return ManualTriggerResponse(
            message="Upload job triggered successfully",
            channel_id=request.channel_id,
        )
    except Exception as e:
        logger.error(f"Manual trigger failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger job: {str(e)}")


@router.get("/jobs/history", response_model=List[JobStatusResponse])
async def get_job_history(
    channel_id: int | None = None,
    limit: int = 50,
    session: Session = Depends(get_session),
):
    logger.info(f"Fetching job history (channel_id: {channel_id}, limit: {limit})")

    statement = (
        select(JobRunHistory)
        .order_by(JobRunHistory.start_time.desc())
        .limit(limit)
    )

    if channel_id is not None:
        statement = statement.where(JobRunHistory.channel_id == channel_id)

    job_histories = session.exec(statement).all()

    return [
        JobStatusResponse(
            id=job.id,
            job_name=job.job_name,
            channel_id=job.channel_id,
            status=job.status,
            start_time=job.start_time.isoformat(),
            end_time=job.end_time.isoformat() if job.end_time else None,
            video_url=job.video_url,
            error_message=job.error_message,
        )
        for job in job_histories
    ]


@router.post("/jobs/register/{channel_id}")
async def register_job(
    channel_id: int,
    session: Session = Depends(get_session),
):
    logger.info(f"Registering job for channel_id: {channel_id}")

    statement = select(SchedulePreference).where(
        SchedulePreference.channel_id == channel_id
    )
    schedule = session.exec(statement).first()

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail=f"No schedule found for channel_id: {channel_id}",
        )

    try:
        register_channel_job(channel_id, schedule)
        return {"message": f"Job registered for channel_id: {channel_id}"}
    except Exception as e:
        logger.error(f"Failed to register job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to register job: {str(e)}")


@router.delete("/jobs/unregister/{channel_id}")
async def unregister_job(channel_id: int):
    logger.info(f"Unregistering job for channel_id: {channel_id}")

    try:
        unregister_channel_job(channel_id)
        return {"message": f"Job unregistered for channel_id: {channel_id}"}
    except Exception as e:
        logger.error(f"Failed to unregister job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to unregister job: {str(e)}"
        )
