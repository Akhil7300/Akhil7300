import logging
from typing import Dict, Any
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ai.interfaces.thumbnail_service import ThumbnailService

logger = logging.getLogger(__name__)


class MockThumbnailService(ThumbnailService):
    def __init__(self):
        logger.info("Initialized MockThumbnailService")

    def generate_thumbnail(
        self,
        prompt: str,
        output_path: Path,
        width: int = 1280,
        height: int = 720,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"Generating mock thumbnail: {prompt[:50]}...")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.new('RGB', (width, height), color=(255, 100, 100))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = "THUMBNAIL"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        prompt_lines = self._wrap_text(prompt, 30)
        y_offset = y + text_height + 20
        try:
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            small_font = ImageFont.load_default()
        
        for line in prompt_lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=small_font)
            line_width = bbox[2] - bbox[0]
            x_line = (width - line_width) // 2
            draw.text((x_line, y_offset), line, fill=(255, 255, 255), font=small_font)
            y_offset += 30
        
        img.save(output_path)
        
        result = {
            "path": str(output_path),
            "width": width,
            "height": height,
            "metadata": {
                "type": "mock",
                "prompt": prompt,
            }
        }
        
        logger.debug(f"Generated mock thumbnail: {output_path}")
        return result

    def generate_thumbnail_from_video(
        self,
        video_path: Path,
        output_path: Path,
        timestamp: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"Extracting mock thumbnail from video at {timestamp}s")
        return self.generate_thumbnail(
            prompt=f"Frame from {video_path.name}",
            output_path=output_path,
            **kwargs
        )

    def _wrap_text(self, text: str, max_chars: int):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if sum(len(w) for w in current_line) + len(current_line) + len(word) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
