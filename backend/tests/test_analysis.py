"""Analysis & careers tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_careers(client: AsyncClient) -> None:
    response = await client.get("/api/v1/careers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert any(c["slug"] == "backend-developer" for c in data)


@pytest.mark.asyncio
async def test_run_analysis(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/v1/analysis/run",
        headers=auth_headers,
        json={"career_path_id": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "owned_skills" in data
    assert "missing_skills" in data
