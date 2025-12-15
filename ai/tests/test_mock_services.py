import pytest
from pathlib import Path
import tempfile
import shutil
from ai.adapters.mock import (
    MockVideoGenerator,
    MockVoiceoverService,
    MockThumbnailService,
    MockCaptionService,
    MockMetadataService,
)


@pytest.fixture
def temp_dir():
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


class TestMockVideoGenerator:
    def test_generate_images(self, temp_dir):
        generator = MockVideoGenerator(width=800, height=600)
        prompts = ["A sunset over mountains", "A city skyline"]
        
        results = generator.generate_images(prompts, temp_dir)
        
        assert len(results) == 2
        for result in results:
            assert Path(result["path"]).exists()
            assert result["prompt"] in prompts
            assert result["metadata"]["type"] == "mock"

    def test_generate_video_clips(self, temp_dir):
        generator = MockVideoGenerator()
        prompts = ["Scene 1", "Scene 2"]
        
        results = generator.generate_video_clips(prompts, 5.0, temp_dir)
        
        assert len(results) == 2
        for result in results:
            assert Path(result["path"]).exists()
            assert result["duration"] == 5.0


class TestMockVoiceoverService:
    def test_generate_voiceover(self, temp_dir):
        service = MockVoiceoverService()
        text = "This is a test narration script."
        output_path = temp_dir / "voiceover.wav"
        
        result = service.generate_voiceover(text, output_path)
        
        assert Path(result["path"]).exists()
        assert result["duration"] > 0
        assert result["metadata"]["type"] == "mock"

    def test_get_available_voices(self):
        service = MockVoiceoverService()
        voices = service.get_available_voices()
        
        assert len(voices) > 0
        assert "mock_voice_1" in voices


class TestMockThumbnailService:
    def test_generate_thumbnail(self, temp_dir):
        service = MockThumbnailService()
        prompt = "An exciting video thumbnail"
        output_path = temp_dir / "thumbnail.png"
        
        result = service.generate_thumbnail(prompt, output_path)
        
        assert Path(result["path"]).exists()
        assert result["width"] == 1280
        assert result["height"] == 720

    def test_generate_thumbnail_custom_size(self, temp_dir):
        service = MockThumbnailService()
        output_path = temp_dir / "thumbnail.png"
        
        result = service.generate_thumbnail(
            "Test",
            output_path,
            width=1920,
            height=1080
        )
        
        assert result["width"] == 1920
        assert result["height"] == 1080


class TestMockCaptionService:
    def test_generate_captions(self):
        service = MockCaptionService()
        text = "This is a test video with multiple words in the script."
        duration = 10.0
        
        captions = service.generate_captions(text, duration)
        
        assert len(captions) > 0
        for caption in captions:
            assert "text" in caption
            assert "start" in caption
            assert "end" in caption
            assert caption["start"] < caption["end"]

    def test_save_captions_srt(self, temp_dir):
        service = MockCaptionService()
        captions = [
            {"text": "First caption", "start": 0.0, "end": 2.0},
            {"text": "Second caption", "start": 2.0, "end": 4.0},
        ]
        output_path = temp_dir / "captions.srt"
        
        result = service.save_captions_srt(captions, output_path)
        
        assert Path(result).exists()
        content = Path(result).read_text()
        assert "First caption" in content
        assert "Second caption" in content

    def test_transcribe_audio(self, temp_dir):
        service = MockCaptionService()
        audio_path = temp_dir / "audio.mp3"
        audio_path.touch()
        
        captions = service.transcribe_audio(audio_path)
        
        assert len(captions) > 0


class TestMockMetadataService:
    def test_generate_metadata(self):
        service = MockMetadataService()
        content = "This is a video about programming and software development."
        
        metadata = service.generate_metadata(content)
        
        assert "title" in metadata
        assert "description" in metadata
        assert "tags" in metadata
        assert len(metadata["tags"]) > 0

    def test_generate_title(self):
        service = MockMetadataService()
        content = "How to build amazing applications with Python"
        
        title = service.generate_title(content)
        
        assert len(title) > 0
        assert len(title) <= 100

    def test_generate_description(self):
        service = MockMetadataService()
        content = "Learn about AI and machine learning"
        
        description = service.generate_description(content)
        
        assert len(description) > 0
        assert content in description

    def test_generate_tags(self):
        service = MockMetadataService()
        content = "Python programming tutorial for beginners"
        
        tags = service.generate_tags(content, max_tags=5)
        
        assert len(tags) <= 5
        assert all(len(tag) > 3 for tag in tags)
