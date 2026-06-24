"""FastAPI application factory.

Run locally with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.health import router as health_router
from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.firebase import warmup_firebase
from app.database.session import AsyncSessionLocal
from app.data.seed_careers import seed_career_catalog
from app.rag.embeddings import verify_embeddings
from app.rag.ingest import ingest_knowledge_base

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown lifecycle."""
    configure_logging()
    logger.info(
        "app.starting",
        env=settings.app_env,
        debug=settings.app_debug,
        api_prefix=settings.api_v1_prefix,
    )
    # Ensure the upload directory exists.
    _ = settings.upload_path
    async with AsyncSessionLocal() as db:
        await seed_career_catalog(db)
    await asyncio.to_thread(warmup_firebase)
    if os.environ.get("SKIP_RAG_INGEST") != "1":
        try:
            indexed = await asyncio.to_thread(ingest_knowledge_base)
            if indexed:
                logger.info("rag.startup.ingested", points=indexed)
        except Exception as exc:
            logger.error("rag.startup.ingest_failed", error=str(exc))
    embed_status = await verify_embeddings()
    if embed_status == "ok":
        logger.info("rag.startup.embeddings_ok")
    else:
        logger.error("rag.startup.embeddings_unavailable", detail=embed_status)
    yield
    logger.info("app.stopping")


def create_app() -> FastAPI:
    """Application factory - wires middlewares, routers, handlers."""
    app = FastAPI(
        title=settings.app_name,
        description="TechMentor AI - intelligent academic & career mentor for CS students.",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ---- Middlewares (order matters: outermost first) ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o).rstrip("/") for o in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    # ---- Exception handlers ----
    register_exception_handlers(app)

    # ---- Routes ----
    app.include_router(health_router)

    v1 = APIRouter(prefix=settings.api_v1_prefix)
    v1.include_router(api_router)
    app.include_router(v1)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"service": settings.app_name, "status": "running", "docs": "/docs"}

    return app


app = create_app()
