# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Install dependencies
pip install -r requirements.txt
```

## Quick Start with Mock Services

Run the example without any API keys (uses mock services):

```bash
python3 example.py
```

This will create a demo video using mock implementations that don't require API keys.

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
USE_MOCK_SERVICES=false
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
STABILITY_API_KEY=sk-...
```

## Basic Usage

### Create a Complete Video

```python
from ai.factory import ServiceFactory

# Create orchestrator (auto-configures from .env)
orchestrator = ServiceFactory.create_orchestrator()

# Generate video
result = orchestrator.create_video(
    script="Your narration script here...",
    scene_prompts=[
        "Visual description 1",
        "Visual description 2",
        "Visual description 3"
    ],
    output_filename="output.mp4"
)

print(f"Video: {result['video_path']}")
print(f"Title: {result['metadata']['title']}")
```

### Use Individual Services

```python
from ai.config import AIServiceConfig
from ai.factory import ServiceFactory

config = AIServiceConfig()

# Generate metadata only
metadata_service = ServiceFactory.create_metadata_service(config)
metadata = metadata_service.generate_metadata("Your content here")
print(metadata['title'])

# Generate voiceover only
voiceover_service = ServiceFactory.create_voiceover_service(config)
result = voiceover_service.generate_voiceover(
    "Text to speak",
    output_path="audio.mp3"
)

# Generate thumbnail only
thumbnail_service = ServiceFactory.create_thumbnail_service(config)
thumbnail = thumbnail_service.generate_thumbnail(
    "Thumbnail description",
    output_path="thumb.png"
)
```

## Testing

Run all tests:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=ai --cov-report=html
open htmlcov/index.html
```

## Common Issues

### Missing API Keys

If you see "using mock" in the logs, it means API keys are not configured. The system will fall back to mock services.

### MoviePy Errors

If you get MoviePy errors, install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Import Errors

Make sure you're in the project directory and have installed dependencies:

```bash
pip install -r requirements.txt
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Check [example.py](example.py) for a complete usage example
