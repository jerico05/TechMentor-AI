"""Embedding client via Gemini (OpenAI-compatible API)."""

from __future__ import annotations

import asyncio
from functools import lru_cache

from openai import OpenAI

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embedding_client() -> OpenAI:
    return OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
        timeout=settings.gemini_timeout_seconds,
    )


def embed_query(text: str) -> list[float]:
    client = get_embedding_client()
    response = client.embeddings.create(
        model=settings.gemini_embedding_model,
        input=text,
        dimensions=settings.embedding_dimension,
    )
    return response.data[0].embedding


async def embed_query_async(text: str) -> list[float]:
    """Non-blocking wrapper for use inside async handlers."""
    return await asyncio.to_thread(embed_query, text)
