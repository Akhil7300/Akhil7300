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


class SchedulePreference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channelconfig.id")
    frequency: str = Field(default="daily")  # daily, weekly, etc.
    preferred_time: str = Field(default="09:00")  # HH:MM
    is_active: bool = Field(default=True)


class JobRunHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_name: str
    status: str  # success, failure, running
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    details: Optional[str] = None


class YouTubeOAuthToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Supports multiple connected accounts/channels in the future.
    account_key: str = Field(default="default", unique=True, index=True)

    # Encrypted (Fernet) refresh token.
    encrypted_refresh_token: str

    scopes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
