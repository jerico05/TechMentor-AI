"""Student profile business logic."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.student_profile import StudentProfile
from app.repositories.student_profile_repository import StudentProfileRepository


class ProfileService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = StudentProfileRepository(db)

    async def get_for_user(self, user_id: int) -> StudentProfile | None:
        return await self.repo.get_for_user(user_id)

    async def upsert_for_user(self, user_id: int, data: dict[str, Any]) -> StudentProfile:
        profile = await self.repo.upsert_for_user(user_id, data)
        await self.db.commit()
        return profile

    async def delete_for_user(self, user_id: int) -> None:
        profile = await self.repo.get_for_user(user_id)
        if profile is None:
            raise NotFoundError("Profile not found")
        await self.repo.delete(profile)
        await self.db.commit()
