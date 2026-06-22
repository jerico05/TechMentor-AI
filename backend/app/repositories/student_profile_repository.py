"""Student profile repository."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student_profile import StudentProfile
from app.repositories.base import BaseRepository


class StudentProfileRepository(BaseRepository[StudentProfile]):
    """Data access for `student_profiles` (1-1 with users)."""

    model = StudentProfile

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_for_user(self, user_id: int) -> StudentProfile | None:
        stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_for_user(self, user_id: int, data: dict[str, Any]) -> StudentProfile:
        """Create the profile if missing, otherwise update the matching fields."""
        profile = await self.get_for_user(user_id)
        if profile is None:
            profile = StudentProfile(user_id=user_id, **data)
            self.db.add(profile)
        else:
            for key, value in data.items():
                setattr(profile, key, value)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile
