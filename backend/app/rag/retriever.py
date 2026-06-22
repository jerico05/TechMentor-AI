"""LangChain-style retriever over Qdrant knowledge base."""

from __future__ import annotations

from app.core.logging import get_logger
from app.rag.embeddings import embed_query
from app.rag.qdrant_store import get_qdrant_client, search_similar

logger = get_logger(__name__)


def retrieve_context(query: str, limit: int = 4) -> str:
    """Return formatted RAG context for LLM prompts. Empty string if Qdrant unavailable."""
    try:
        vector = embed_query(query)
        client = get_qdrant_client()
        hits = search_similar(client, vector, limit=limit)
        if not hits:
            return ""
        lines = ["Base de connaissances pertinente :"]
        for hit in hits:
            lines.append(f"- [{hit['category']}] {hit['title']}: {hit['content']}")
        return "\n".join(lines)
    except Exception as exc:
        logger.warning("rag.retrieve.failed", error=str(exc))
        return ""


def retrieve_for_roadmap(career_name: str, missing_skills: list[str]) -> str:
    query = f"roadmap {career_name} " + " ".join(missing_skills[:5])
    return retrieve_context(query, limit=5)
