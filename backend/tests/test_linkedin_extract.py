"""Tests for LinkedIn LLM parsing fallbacks."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.utils.linkedin_extract import _parse_with_llm


@pytest.mark.asyncio
async def test_parse_with_llm_fallback_on_invalid_json():
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="not json at all"))]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    with patch("app.utils.linkedin_extract.settings") as mock_settings, patch(
        "app.utils.linkedin_extract.get_llm_client", return_value=mock_client
    ):
        mock_settings.mistral_api_key = "test-key"
        mock_settings.mistral_default_model = "test-model"

        result = await _parse_with_llm("Développeur Python chez Acme. Skills: FastAPI, Docker.", "https://linkedin.com/in/jane")

    assert result["profile_url"] == "https://linkedin.com/in/jane"
    assert "Python" in (result["summary"] or "")
    assert result["experiences"] == []


@pytest.mark.asyncio
async def test_parse_with_llm_parses_valid_json():
    payload = {
        "headline": "Dev Full Stack",
        "summary": "5 ans d'expérience",
        "experiences": [{"title": "Dev", "company": "Acme", "duration": "2022-2024"}],
        "education": [],
        "skills": ["Python"],
    }
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    with patch("app.utils.linkedin_extract.settings") as mock_settings, patch(
        "app.utils.linkedin_extract.get_llm_client", return_value=mock_client
    ):
        mock_settings.mistral_api_key = "test-key"
        mock_settings.mistral_default_model = "test-model"

        result = await _parse_with_llm("texte linkedin", "https://linkedin.com/in/jane")

    assert result["headline"] == "Dev Full Stack"
    assert result["skills"] == ["Python"]
