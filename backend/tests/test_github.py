"""GitHub analysis tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_github_analyze_inline(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    mock_repos = [
        {"language": "Python", "topics": ["fastapi"]},
        {"language": "TypeScript", "topics": []},
    ]
    mock_user = {"login": "testuser", "public_repos": 2}

    with patch(
        "app.services.github_service.fetch_github_profile",
        new=AsyncMock(return_value=(mock_user, mock_repos, {"Python": 1, "TypeScript": 1}, ["fastapi"])),
    ), patch("app.utils.llm_helpers.extract_skills_from_text", new=AsyncMock(return_value=["Python"])):
        response = await client.post(
            "/api/v1/github/analyze",
            headers=auth_headers,
            json={"github_url": "https://github.com/testuser"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["username"] == "testuser"
    assert data["repo_count"] == 2
