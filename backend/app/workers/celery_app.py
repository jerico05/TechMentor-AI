"""Celery application."""

from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "techmentor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.tasks.cv_tasks",
        "app.workers.tasks.github_tasks",
        "app.workers.tasks.rag_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
