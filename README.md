# AI Services Layer

A comprehensive AI services package for automated video content generation with pluggable adapters for multiple AI APIs.

## Features

- **Modular Architecture**: Clean interfaces with pluggable adapters
- **Multiple AI Providers**: Support for OpenAI, ElevenLabs, and Stability AI
- **Video Orchestration**: MoviePy integration for professional video composition
- **Mock Implementations**: Local development without API keys
- **Comprehensive Services**:
  - Video content generation (visuals)
  - Voiceover/narration synthesis
  - Thumbnail imagery generation
  - Caption/subtitle generation
  - Metadata generation (titles, descriptions, tags)

## Installation

```bash
pip install -r requirements.txt
```

For development:

```bash
pip install -r requirements-dev.txt
```

## Configuration

The package uses environment variables for configuration. Create a `.env` file in your project root:

```env
# OpenAI Configuration (for metadata and captions)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# ElevenLabs Configuration (for voiceover)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Stability AI Configuration (for images/thumbnails)
STABILITY_API_KEY=your_stability_api_key_here
STABILITY_ENGINE=stable-diffusion-xl-1024-v1-0

# Video Configuration
VIDEO_WIDTH=1920
VIDEO_HEIGHT=1080
VIDEO_FPS=30
VIDEO_DURATION=60

# Output Configuration
OUTPUT_DIR=./output
TEMP_DIR=./temp

# Development Mode (uses mock services)
USE_MOCK_SERVICES=false

# Logging
LOG_LEVEL=INFO
```

### Required API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| OpenAI | Metadata generation, captions | [platform.openai.com](https://platform.openai.com) |
| ElevenLabs | Voiceover/narration | [elevenlabs.io](https://elevenlabs.io) |
| Stability AI | Image/thumbnail generation | [platform.stability.ai](https://platform.stability.ai) |

**Note**: If API keys are not provided, the system automatically falls back to mock implementations for local development.

## Usage

### Basic Example

```python
from ai import VideoOrchestrator, AIServiceConfig
from ai.factory import ServiceFactory

# Initialize configuration
config = AIServiceConfig()

# Create orchestrator with all services
orchestrator = ServiceFactory.create_orchestrator(config)

# Generate a complete video
result = orchestrator.create_video(
    script="Welcome to our AI-powered video. This demonstrates automated content generation.",
    scene_prompts=[
        "A futuristic AI laboratory",
        "Neural network visualization",
        "Technology and innovation"
    ],
    output_filename="my_video.mp4"
)

print(f"Video created: {result['video_path']}")
print(f"Thumbnail: {result['thumbnail_path']}")
print(f"Title: {result['metadata']['title']}")
print(f"Tags: {', '.join(result['metadata']['tags'])}")
```

### Using Individual Services

```python
from ai.config import AIServiceConfig
from ai.factory import ServiceFactory

config = AIServiceConfig()

# Use metadata service independently
metadata_service = ServiceFactory.create_metadata_service(config)
metadata = metadata_service.generate_metadata(
    "A video about machine learning fundamentals"
)
print(f"Generated title: {metadata['title']}")

# Use voiceover service independently
voiceover_service = ServiceFactory.create_voiceover_service(config)
result = voiceover_service.generate_voiceover(
    "This is the narration text",
    output_path="narration.mp3"
)
print(f"Audio duration: {result['duration']} seconds")

# Use thumbnail service independently
thumbnail_service = ServiceFactory.create_thumbnail_service(config)
thumbnail = thumbnail_service.generate_thumbnail(
    prompt="An exciting video thumbnail about AI",
    output_path="thumbnail.png",
    width=1280,
    height=720
)
```

### Mock Services for Development

```python
from ai import AIServiceConfig
from ai.factory import ServiceFactory

# Enable mock services
config = AIServiceConfig(use_mock_services=True)
orchestrator = ServiceFactory.create_orchestrator(config)

# All API calls will use mock implementations
result = orchestrator.create_video(
    script="Test script",
    scene_prompts=["Scene 1", "Scene 2"],
    output_filename="test.mp4"
)
```

## Architecture

### Package Structure

```
ai/
├── __init__.py                 # Main package exports
├── config.py                   # Configuration management
├── exceptions.py               # Custom exceptions
├── factory.py                  # Service factory
├── interfaces/                 # Abstract base classes
│   ├── video_generator.py
│   ├── voiceover_service.py
│   ├── thumbnail_service.py
│   ├── caption_service.py
│   └── metadata_service.py
├── adapters/                   # Concrete implementations
│   ├── openai/                 # OpenAI adapters
│   │   ├── openai_metadata_service.py
│   │   └── openai_caption_service.py
│   ├── elevenlabs/             # ElevenLabs adapters
│   │   └── elevenlabs_voiceover_service.py
│   ├── stability/              # Stability AI adapters
│   │   ├── stability_video_generator.py
│   │   └── stability_thumbnail_service.py
│   └── mock/                   # Mock implementations
│       ├── mock_video_generator.py
│       ├── mock_voiceover_service.py
│       ├── mock_thumbnail_service.py
│       ├── mock_caption_service.py
│       └── mock_metadata_service.py
├── orchestrator/               # Video composition
│   └── video_orchestrator.py
└── tests/                      # Unit tests
    ├── test_config.py
    ├── test_mock_services.py
    └── test_orchestrator.py
```

### Design Patterns

- **Abstract Base Classes**: All services define clear interfaces
- **Adapter Pattern**: Pluggable implementations for different APIs
- **Factory Pattern**: Centralized service creation based on configuration
- **Dependency Injection**: Services are injected into orchestrator
- **Fallback Strategy**: Automatic fallback to mock services when API keys are missing

## Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=ai --cov-report=html
```

Run specific test file:

```bash
pytest ai/tests/test_orchestrator.py
```

## API Reference

### VideoOrchestrator

Main class for orchestrating video creation.

#### Methods

- `create_video(script, scene_prompts, output_filename, **kwargs)`: Create a complete video with all components

### Service Interfaces

#### VideoGenerator

- `generate_video_clips(prompts, duration_per_clip, output_dir, **kwargs)`: Generate video clips
- `generate_images(prompts, output_dir, **kwargs)`: Generate static images

#### VoiceoverService

- `generate_voiceover(text, output_path, **kwargs)`: Generate voiceover audio
- `get_available_voices()`: List available voices

#### ThumbnailService

- `generate_thumbnail(prompt, output_path, width, height, **kwargs)`: Generate thumbnail
- `generate_thumbnail_from_video(video_path, output_path, timestamp, **kwargs)`: Extract frame from video

#### CaptionService

- `generate_captions(text, duration, **kwargs)`: Generate caption data
- `save_captions_srt(captions, output_path)`: Save captions in SRT format
- `transcribe_audio(audio_path, **kwargs)`: Transcribe audio to captions

#### MetadataService

- `generate_metadata(content, context, **kwargs)`: Generate complete metadata
- `generate_title(content, max_length, **kwargs)`: Generate title
- `generate_description(content, max_length, **kwargs)`: Generate description
- `generate_tags(content, max_tags, **kwargs)`: Generate tags

## Error Handling

All services include comprehensive error handling with custom exceptions:

- `AIServiceError`: Base exception
- `VideoGenerationError`: Video generation failures
- `VoiceoverError`: Voiceover generation failures
- `ThumbnailError`: Thumbnail generation failures
- `CaptionError`: Caption generation failures
- `MetadataError`: Metadata generation failures
- `APIError`: External API failures

## Logging

The package uses Python's logging module. Configure logging level via environment:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Or in `.env`:

```env
LOG_LEVEL=DEBUG
```

## Contributing

1. Follow existing code patterns and conventions
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass before submitting

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.
