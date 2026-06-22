"""Profile endpoint tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upsert_and_get_profile(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "university": "Université de Lomé",
        "department": "Informatique",
        "academic_level": "licence3",
        "career_goal": "Backend Developer",
        "career_path_id": 1,
    }
    put = await client.put("/api/v1/profiles/me", headers=auth_headers, json=payload)
    assert put.status_code == 200
    assert put.json()["university"] == "Université de Lomé"

    get = await client.get("/api/v1/profiles/me", headers=auth_headers)
    assert get.status_code == 200
    assert get.json()["department"] == "Informatique"
