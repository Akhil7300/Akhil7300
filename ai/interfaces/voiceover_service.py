from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class VoiceoverService(ABC):
    @abstractmethod
    def generate_voiceover(
        self,
        text: str,
        output_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate voiceover audio from text.
        
        Args:
            text: Text to convert to speech
            output_path: Path where audio file should be saved
            **kwargs: Additional parameters (voice_id, speed, etc.)
            
        Returns:
            Dict containing:
                - path: Path to generated audio file
                - duration: Duration in seconds
                - metadata: Additional metadata about generation
        """
        pass

    @abstractmethod
    def get_available_voices(self) -> Dict[str, Any]:
        """
        Get list of available voices.
        
        Returns:
            Dict mapping voice IDs to voice information
        """
        pass
