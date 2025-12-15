import logging
from typing import Dict, Any
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from ai.interfaces.voiceover_service import VoiceoverService
from ai.exceptions import VoiceoverError, APIError

logger = logging.getLogger(__name__)


class ElevenLabsVoiceoverService(VoiceoverService):
    def __init__(self, api_key: str, voice_id: str = None):
        if not api_key:
            raise VoiceoverError("ElevenLabs API key is required")
        
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"
        logger.info(f"Initialized ElevenLabsVoiceoverService with voice {self.voice_id}")

    def generate_voiceover(
        self,
        text: str,
        output_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"Generating voiceover with ElevenLabs for text of length {len(text)}")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            voice_id = kwargs.get("voice_id", self.voice_id)
            model = kwargs.get("model", "eleven_monolingual_v1")
            
            audio_generator = self.client.generate(
                text=text,
                voice=voice_id,
                model=model
            )
            
            save(audio_generator, str(output_path))
            
            duration = self._estimate_duration(text)
            
            result = {
                "path": str(output_path),
                "duration": duration,
                "metadata": {
                    "voice_id": voice_id,
                    "model": model,
                    "text_length": len(text),
                }
            }
            
            logger.debug(f"Generated voiceover: {output_path} ({duration}s)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating voiceover: {e}")
            raise APIError(f"ElevenLabs API error: {e}")

    def get_available_voices(self) -> Dict[str, Any]:
        logger.info("Fetching available voices from ElevenLabs")
        
        try:
            response = self.client.voices.get_all()
            voices = {}
            
            for voice in response.voices:
                voices[voice.voice_id] = {
                    "name": voice.name,
                    "category": voice.category if hasattr(voice, 'category') else 'unknown',
                    "labels": voice.labels if hasattr(voice, 'labels') else {},
                }
            
            logger.debug(f"Retrieved {len(voices)} voices")
            return voices
            
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            raise APIError(f"ElevenLabs API error: {e}")

    def _estimate_duration(self, text: str) -> float:
        words = len(text.split())
        return max(1.0, words * 0.4)
