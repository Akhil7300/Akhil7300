class AIServiceError(Exception):
    pass


class VideoGenerationError(AIServiceError):
    pass


class VoiceoverError(AIServiceError):
    pass


class ThumbnailError(AIServiceError):
    pass


class CaptionError(AIServiceError):
    pass


class MetadataError(AIServiceError):
    pass


class ConfigurationError(AIServiceError):
    pass


class APIError(AIServiceError):
    pass
