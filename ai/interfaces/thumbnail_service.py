from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class ThumbnailService(ABC):
    @abstractmethod
    def generate_thumbnail(
        self,
        prompt: str,
        output_path: Path,
        width: int = 1280,
        height: int = 720,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a thumbnail image from a text prompt.
        
        Args:
            prompt: Text description for thumbnail generation
            output_path: Path where thumbnail should be saved
            width: Thumbnail width in pixels
            height: Thumbnail height in pixels
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing:
                - path: Path to generated thumbnail
                - width: Actual width
                - height: Actual height
                - metadata: Additional metadata about generation
        """
        pass

    @abstractmethod
    def generate_thumbnail_from_video(
        self,
        video_path: Path,
        output_path: Path,
        timestamp: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract a thumbnail from a video file.
        
        Args:
            video_path: Path to source video
            output_path: Path where thumbnail should be saved
            timestamp: Time in seconds to extract frame from
            **kwargs: Additional parameters
            
        Returns:
            Dict containing:
                - path: Path to generated thumbnail
                - width: Actual width
                - height: Actual height
                - metadata: Additional metadata
        """
        pass
