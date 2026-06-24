"""RAG stack health (Qdrant + embeddings + indexed chunks)."""

from __future__ import annotations

import asyncio

from app.core.config import settings
from app.rag.embeddings import verify_embeddings
from app.rag.qdrant_store import check_qdrant_health, collection_point_count, get_qdrant_client


async def get_rag_status() -> dict[str, str | int]:
    qdrant = await check_qdrant_health()
    points = 0
    if qdrant == "ok":
        try:
            client = get_qdrant_client()
            points = await asyncio.to_thread(collection_point_count, client)
        except Exception:  # noqa: BLE001
            points = 0

    embeddings = await verify_embeddings()
    ready = qdrant == "ok" and embeddings == "ok" and points > 0

    return {
        "qdrant": qdrant,
        "embeddings": embeddings,
        "collection": settings.qdrant_collection,
        "points": points,
        "ready": "ok" if ready else "degraded",
    }
