import logging
from typing import List, Dict, Any
from ai.interfaces.metadata_service import MetadataService

logger = logging.getLogger(__name__)


class MockMetadataService(MetadataService):
    def __init__(self):
        logger.info("Initialized MockMetadataService")

    def generate_metadata(
        self,
        content: str,
        context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info("Generating mock metadata")
        
        title = self.generate_title(content)
        description = self.generate_description(content)
        tags = self.generate_tags(content)
        
        result = {
            "title": title,
            "description": description,
            "tags": tags,
            "metadata": {
                "type": "mock",
                "content_length": len(content),
                "context": context or {},
            }
        }
        
        logger.debug(f"Generated metadata: {title}")
        return result

    def generate_title(
        self,
        content: str,
        max_length: int = 100,
        **kwargs
    ) -> str:
        words = content.split()[:10]
        title = " ".join(words)
        
        if len(title) > max_length:
            title = title[:max_length - 3] + "..."
        
        return title or "Mock Video Title"

    def generate_description(
        self,
        content: str,
        max_length: int = 5000,
        **kwargs
    ) -> str:
        description = f"Mock video description based on content.\n\n{content}"
        
        if len(description) > max_length:
            description = description[:max_length - 3] + "..."
        
        return description

    def generate_tags(
        self,
        content: str,
        max_tags: int = 20,
        **kwargs
    ) -> List[str]:
        words = content.lower().split()
        unique_words = []
        seen = set()
        
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum())
            if clean_word and len(clean_word) > 3 and clean_word not in seen:
                unique_words.append(clean_word)
                seen.add(clean_word)
                if len(unique_words) >= max_tags:
                    break
        
        if not unique_words:
            return ["mock", "video", "content"]
        
        return unique_words
