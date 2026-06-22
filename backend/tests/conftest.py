"""Shared pytest fixtures."""

from __future__ import annotations

import os

# Tests skip slow RAG ingestion at startup.
os.environ.setdefault("SKIP_RAG_INGEST", "1")

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.database.session import get_db
from app.data.seed_careers import seed_career_catalog
from app.main import create_app


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


@pytest.fixture(autouse=True)
def mock_firebase_verify(monkeypatch: pytest.MonkeyPatch) -> None:
    """Accept `test-firebase-token` and reject everything else."""

    def _verify(token: str) -> dict[str, Any]:
        if token == "test-firebase-token":
            return _fake_claims()
        if token == "google-token":
            return _fake_claims(
                uid="google-uid",
                email="bob@gmail.com",
                name="Bob Google",
                provider="google.com",
            )
        from app.core.exceptions import UnauthorizedError

        raise UnauthorizedError("Token invalide.")

    monkeypatch.setattr("app.core.firebase.verify_firebase_token", _verify)
    monkeypatch.setattr("app.core.deps.verify_firebase_token", _verify)
    monkeypatch.setattr("app.api.v1.auth.verify_firebase_token", _verify)


@pytest.fixture(scope="session")
def event_loop():  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def _engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(_engine) -> AsyncIterator[AsyncSession]:
    maker = async_sessionmaker(bind=_engine, expire_on_commit=False, autoflush=False)
    async with maker() as session:
        await seed_career_catalog(session)
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    app = create_app()

    async def _override_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    headers = {"Authorization": "Bearer test-firebase-token"}
    await client.post("/api/v1/auth/session", headers=headers, json={"firstname": "Alice", "lastname": "Martin"})
    return headers
