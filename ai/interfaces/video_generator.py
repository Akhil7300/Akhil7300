from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path


class VideoGenerator(ABC):
    @abstractmethod
    def generate_video_clips(
        self,
        prompts: List[str],
        duration_per_clip: float,
        output_dir: Path,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate video clips from text prompts.
        
        Args:
            prompts: List of text descriptions for video generation
            duration_per_clip: Duration in seconds for each clip
            output_dir: Directory to save generated clips
            **kwargs: Additional generation parameters
            
        Returns:
            List of dicts containing:
                - path: Path to generated video clip
                - prompt: Original prompt used
                - metadata: Additional metadata about generation
        """
        pass

    @abstractmethod
    def generate_images(
        self,
        prompts: List[str],
        output_dir: Path,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate static images from text prompts (fallback for video).
        
        Args:
            prompts: List of text descriptions for image generation
            output_dir: Directory to save generated images
            **kwargs: Additional generation parameters
            
        Returns:
            List of dicts containing:
                - path: Path to generated image
                - prompt: Original prompt used
                - metadata: Additional metadata about generation
        """
        pass
