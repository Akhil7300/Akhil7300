from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ChannelConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_name: str = Field(index=True)
    channel_id: str = Field(unique=True, index=True)
    description: Optional[str] = None
    content_type: str = Field(default="educational")
    video_length: str = Field(default="short")
    video_style: str = Field(default="informative")
    ai_provider: str = Field(default="openai")
    youtube_connected: bool = Field(default=False)
    youtube_refresh_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SchedulePreference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channelconfig.id")
    frequency: str = Field(default="daily")
    preferred_time: str = Field(default="09:00")
    timezone: str = Field(default="UTC")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class JobRunHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_name: str
    job_type: str = Field(default="scheduled")
    status: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    details: Optional[str] = None
    error_message: Optional[str] = None


class UploadHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channelconfig.id")
    video_title: str
    video_id: Optional[str] = None
    status: str
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
