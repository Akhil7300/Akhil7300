import pytest

from src.services.ai_generator import AIGenerator


@pytest.mark.asyncio
async def test_generate_content_without_api_key():
    generator = AIGenerator(api_key=None)
    content = await generator.generate_content("Test Channel")

    assert "title" in content
    assert "description" in content
    assert "script" in content
    assert "tags" in content
    assert "Test Channel" in content["title"]


@pytest.mark.asyncio
async def test_generate_content_with_api_key():
    generator = AIGenerator(api_key="test_key")
    content = await generator.generate_content("Test Channel")

    assert "title" in content
    assert "description" in content
    assert "script" in content
    assert "tags" in content


@pytest.mark.asyncio
async def test_generate_content_with_template():
    generator = AIGenerator(api_key="test_key")
    content = await generator.generate_content(
        "Test Channel", content_template="Custom template"
    )

    assert content is not None
    assert isinstance(content, dict)


def test_ai_generator_model_configuration():
    generator = AIGenerator(api_key="test_key", model="gpt-3.5-turbo")
    assert generator.model == "gpt-3.5-turbo"
    assert generator.api_key == "test_key"
