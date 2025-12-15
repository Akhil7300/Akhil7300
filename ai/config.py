import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")
    
    elevenlabs_api_key: Optional[str] = Field(default=None, alias="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM", alias="ELEVENLABS_VOICE_ID")
    
    stability_api_key: Optional[str] = Field(default=None, alias="STABILITY_API_KEY")
    stability_engine: str = Field(default="stable-diffusion-xl-1024-v1-0", alias="STABILITY_ENGINE")
    
    video_width: int = Field(default=1920, alias="VIDEO_WIDTH")
    video_height: int = Field(default=1080, alias="VIDEO_HEIGHT")
    video_fps: int = Field(default=30, alias="VIDEO_FPS")
    video_duration: int = Field(default=60, alias="VIDEO_DURATION")
    
    output_dir: str = Field(default="./output", alias="OUTPUT_DIR")
    temp_dir: str = Field(default="./temp", alias="TEMP_DIR")
    
    use_mock_services: bool = Field(default=False, alias="USE_MOCK_SERVICES")
    
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
