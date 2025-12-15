from abc import ABC, abstractmethod
from typing import List, Dict, Any


class MetadataService(ABC):
    @abstractmethod
    def generate_metadata(
        self,
        content: str,
        context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video metadata from content.
        
        Args:
            content: Main content/script for the video
            context: Additional context for generation
            **kwargs: Additional parameters
            
        Returns:
            Dict containing:
                - title: Generated video title
                - description: Generated description
                - tags: List of relevant tags
                - metadata: Additional metadata
        """
        pass

    @abstractmethod
    def generate_title(
        self,
        content: str,
        max_length: int = 100,
        **kwargs
    ) -> str:
        """
        Generate a video title.
        
        Args:
            content: Content to base title on
            max_length: Maximum title length
            **kwargs: Additional parameters
            
        Returns:
            Generated title string
        """
        pass

    @abstractmethod
    def generate_description(
        self,
        content: str,
        max_length: int = 5000,
        **kwargs
    ) -> str:
        """
        Generate a video description.
        
        Args:
            content: Content to base description on
            max_length: Maximum description length
            **kwargs: Additional parameters
            
        Returns:
            Generated description string
        """
        pass

    @abstractmethod
    def generate_tags(
        self,
        content: str,
        max_tags: int = 20,
        **kwargs
    ) -> List[str]:
        """
        Generate relevant tags.
        
        Args:
            content: Content to base tags on
            max_tags: Maximum number of tags
            **kwargs: Additional parameters
            
        Returns:
            List of tag strings
        """
        pass
