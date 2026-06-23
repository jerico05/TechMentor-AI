"""LLM client (OpenAI-compatible API - Groq, Mistral, etc.)."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.core.config import settings

_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.mistral_api_key,
            base_url=settings.mistral_base_url,
            timeout=settings.llm_timeout_seconds,
        )
    return _client
