from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path


class CaptionService(ABC):
    @abstractmethod
    def generate_captions(
        self,
        text: str,
        duration: float,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate caption/subtitle data from text.
        
        Args:
            text: Text to be captioned
            duration: Total duration in seconds
            **kwargs: Additional parameters (words_per_caption, etc.)
            
        Returns:
            List of caption dicts containing:
                - text: Caption text
                - start: Start time in seconds
                - end: End time in seconds
        """
        pass

    @abstractmethod
    def save_captions_srt(
        self,
        captions: List[Dict[str, Any]],
        output_path: Path
    ) -> Path:
        """
        Save captions in SRT format.
        
        Args:
            captions: List of caption dicts from generate_captions
            output_path: Path where SRT file should be saved
            
        Returns:
            Path to saved SRT file
        """
        pass

    @abstractmethod
    def transcribe_audio(
        self,
        audio_path: Path,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Transcribe audio and generate timed captions.
        
        Args:
            audio_path: Path to audio file
            **kwargs: Additional parameters
            
        Returns:
            List of caption dicts with timing information
        """
        pass
