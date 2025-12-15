import logging
from typing import Dict, Any
from pathlib import Path
import requests
from PIL import Image
import io
from ai.interfaces.thumbnail_service import ThumbnailService
from ai.exceptions import ThumbnailError, APIError

logger = logging.getLogger(__name__)


class StabilityThumbnailService(ThumbnailService):
    def __init__(self, api_key: str, engine: str = "stable-diffusion-xl-1024-v1-0"):
        if not api_key:
            raise ThumbnailError("Stability API key is required")
        
        self.api_key = api_key
        self.engine = engine
        self.base_url = "https://api.stability.ai"
        logger.info(f"Initialized StabilityThumbnailService with engine {engine}")

    def generate_thumbnail(
        self,
        prompt: str,
        output_path: Path,
        width: int = 1280,
        height: int = 720,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"Generating thumbnail with Stability AI: {prompt[:50]}...")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self._generate_image(prompt, output_path, width, height, **kwargs)
            
            result = {
                "path": str(output_path),
                "width": width,
                "height": height,
                "metadata": {
                    "engine": self.engine,
                    "prompt": prompt,
                }
            }
            
            logger.debug(f"Generated thumbnail: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            raise APIError(f"Stability API error: {e}")

    def generate_thumbnail_from_video(
        self,
        video_path: Path,
        output_path: Path,
        timestamp: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"Extracting thumbnail from video at {timestamp}s")
        
        try:
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(str(video_path))
            frame = video.get_frame(timestamp)
            video.close()
            
            image = Image.fromarray(frame)
            image.save(output_path)
            
            result = {
                "path": str(output_path),
                "width": image.width,
                "height": image.height,
                "metadata": {
                    "source": str(video_path),
                    "timestamp": timestamp,
                }
            }
            
            logger.debug(f"Extracted thumbnail: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting thumbnail: {e}")
            raise ThumbnailError(f"Failed to extract thumbnail: {e}")

    def _generate_image(self, prompt: str, output_path: Path, width: int, height: int, **kwargs):
        steps = kwargs.get("steps", 30)
        cfg_scale = kwargs.get("cfg_scale", 7.0)
        
        url = f"{self.base_url}/v1/generation/{self.engine}/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "text_prompts": [{"text": prompt, "weight": 1.0}],
            "cfg_scale": cfg_scale,
            "height": height,
            "width": width,
            "steps": steps,
            "samples": 1,
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise APIError(f"Stability API error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        if "artifacts" not in data or not data["artifacts"]:
            raise APIError("No image artifacts returned from Stability API")
        
        import base64
        image_data = base64.b64decode(data["artifacts"][0]["base64"])
        image = Image.open(io.BytesIO(image_data))
        image.save(output_path)
