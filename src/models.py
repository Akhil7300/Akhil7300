from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ChannelConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_name: str = Field(index=True)
    channel_id: str = Field(unique=True, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channelconfig.id")
    content_template: Optional[str] = None
    ai_model: str = Field(default="gpt-4")
    video_duration: int = Field(default=60)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SchedulePreference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channelconfig.id")
    frequency: str = Field(default="daily")
    preferred_time: str = Field(default="09:00")
    timezone: str = Field(default="UTC")
    is_active: bool = Field(default=True)
    next_run: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class JobRunHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_name: str = Field(index=True)
    channel_id: Optional[int] = Field(foreign_key="channelconfig.id", default=None)
    status: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[str] = None
