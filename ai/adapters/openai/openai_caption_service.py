import logging
from typing import List, Dict, Any
from pathlib import Path
from openai import OpenAI
from ai.interfaces.caption_service import CaptionService
from ai.exceptions import CaptionError, APIError

logger = logging.getLogger(__name__)


class OpenAICaptionService(CaptionService):
    def __init__(self, api_key: str, model: str = "whisper-1"):
        if not api_key:
            raise CaptionError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAICaptionService with model {model}")

    def generate_captions(
        self,
        text: str,
        duration: float,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating captions for {duration}s")
        
        words_per_caption = kwargs.get("words_per_caption", 7)
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
        logger.info(f"Transcribing audio with Whisper: {audio_path}")
        
        try:
            with open(audio_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            captions = []
            if hasattr(response, 'words') and response.words:
                words_per_caption = kwargs.get("words_per_caption", 7)
                words = response.words
                
                for i in range(0, len(words), words_per_caption):
                    caption_words = words[i:i + words_per_caption]
                    text = " ".join([w.word for w in caption_words])
                    start = caption_words[0].start
                    end = caption_words[-1].end
                    
                    captions.append({
                        "text": text,
                        "start": start,
                        "end": end,
                    })
            else:
                text = response.text
                duration = kwargs.get("duration", 30.0)
                captions = self.generate_captions(text, duration)
            
            logger.debug(f"Transcribed audio into {len(captions)} captions")
            return captions
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise APIError(f"OpenAI Whisper API error: {e}")

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
