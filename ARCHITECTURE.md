# Architecture Documentation

## Overview

The AI Services Layer is designed with a modular, pluggable architecture that supports multiple AI providers while maintaining clean separation of concerns.

## Design Principles

1. **Interface-based Design**: All services implement abstract base classes
2. **Dependency Injection**: Services are injected into orchestrator
3. **Configuration-driven**: Behavior controlled via environment variables
4. **Fail-safe**: Automatic fallback to mock services
5. **Extensible**: Easy to add new providers or services

## Core Components

### 1. Interfaces (`ai/interfaces/`)

Define contracts for all services:

- `VideoGenerator`: Generate visual content (images/videos)
- `VoiceoverService`: Generate narration audio
- `ThumbnailService`: Generate thumbnail images
- `CaptionService`: Generate and manage subtitles
- `MetadataService`: Generate titles, descriptions, tags

**Key Design**: All interfaces use ABC (Abstract Base Class) to enforce implementation contracts.

### 2. Adapters (`ai/adapters/`)

Concrete implementations of interfaces for different providers:

#### OpenAI Adapters
- `OpenAIMetadataService`: GPT-4 for metadata generation
- `OpenAICaptionService`: Whisper for audio transcription

#### ElevenLabs Adapters
- `ElevenLabsVoiceoverService`: Professional voice synthesis

#### Stability AI Adapters
- `StabilityVideoGenerator`: Image generation for video frames
- `StabilityThumbnailService`: Thumbnail image generation

#### Mock Adapters
- Full set of mock implementations for local development
- Generate placeholder content without API calls
- Useful for testing and development

### 3. Orchestrator (`ai/orchestrator/`)

The `VideoOrchestrator` class coordinates all services:

```
┌─────────────────────────────────────┐
│     VideoOrchestrator               │
├─────────────────────────────────────┤
│  - coordinate all services          │
│  - manage workflow                  │
│  - compose video with MoviePy       │
└─────────────────────────────────────┘
           │
           ├──> VideoGenerator (visuals)
           ├──> VoiceoverService (audio)
           ├──> ThumbnailService (thumbnail)
           ├──> CaptionService (subtitles)
           └──> MetadataService (metadata)
```

### 4. Factory (`ai/factory.py`)

The `ServiceFactory` handles service instantiation:

- Reads configuration
- Selects appropriate adapter based on API keys
- Falls back to mock services if needed
- Returns configured service instances

**Selection Logic**:
```
if use_mock_services:
    return MockService()
elif api_key_available:
    return RealService(api_key)
else:
    log_warning("No API key, using mock")
    return MockService()
```

### 5. Configuration (`ai/config.py`)

Uses Pydantic for configuration management:

- Type-safe configuration
- Environment variable loading
- Validation
- Default values

## Data Flow

### Complete Video Creation

```
1. User provides script and scene prompts
                 ↓
2. Generate voiceover from script
   → ElevenLabs/Mock → audio.mp3
                 ↓
3. Generate visuals for each scene
   → Stability/Mock → image_1.png, image_2.png, ...
                 ↓
4. Generate captions from script
   → OpenAI/Mock → captions.srt
                 ↓
5. Generate thumbnail
   → Stability/Mock → thumbnail.png
                 ↓
6. Generate metadata
   → OpenAI/Mock → title, description, tags
                 ↓
7. Compose video with MoviePy
   - Concatenate images as video clips
   - Add audio track
   - Optionally burn-in captions
   - Export as MP4
                 ↓
8. Return asset paths and metadata
```

## Extension Points

### Adding a New AI Provider

1. Create new directory: `ai/adapters/provider_name/`
2. Implement relevant interfaces
3. Add API key to `AIServiceConfig`
4. Update `ServiceFactory` with selection logic
5. Add tests
6. Document in README

Example:
```python
# ai/adapters/anthropic/anthropic_metadata_service.py
from ai.interfaces import MetadataService

class AnthropicMetadataService(MetadataService):
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
    
    def generate_metadata(self, content, **kwargs):
        # Implementation
        pass
```

### Adding a New Service Type

1. Define interface in `ai/interfaces/new_service.py`
2. Implement mock version
3. Implement real adapter(s)
4. Update `VideoOrchestrator` to use new service
5. Update `ServiceFactory`
6. Add tests

## Error Handling Strategy

1. **Custom Exceptions**: Domain-specific exceptions in `exceptions.py`
2. **Logging**: Comprehensive logging at all levels
3. **Graceful Degradation**: Fall back to mock services
4. **User Feedback**: Clear error messages

## Testing Strategy

1. **Unit Tests**: Test each service independently
2. **Mock Services**: Test orchestration without API calls
3. **Integration Tests**: Can be added with real API keys (not included)
4. **Coverage**: Aim for >80% code coverage

## Performance Considerations

1. **API Calls**: Services make external API calls (can be slow)
2. **Video Processing**: MoviePy operations are CPU-intensive
3. **File I/O**: Multiple file operations for assets
4. **Memory**: Video clips loaded into memory

**Optimization Opportunities**:
- Implement caching for API responses
- Parallel processing for independent operations
- Stream processing for large videos
- Batch API requests where possible

## Security Considerations

1. **API Keys**: Never commit to repository
2. **Environment Variables**: Use `.env` file (gitignored)
3. **Input Validation**: Validate all user inputs
4. **File Paths**: Use Path objects, avoid injection
5. **Dependencies**: Regular security updates

## Future Enhancements

Potential improvements:
- Async/await for concurrent API calls
- Progress callbacks for long operations
- Video template system
- Batch video generation
- Cloud storage integration
- Queue system for background processing
- Web API/REST interface
- Real-time preview generation
