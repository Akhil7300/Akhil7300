import logging
from typing import List, Dict, Any
from pathlib import Path
from ai.interfaces.caption_service import CaptionService

logger = logging.getLogger(__name__)


class MockCaptionService(CaptionService):
    def __init__(self):
        logger.info("Initialized MockCaptionService")

    def generate_captions(
        self,
        text: str,
        duration: float,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating mock captions for {duration}s")
        
        words_per_caption = kwargs.get("words_per_caption", 5)
        words = text.split()
        
        captions = []
        time_per_word = duration / len(words) if words else 0
        
        for i in range(0, len(words), words_per_caption):
            caption_words = words[i:i + words_per_caption]
            start_time = i * time_per_word
            end_time = min((i + len(caption_words)) * time_per_word, duration)
            
            captions.append({
                "text": " ".join(caption_words),
                "start": start_time,
                "end": end_time,
            })
        
        logger.debug(f"Generated {len(captions)} captions")
        return captions

    def save_captions_srt(
        self,
        captions: List[Dict[str, Any]],
        output_path: Path
    ) -> Path:
        logger.info(f"Saving captions to SRT: {output_path}")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for idx, caption in enumerate(captions, start=1):
                f.write(f"{idx}\n")
                f.write(f"{self._format_time(caption['start'])} --> {self._format_time(caption['end'])}\n")
                f.write(f"{caption['text']}\n\n")
        
        logger.debug(f"Saved {len(captions)} captions to {output_path}")
        return output_path

    def transcribe_audio(
        self,
        audio_path: Path,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"Mock transcribing audio: {audio_path}")
        
        mock_text = "This is a mock transcription of the audio file. " * 5
        mock_duration = 30.0
        
        return self.generate_captions(mock_text, mock_duration)

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
