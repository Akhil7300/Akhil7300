import logging
from typing import List, Dict, Any
from pathlib import Path
import requests
from PIL import Image
import io
from ai.interfaces.video_generator import VideoGenerator
from ai.exceptions import VideoGenerationError, APIError

logger = logging.getLogger(__name__)


class StabilityVideoGenerator(VideoGenerator):
    def __init__(self, api_key: str, engine: str = "stable-diffusion-xl-1024-v1-0"):
        if not api_key:
            raise VideoGenerationError("Stability API key is required")
        
        self.api_key = api_key
        self.engine = engine
        self.base_url = "https://api.stability.ai"
        logger.info(f"Initialized StabilityVideoGenerator with engine {engine}")

    def generate_video_clips(
        self,
        prompts: List[str],
        duration_per_clip: float,
        output_dir: Path,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating {len(prompts)} video clips (as images)")
        logger.warning("Stability AI doesn't support direct video generation, falling back to images")
        
        return self.generate_images(prompts, output_dir, **kwargs)

    def generate_images(
        self,
        prompts: List[str],
        output_dir: Path,
        **kwargs
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating {len(prompts)} images with Stability AI")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for idx, prompt in enumerate(prompts):
            try:
                image_path = output_dir / f"stability_image_{idx}.png"
                self._generate_single_image(prompt, image_path, **kwargs)
                
                results.append({
                    "path": str(image_path),
                    "prompt": prompt,
                    "metadata": {
                        "engine": self.engine,
                        "index": idx,
                    }
                })
                logger.debug(f"Generated image {idx}: {image_path}")
                
            except Exception as e:
                logger.error(f"Error generating image {idx}: {e}")
                raise APIError(f"Stability API error: {e}")
        
        return results

    def _generate_single_image(self, prompt: str, output_path: Path, **kwargs):
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 1024)
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
