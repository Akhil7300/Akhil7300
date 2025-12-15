import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    concatenate_videoclips,
)
from ai.interfaces import (
    VideoGenerator,
    VoiceoverService,
    ThumbnailService,
    CaptionService,
    MetadataService,
)
from ai.config import AIServiceConfig
from ai.exceptions import AIServiceError

logger = logging.getLogger(__name__)


class VideoOrchestrator:
    def __init__(
        self,
        config: AIServiceConfig,
        video_generator: VideoGenerator,
        voiceover_service: VoiceoverService,
        thumbnail_service: ThumbnailService,
        caption_service: CaptionService,
        metadata_service: MetadataService,
    ):
        self.config = config
        self.video_generator = video_generator
        self.voiceover_service = voiceover_service
        self.thumbnail_service = thumbnail_service
        self.caption_service = caption_service
        self.metadata_service = metadata_service
        
        logger.info("Initialized VideoOrchestrator")

    def create_video(
        self,
        script: str,
        scene_prompts: List[str],
        output_filename: str = "output_video.mp4",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Orchestrate the creation of a complete video.
        
        Args:
            script: The narration script
            scene_prompts: List of visual prompts for each scene
            output_filename: Name of the output video file
            **kwargs: Additional parameters
            
        Returns:
            Dict containing paths to generated assets and metadata
        """
        logger.info(f"Starting video creation: {output_filename}")
        
        try:
            temp_dir = Path(self.config.temp_dir)
            output_dir = Path(self.config.output_dir)
            
            voiceover_result = self._generate_voiceover(script, temp_dir)
            
            visuals_result = self._generate_visuals(
                scene_prompts,
                voiceover_result["duration"],
                temp_dir
            )
            
            captions_result = self._generate_captions(
                script,
                voiceover_result["duration"],
                temp_dir
            )
            
            video_path = self._stitch_video(
                visuals_result,
                voiceover_result,
                captions_result,
                output_dir / output_filename,
                **kwargs
            )
            
            thumbnail_result = self._generate_thumbnail(
                scene_prompts[0] if scene_prompts else "Video thumbnail",
                output_dir / f"{Path(output_filename).stem}_thumbnail.png"
            )
            
            metadata_result = self._generate_metadata(script)
            
            result = {
                "video_path": str(video_path),
                "thumbnail_path": thumbnail_result["path"],
                "captions_path": captions_result["srt_path"],
                "metadata": metadata_result,
                "duration": voiceover_result["duration"],
            }
            
            logger.info(f"Video creation complete: {video_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            raise AIServiceError(f"Video creation failed: {e}")

    def _generate_voiceover(self, script: str, temp_dir: Path) -> Dict[str, Any]:
        logger.info("Generating voiceover")
        audio_path = temp_dir / "voiceover.mp3"
        return self.voiceover_service.generate_voiceover(script, audio_path)

    def _generate_visuals(
        self,
        prompts: List[str],
        total_duration: float,
        temp_dir: Path
    ) -> List[Dict[str, Any]]:
        logger.info(f"Generating visuals for {len(prompts)} scenes")
        
        duration_per_clip = total_duration / len(prompts) if prompts else total_duration
        visuals_dir = temp_dir / "visuals"
        
        return self.video_generator.generate_images(prompts, visuals_dir)

    def _generate_captions(
        self,
        script: str,
        duration: float,
        temp_dir: Path
    ) -> Dict[str, Any]:
        logger.info("Generating captions")
        
        captions = self.caption_service.generate_captions(script, duration)
        srt_path = temp_dir / "captions.srt"
        self.caption_service.save_captions_srt(captions, srt_path)
        
        return {
            "captions": captions,
            "srt_path": str(srt_path),
        }

    def _generate_thumbnail(self, prompt: str, output_path: Path) -> Dict[str, Any]:
        logger.info("Generating thumbnail")
        return self.thumbnail_service.generate_thumbnail(prompt, output_path)

    def _generate_metadata(self, script: str) -> Dict[str, Any]:
        logger.info("Generating metadata")
        return self.metadata_service.generate_metadata(script)

    def _stitch_video(
        self,
        visuals: List[Dict[str, Any]],
        voiceover: Dict[str, Any],
        captions: Dict[str, Any],
        output_path: Path,
        **kwargs
    ) -> Path:
        logger.info("Stitching video with MoviePy")
        
        try:
            audio = AudioFileClip(voiceover["path"])
            total_duration = audio.duration
            
            clip_duration = total_duration / len(visuals) if visuals else total_duration
            
            video_clips = []
            for visual in visuals:
                img_clip = ImageClip(visual["path"]).set_duration(clip_duration)
                img_clip = img_clip.resize((self.config.video_width, self.config.video_height))
                video_clips.append(img_clip)
            
            final_video = concatenate_videoclips(video_clips, method="compose")
            final_video = final_video.set_audio(audio)
            
            if kwargs.get("add_captions", False):
                final_video = self._add_text_captions(final_video, captions["captions"])
            
            final_video.write_videofile(
                str(output_path),
                fps=self.config.video_fps,
                codec='libx264',
                audio_codec='aac',
                logger=None
            )
            
            final_video.close()
            audio.close()
            
            logger.info(f"Video stitched successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error stitching video: {e}")
            raise AIServiceError(f"Failed to stitch video: {e}")

    def _add_text_captions(
        self,
        video: VideoFileClip,
        captions: List[Dict[str, Any]]
    ) -> CompositeVideoClip:
        logger.debug("Adding text captions to video")
        
        caption_clips = []
        
        for caption in captions:
            try:
                txt_clip = TextClip(
                    caption["text"],
                    fontsize=40,
                    color='white',
                    bg_color='black',
                    size=(self.config.video_width * 0.8, None),
                    method='caption'
                )
                txt_clip = txt_clip.set_position(('center', 'bottom'))
                txt_clip = txt_clip.set_start(caption["start"])
                txt_clip = txt_clip.set_duration(caption["end"] - caption["start"])
                
                caption_clips.append(txt_clip)
            except Exception as e:
                logger.warning(f"Failed to create caption clip: {e}")
                continue
        
        if caption_clips:
            return CompositeVideoClip([video] + caption_clips)
        
        return video
