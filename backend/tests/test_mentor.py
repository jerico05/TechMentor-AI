"""Mentor chat tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mentor_chat(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    mock_message = MagicMock()
    mock_message.content = "Bonjour, je suis votre mentor."
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    with patch("app.services.mentor_service.get_rodium_client", return_value=mock_client), patch(
        "app.services.mentor_service.retrieve_context", return_value=""
    ):
        response = await client.post(
            "/api/v1/mentor/chat",
            headers=auth_headers,
            json={"message": "Bonjour", "history": []},
        )
    assert response.status_code == 200
    assert "mentor" in response.json()["reply"].lower() or response.json()["reply"]
