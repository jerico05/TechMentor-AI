"""Embedding client via RodiumAI (OpenAI-compatible)."""

from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embedding_client() -> OpenAI:
    return OpenAI(
        api_key=settings.rodium_api_key,
        base_url=settings.rodium_base_url,
        timeout=settings.rodium_timeout_seconds,
    )


def embed_query(text: str) -> list[float]:
    client = get_embedding_client()
    response = client.embeddings.create(
        model=settings.rodium_embedding_model,
        input=text,
    )
    return response.data[0].embedding
