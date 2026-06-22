"""RAG reindex Celery task."""

from __future__ import annotations

from app.rag.ingest import ingest_knowledge_base
from app.workers.celery_app import celery_app


@celery_app.task(name="rag.reindex")
def reindex_kb_task(force: bool = True) -> int:
    return ingest_knowledge_base(force=force)
