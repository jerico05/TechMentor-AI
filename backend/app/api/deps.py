"""Router-scoped dependencies (factories that build repositories)."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import DBSession
from app.repositories import StudentProfileRepository, UserRepository


def get_user_repository(db: DBSession) -> UserRepository:
    return UserRepository(db)


def get_profile_repository(db: DBSession) -> StudentProfileRepository:
    return StudentProfileRepository(db)


UserRepoDep = Depends(get_user_repository)
ProfileRepoDep = Depends(get_profile_repository)
