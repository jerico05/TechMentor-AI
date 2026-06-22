"""Auth endpoint tests (Firebase token verification mocked)."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient

from app.core.firebase import verify_firebase_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


def _fake_claims(
    *,
    uid: str = "firebase-uid-test",
    email: str = "alice@example.com",
    name: str = "Alice Martin",
    provider: str = "password",
) -> dict[str, Any]:
    return {
        "uid": uid,
        "email": email,
        "email_verified": True,
        "name": name,
        "firebase": {"sign_in_provider": provider},
    }


@pytest.mark.asyncio
async def test_sync_session_creates_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer test-firebase-token"},
        json={"firstname": "Alice", "lastname": "Martin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["firstname"] == "Alice"
    assert data["lastname"] == "Martin"
    assert data["oauth_provider"] == "local"


@pytest.mark.asyncio
async def test_sync_session_idempotent(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer test-firebase-token"}
    first = await client.post("/api/v1/auth/session", headers=headers, json={})
    second = await client.post("/api/v1/auth/session", headers=headers, json={})
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["public_id"] == second.json()["public_id"]


@pytest.mark.asyncio
async def test_get_me_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_returns_user(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer test-firebase-token"}
    await client.post("/api/v1/auth/session", headers=headers, json={})

    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_oauth_provider_mapped(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer google-token"},
        json={},
    )
    assert response.status_code == 200
    assert response.json()["oauth_provider"] == "google"


@pytest.mark.asyncio
async def test_invalid_token_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer bad-token"},
        json={},
    )
    assert response.status_code == 401
