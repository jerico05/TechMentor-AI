"""Qdrant vector store helpers."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        timeout=10,
    )


def ensure_collection(client: QdrantClient) -> None:
    name = settings.qdrant_collection
    collections = {c.name for c in client.get_collections().collections}
    if name in collections:
        return
    client.create_collection(
        collection_name=name,
        vectors_config=qmodels.VectorParams(
            size=settings.embedding_dimension,
            distance=qmodels.Distance.COSINE,
        ),
    )
    logger.info("qdrant.collection.created", name=name)


def collection_point_count(client: QdrantClient) -> int:
    try:
        info = client.get_collection(settings.qdrant_collection)
        return info.points_count or 0
    except Exception:
        return 0


def upsert_chunks(client: QdrantClient, points: list[qmodels.PointStruct]) -> None:
    ensure_collection(client)
    client.upsert(collection_name=settings.qdrant_collection, points=points)


def search_similar(client: QdrantClient, vector: list[float], limit: int = 4) -> list[dict[str, Any]]:
    ensure_collection(client)
    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=vector,
        limit=limit,
    )
    return [
        {
            "score": hit.score,
            "title": hit.payload.get("title", "") if hit.payload else "",
            "content": hit.payload.get("content", "") if hit.payload else "",
            "category": hit.payload.get("category", "") if hit.payload else "",
        }
        for hit in results
    ]


async def check_qdrant_health() -> str:
    try:
        client = get_qdrant_client()
        client.get_collections()
        return "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("qdrant_health_failed", error=str(exc))
        return f"error: {type(exc).__name__}"
