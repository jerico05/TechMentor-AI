"""Async SQLAlchemy session/engine wiring."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _build_connect_args() -> dict:
    """Driver-specific connect args.

    Neon (and most managed Postgres) require SSL. We pass `ssl=prefer` so the
    engine works both locally (no SSL) and against Neon (SSL required).
    """
    if settings.database_url.startswith("postgresql+asyncpg://"):
        return {"ssl": "prefer", "timeout": 20}
    return {}


# `pool_pre_ping` ensures stale pooled connections are recycled — important with
# serverless Postgres (Neon) that may idle-timeout and suspend compute.
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug and not settings.is_production,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,  # recycle connections every 30 min (Neon cold-starts)
    connect_args=_build_connect_args(),
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a scoped async session.

    Commits on success, rolls back on exception, always closes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context-manager flavor for use outside FastAPI (workers, scripts)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
