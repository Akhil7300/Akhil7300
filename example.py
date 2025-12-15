#!/usr/bin/env python3
"""
Example script demonstrating the AI services layer usage.

This script shows how to create a complete video using the VideoOrchestrator.
It will use mock services if API keys are not configured.
"""

import logging
from ai import VideoOrchestrator, AIServiceConfig
from ai.factory import ServiceFactory
from ai.utils import setup_logging

setup_logging(level="INFO")

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting AI video generation example")
    
    config = AIServiceConfig()
    
    if config.use_mock_services or not any([
        config.openai_api_key,
        config.elevenlabs_api_key,
        config.stability_api_key
    ]):
        logger.warning(
            "No API keys configured. Using mock services. "
            "Set API keys in .env file for real AI generation."
        )
    
    orchestrator = ServiceFactory.create_orchestrator(config)
    
    script = """
    Welcome to this demonstration of automated video creation using AI.
    
    In this video, we explore how artificial intelligence can generate
    engaging visual content, professional voiceovers, and comprehensive
    metadata automatically.
    
    The system uses multiple AI services working together to create
    polished video content with minimal human intervention.
    
    This represents the future of content creation, where AI assists
    creators in producing high-quality videos efficiently.
    """
    
    scene_prompts = [
        "A futuristic AI laboratory with glowing servers and holograms",
        "Neural network visualization with interconnected nodes",
        "A person using advanced technology, digital overlay effects",
        "Robotic arm creating art, demonstrating AI creativity",
        "Global network connections, earth from space with data streams",
    ]
    
    logger.info("Creating video...")
    
    try:
        result = orchestrator.create_video(
            script=script,
            scene_prompts=scene_prompts,
            output_filename="ai_demo_video.mp4",
            add_captions=False
        )
        
        logger.info("=" * 60)
        logger.info("Video creation successful!")
        logger.info("=" * 60)
        logger.info(f"Video path: {result['video_path']}")
        logger.info(f"Thumbnail path: {result['thumbnail_path']}")
        logger.info(f"Captions path: {result['captions_path']}")
        logger.info(f"Duration: {result['duration']:.2f} seconds")
        logger.info("")
        logger.info("Metadata:")
        logger.info(f"  Title: {result['metadata']['title']}")
        logger.info(f"  Description: {result['metadata']['description'][:100]}...")
        logger.info(f"  Tags: {', '.join(result['metadata']['tags'][:10])}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error creating video: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
