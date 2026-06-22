"""RodiumAI gateway client (OpenAI-compatible API)."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.core.config import settings

_client: AsyncOpenAI | None = None


def get_rodium_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.rodium_api_key,
            base_url=settings.rodium_base_url,
            timeout=settings.rodium_timeout_seconds,
        )
    return _client
