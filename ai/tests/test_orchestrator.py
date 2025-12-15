import pytest
from pathlib import Path
import tempfile
import shutil
from ai.config import AIServiceConfig
from ai.factory import ServiceFactory
from ai.orchestrator import VideoOrchestrator


@pytest.fixture
def temp_dir():
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def config(temp_dir):
    return AIServiceConfig(
        use_mock_services=True,
        output_dir=str(temp_dir / "output"),
        temp_dir=str(temp_dir / "temp"),
        video_duration=10,
        video_width=640,
        video_height=480,
        video_fps=24,
    )


@pytest.fixture
def orchestrator(config):
    return ServiceFactory.create_orchestrator(config)


class TestVideoOrchestrator:
    def test_initialization(self, orchestrator):
        assert orchestrator is not None
        assert orchestrator.config is not None
        assert orchestrator.video_generator is not None
        assert orchestrator.voiceover_service is not None
        assert orchestrator.thumbnail_service is not None
        assert orchestrator.caption_service is not None
        assert orchestrator.metadata_service is not None

    def test_create_video(self, orchestrator):
        script = "This is a test video about artificial intelligence and machine learning."
        scene_prompts = [
            "A robot thinking",
            "Neural network visualization",
            "AI in action",
        ]
        
        result = orchestrator.create_video(
            script=script,
            scene_prompts=scene_prompts,
            output_filename="test_video.mp4"
        )
        
        assert "video_path" in result
        assert "thumbnail_path" in result
        assert "captions_path" in result
        assert "metadata" in result
        assert "duration" in result
        
        assert Path(result["video_path"]).exists()
        assert Path(result["thumbnail_path"]).exists()
        assert Path(result["captions_path"]).exists()
        
        assert result["metadata"]["title"]
        assert result["metadata"]["description"]
        assert len(result["metadata"]["tags"]) > 0

    def test_generate_voiceover(self, orchestrator, temp_dir):
        script = "Test narration script"
        result = orchestrator._generate_voiceover(script, temp_dir)
        
        assert "path" in result
        assert "duration" in result
        assert Path(result["path"]).exists()

    def test_generate_visuals(self, orchestrator, temp_dir):
        prompts = ["Scene 1", "Scene 2"]
        duration = 10.0
        
        results = orchestrator._generate_visuals(prompts, duration, temp_dir)
        
        assert len(results) == 2
        for result in results:
            assert Path(result["path"]).exists()

    def test_generate_captions(self, orchestrator, temp_dir):
        script = "This is a test caption generation script"
        duration = 5.0
        
        result = orchestrator._generate_captions(script, duration, temp_dir)
        
        assert "captions" in result
        assert "srt_path" in result
        assert len(result["captions"]) > 0
        assert Path(result["srt_path"]).exists()

    def test_generate_thumbnail(self, orchestrator, temp_dir):
        prompt = "Test thumbnail"
        output_path = temp_dir / "thumb.png"
        
        result = orchestrator._generate_thumbnail(prompt, output_path)
        
        assert "path" in result
        assert Path(result["path"]).exists()

    def test_generate_metadata(self, orchestrator):
        script = "AI and machine learning content"
        
        result = orchestrator._generate_metadata(script)
        
        assert "title" in result
        assert "description" in result
        assert "tags" in result


class TestServiceFactory:
    def test_create_orchestrator_with_mock(self, config):
        orchestrator = ServiceFactory.create_orchestrator(config)
        
        assert orchestrator is not None
        from ai.adapters.mock import (
            MockVideoGenerator,
            MockVoiceoverService,
            MockThumbnailService,
            MockCaptionService,
            MockMetadataService,
        )
        
        assert isinstance(orchestrator.video_generator, MockVideoGenerator)
        assert isinstance(orchestrator.voiceover_service, MockVoiceoverService)
        assert isinstance(orchestrator.thumbnail_service, MockThumbnailService)
        assert isinstance(orchestrator.caption_service, MockCaptionService)
        assert isinstance(orchestrator.metadata_service, MockMetadataService)

    def test_create_video_generator(self, config):
        generator = ServiceFactory.create_video_generator(config)
        assert generator is not None

    def test_create_voiceover_service(self, config):
        service = ServiceFactory.create_voiceover_service(config)
        assert service is not None

    def test_create_thumbnail_service(self, config):
        service = ServiceFactory.create_thumbnail_service(config)
        assert service is not None

    def test_create_caption_service(self, config):
        service = ServiceFactory.create_caption_service(config)
        assert service is not None

    def test_create_metadata_service(self, config):
        service = ServiceFactory.create_metadata_service(config)
        assert service is not None
