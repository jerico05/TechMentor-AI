"""Health & readiness endpoints (unauthenticated).

`/health`  - liveness probe: process is up.
`/health/ready` - readiness probe: DB + Redis + Qdrant reachable.
"""

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)


@router.get("", summary="Liveness probe")
async def liveness() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "env": settings.app_env}


@router.get("/rag", summary="RAG stack status (Qdrant + embeddings)")
async def rag_status() -> dict:
    from app.rag.status import get_rag_status

    return await get_rag_status()


@router.get("/ready", summary="Readiness probe")
async def readiness() -> JSONResponse:
    """Check infra dependencies. Returns 503 if any critical dep is down."""
    from app.database.session import engine

    checks: dict[str, str] = {}
    overall = "ok"

    # ---- Database ----
    checks["database_host"] = settings.database_host
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            user_count = await conn.execute(text("SELECT COUNT(*) FROM users"))
            checks["database_users"] = int(user_count.scalar_one())
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {type(exc).__name__}"
        overall = "degraded"

    # ---- Redis (optional in dev) ----
    checks["redis"] = await _check_redis()
    checks["qdrant"] = await _check_qdrant()

    from app.rag.status import get_rag_status

    rag = await get_rag_status()
    checks["rag"] = str(rag.get("ready", "unknown"))
    checks["rag_embeddings"] = str(rag.get("embeddings", "unknown"))
    checks["rag_points"] = int(rag.get("points", 0))

    code = status.HTTP_200_OK if overall == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content={"status": overall, "checks": checks, "rag": rag})


async def _check_qdrant() -> str:
    from app.rag.qdrant_store import check_qdrant_health

    return await check_qdrant_health()


async def _check_redis() -> str:
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.redis_url, socket_connect_timeout=2)
        try:
            pong = await client.ping()
            return "ok" if pong else "error: no pong"
        finally:
            await client.aclose()
    except Exception as exc:  # noqa: BLE001
        logger.warning("redis_health_failed", error=str(exc))
        return f"error: {type(exc).__name__}"
