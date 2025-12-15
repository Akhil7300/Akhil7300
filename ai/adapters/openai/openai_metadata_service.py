import logging
from typing import List, Dict, Any
from openai import OpenAI
from ai.interfaces.metadata_service import MetadataService
from ai.exceptions import MetadataError, APIError

logger = logging.getLogger(__name__)


class OpenAIMetadataService(MetadataService):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        if not api_key:
            raise MetadataError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAIMetadataService with model {model}")

    def generate_metadata(
        self,
        content: str,
        context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info("Generating metadata with OpenAI")
        
        try:
            prompt = self._build_metadata_prompt(content, context)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates video metadata."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            result_text = response.choices[0].message.content
            metadata = self._parse_metadata_response(result_text)
            
            logger.debug(f"Generated metadata: {metadata.get('title', '')}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating metadata: {e}")
            raise APIError(f"OpenAI API error: {e}")

    def generate_title(
        self,
        content: str,
        max_length: int = 100,
        **kwargs
    ) -> str:
        logger.info("Generating title with OpenAI")
        
        try:
            prompt = f"Generate a compelling video title (max {max_length} characters) for:\n\n{content[:500]}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative video title generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=50,
            )
            
            title = response.choices[0].message.content.strip()
            title = title.strip('"\'')
            
            if len(title) > max_length:
                title = title[:max_length - 3] + "..."
            
            logger.debug(f"Generated title: {title}")
            return title
            
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            raise APIError(f"OpenAI API error: {e}")

    def generate_description(
        self,
        content: str,
        max_length: int = 5000,
        **kwargs
    ) -> str:
        logger.info("Generating description with OpenAI")
        
        try:
            prompt = f"Generate an engaging video description (max {max_length} characters) for:\n\n{content[:1000]}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a video marketing expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            description = response.choices[0].message.content.strip()
            
            if len(description) > max_length:
                description = description[:max_length - 3] + "..."
            
            logger.debug(f"Generated description ({len(description)} chars)")
            return description
            
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            raise APIError(f"OpenAI API error: {e}")

    def generate_tags(
        self,
        content: str,
        max_tags: int = 20,
        **kwargs
    ) -> List[str]:
        logger.info("Generating tags with OpenAI")
        
        try:
            prompt = f"Generate {max_tags} relevant tags (comma-separated) for:\n\n{content[:500]}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a SEO expert specializing in video tags."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=100,
            )
            
            tags_text = response.choices[0].message.content.strip()
            tags = [tag.strip().strip('"\'') for tag in tags_text.split(',')]
            tags = [tag for tag in tags if tag][:max_tags]
            
            logger.debug(f"Generated {len(tags)} tags")
            return tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            raise APIError(f"OpenAI API error: {e}")

    def _build_metadata_prompt(self, content: str, context: Dict[str, Any] = None) -> str:
        prompt = f"Generate video metadata (title, description, and tags) for:\n\n{content[:1000]}\n\n"
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += "Return the metadata in this format:\nTitle: [title]\nDescription: [description]\nTags: [tag1, tag2, tag3, ...]"
        
        return prompt

    def _parse_metadata_response(self, response: str) -> Dict[str, Any]:
        lines = response.split('\n')
        metadata = {
            "title": "",
            "description": "",
            "tags": [],
            "metadata": {"source": "openai"}
        }
        
        for line in lines:
            if line.startswith("Title:"):
                metadata["title"] = line[6:].strip()
            elif line.startswith("Description:"):
                metadata["description"] = line[12:].strip()
            elif line.startswith("Tags:"):
                tags_text = line[5:].strip()
                metadata["tags"] = [tag.strip().strip('[]"\'') for tag in tags_text.split(',')]
        
        return metadata
