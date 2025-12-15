import logging
from typing import Dict, Any
from pathlib import Path
import wave
import struct
import math
from ai.interfaces.voiceover_service import VoiceoverService

logger = logging.getLogger(__name__)


class MockVoiceoverService(VoiceoverService):
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        logger.info("Initialized MockVoiceoverService")

    def generate_voiceover(
        self,
        text: str,
        output_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"Generating mock voiceover for text of length {len(text)}")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        duration = self._estimate_duration(text)
        self._create_mock_audio(duration, output_path)
        
        result = {
            "path": str(output_path),
            "duration": duration,
            "metadata": {
                "type": "mock",
                "text_length": len(text),
                "sample_rate": self.sample_rate,
            }
        }
        
        logger.debug(f"Generated mock voiceover: {output_path} ({duration}s)")
        return result

    def get_available_voices(self) -> Dict[str, Any]:
        return {
            "mock_voice_1": {
                "name": "Mock Voice 1",
                "language": "en-US",
                "gender": "neutral"
            },
            "mock_voice_2": {
                "name": "Mock Voice 2",
                "language": "en-US",
                "gender": "neutral"
            }
        }

    def _estimate_duration(self, text: str) -> float:
        words = len(text.split())
        return max(1.0, words * 0.4)

    def _create_mock_audio(self, duration: float, output_path: Path):
        num_samples = int(duration * self.sample_rate)
        frequency = 440.0
        
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            
            for i in range(num_samples):
                value = int(32767.0 * 0.1 * math.sin(2.0 * math.pi * frequency * i / self.sample_rate))
                data = struct.pack('<h', value)
                wav_file.writeframes(data)
