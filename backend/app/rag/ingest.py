"""Ingest static knowledge base into Qdrant."""

from __future__ import annotations

import json
from pathlib import Path

from qdrant_client.http import models as qmodels

from app.core.logging import get_logger
from app.rag.embeddings import embed_query
from app.rag.qdrant_store import collection_point_count, get_qdrant_client, upsert_chunks

logger = get_logger(__name__)

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def _chunk_text(text: str, max_chars: int = 800) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + max_chars])
        start += max_chars
    return chunks


def load_knowledge_documents() -> list[dict]:
    docs: list[dict] = []
    kb_file = KNOWLEDGE_DIR / "kb.json"
    if kb_file.exists():
        raw = json.loads(kb_file.read_text(encoding="utf-8"))
        for item in raw:
            docs.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "category": item.get("category", "general"),
                    "content": item["content"],
                }
            )
    return docs


def ingest_knowledge_base(force: bool = False) -> int:
    """Index static KB into Qdrant. Idempotent unless force=True."""
    try:
        client = get_qdrant_client()
        if not force and collection_point_count(client) > 0:
            logger.info("rag.ingest.skipped", reason="collection_not_empty")
            return 0

        docs = load_knowledge_documents()
        if not docs:
            logger.warning("rag.ingest.empty")
            return 0

        embeddings = embed_query
        points: list[qmodels.PointStruct] = []
        idx = 0
        for doc in docs:
            for chunk in _chunk_text(doc["content"]):
                vector = embeddings(f"{doc['title']}\n{chunk}")
                points.append(
                    qmodels.PointStruct(
                        id=idx,
                        vector=vector,
                        payload={
                            "doc_id": doc["id"],
                            "title": doc["title"],
                            "category": doc["category"],
                            "content": chunk,
                        },
                    )
                )
                idx += 1

        upsert_chunks(client, points)
        logger.info("rag.ingest.done", points=len(points))
        return len(points)
    except Exception as exc:
        logger.warning("rag.ingest.failed", error=str(exc))
        return 0
