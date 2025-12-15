import logging
from typing import List, Dict, Any
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ai.interfaces.video_generator import VideoGenerator

logger = logging.getLogger(__name__)


class MockVideoGenerator(VideoGenerator):
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        logger.info("Initialized MockVideoGenerator")

    def generate_video_clips(
        self,
        prompts: List[str],
        duration_per_clip: float,
        output_dir: Path,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating {len(prompts)} mock video clips")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for idx, prompt in enumerate(prompts):
            image_path = output_dir / f"clip_{idx}.png"
            self._create_mock_image(prompt, image_path)
            
            results.append({
                "path": str(image_path),
                "prompt": prompt,
                "duration": duration_per_clip,
                "metadata": {
                    "type": "mock",
                    "index": idx,
                }
            })
            logger.debug(f"Generated mock clip {idx}: {image_path}")
        
        return results

    def generate_images(
        self,
        prompts: List[str],
        output_dir: Path,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating {len(prompts)} mock images")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for idx, prompt in enumerate(prompts):
            image_path = output_dir / f"image_{idx}.png"
            self._create_mock_image(prompt, image_path)
            
            results.append({
                "path": str(image_path),
                "prompt": prompt,
                "metadata": {
                    "type": "mock",
                    "index": idx,
                    "width": self.width,
                    "height": self.height,
                }
            })
            logger.debug(f"Generated mock image {idx}: {image_path}")
        
        return results

    def _create_mock_image(self, text: str, output_path: Path):
        img = Image.new('RGB', (self.width, self.height), color=(73, 109, 137))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text_lines = self._wrap_text(text, 50)
        y_offset = self.height // 2 - (len(text_lines) * 50) // 2
        
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_offset), line, fill=(255, 255, 255), font=font)
            y_offset += 50
        
        img.save(output_path)

    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
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
