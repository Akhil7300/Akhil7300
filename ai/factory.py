import logging
from ai.config import AIServiceConfig
from ai.interfaces import (
    VideoGenerator,
    VoiceoverService,
    ThumbnailService,
    CaptionService,
    MetadataService,
)
from ai.orchestrator import VideoOrchestrator

logger = logging.getLogger(__name__)


class ServiceFactory:
    @staticmethod
    def create_orchestrator(config: AIServiceConfig = None) -> VideoOrchestrator:
        """
        Create a VideoOrchestrator with all services configured.
        
        Args:
            config: Optional configuration. If not provided, will use defaults.
            
        Returns:
            Configured VideoOrchestrator instance
        """
        if config is None:
            config = AIServiceConfig()
        
        video_generator = ServiceFactory.create_video_generator(config)
        voiceover_service = ServiceFactory.create_voiceover_service(config)
        thumbnail_service = ServiceFactory.create_thumbnail_service(config)
        caption_service = ServiceFactory.create_caption_service(config)
        metadata_service = ServiceFactory.create_metadata_service(config)
        
        return VideoOrchestrator(
            config=config,
            video_generator=video_generator,
            voiceover_service=voiceover_service,
            thumbnail_service=thumbnail_service,
            caption_service=caption_service,
            metadata_service=metadata_service,
        )

    @staticmethod
    def create_video_generator(config: AIServiceConfig) -> VideoGenerator:
        """Create video generator based on configuration."""
        if config.use_mock_services:
            from ai.adapters.mock import MockVideoGenerator
            logger.info("Using MockVideoGenerator")
            return MockVideoGenerator(config.video_width, config.video_height)
        
        if config.stability_api_key:
            from ai.adapters.stability import StabilityVideoGenerator
            logger.info("Using StabilityVideoGenerator")
            return StabilityVideoGenerator(
                config.stability_api_key,
                config.stability_engine
            )
        
        from ai.adapters.mock import MockVideoGenerator
        logger.warning("No video generator API key found, using mock")
        return MockVideoGenerator(config.video_width, config.video_height)

    @staticmethod
    def create_voiceover_service(config: AIServiceConfig) -> VoiceoverService:
        """Create voiceover service based on configuration."""
        if config.use_mock_services:
            from ai.adapters.mock import MockVoiceoverService
            logger.info("Using MockVoiceoverService")
            return MockVoiceoverService()
        
        if config.elevenlabs_api_key:
            from ai.adapters.elevenlabs import ElevenLabsVoiceoverService
            logger.info("Using ElevenLabsVoiceoverService")
            return ElevenLabsVoiceoverService(
                config.elevenlabs_api_key,
                config.elevenlabs_voice_id
            )
        
        from ai.adapters.mock import MockVoiceoverService
        logger.warning("No voiceover API key found, using mock")
        return MockVoiceoverService()

    @staticmethod
    def create_thumbnail_service(config: AIServiceConfig) -> ThumbnailService:
        """Create thumbnail service based on configuration."""
        if config.use_mock_services:
            from ai.adapters.mock import MockThumbnailService
            logger.info("Using MockThumbnailService")
            return MockThumbnailService()
        
        if config.stability_api_key:
            from ai.adapters.stability import StabilityThumbnailService
            logger.info("Using StabilityThumbnailService")
            return StabilityThumbnailService(
                config.stability_api_key,
                config.stability_engine
            )
        
        from ai.adapters.mock import MockThumbnailService
        logger.warning("No thumbnail API key found, using mock")
        return MockThumbnailService()

    @staticmethod
    def create_caption_service(config: AIServiceConfig) -> CaptionService:
        """Create caption service based on configuration."""
        if config.use_mock_services:
            from ai.adapters.mock import MockCaptionService
            logger.info("Using MockCaptionService")
            return MockCaptionService()
        
        if config.openai_api_key:
            from ai.adapters.openai import OpenAICaptionService
            logger.info("Using OpenAICaptionService")
            return OpenAICaptionService(config.openai_api_key)
        
        from ai.adapters.mock import MockCaptionService
        logger.warning("No caption API key found, using mock")
        return MockCaptionService()

    @staticmethod
    def create_metadata_service(config: AIServiceConfig) -> MetadataService:
        """Create metadata service based on configuration."""
        if config.use_mock_services:
            from ai.adapters.mock import MockMetadataService
            logger.info("Using MockMetadataService")
            return MockMetadataService()
        
        if config.openai_api_key:
            from ai.adapters.openai import OpenAIMetadataService
            logger.info("Using OpenAIMetadataService")
            return OpenAIMetadataService(
                config.openai_api_key,
                config.openai_model
            )
        
        from ai.adapters.mock import MockMetadataService
        logger.warning("No metadata API key found, using mock")
        return MockMetadataService()
