import pytest
from pathlib import Path
import tempfile
import shutil
from ai.config import AIServiceConfig


@pytest.fixture
def temp_dir():
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


class TestAIServiceConfig:
    def test_default_config(self):
        config = AIServiceConfig()
        
        assert config.openai_model == "gpt-4"
        assert config.video_width == 1920
        assert config.video_height == 1080
        assert config.video_fps == 30
        assert config.video_duration == 60
        assert config.use_mock_services is False
        assert config.log_level == "INFO"

    def test_custom_config(self, temp_dir):
        config = AIServiceConfig(
            openai_api_key="test_key",
            video_width=1280,
            video_height=720,
            output_dir=str(temp_dir / "output"),
            temp_dir=str(temp_dir / "temp"),
            use_mock_services=True,
        )
        
        assert config.openai_api_key == "test_key"
        assert config.video_width == 1280
        assert config.video_height == 720
        assert config.use_mock_services is True

    def test_directories_created(self, temp_dir):
        output_dir = temp_dir / "output"
        temp_dir_path = temp_dir / "temp"
        
        config = AIServiceConfig(
            output_dir=str(output_dir),
            temp_dir=str(temp_dir_path),
        )
        
        assert output_dir.exists()
        assert temp_dir_path.exists()

    def test_config_with_all_api_keys(self):
        config = AIServiceConfig(
            openai_api_key="openai_test",
            elevenlabs_api_key="elevenlabs_test",
            stability_api_key="stability_test",
        )
        
        assert config.openai_api_key == "openai_test"
        assert config.elevenlabs_api_key == "elevenlabs_test"
        assert config.stability_api_key == "stability_test"
