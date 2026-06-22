"""User repository."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access for `users`."""

    model = User

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_public_id(self, public_id: str) -> User | None:
        stmt = select(User).where(User.public_id == public_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_oauth(self, provider: str, subject: str) -> User | None:
        stmt = select(User).where(
            User.oauth_provider == provider,
            User.oauth_subject == subject,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        stmt = select(User).where(User.firebase_uid == firebase_uid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def email_taken_by_other(self, email: str, exclude_user_id: int) -> bool:
        stmt = select(User.id).where(User.email == email, User.id != exclude_user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create_user(
        self,
        *,
        firstname: str,
        lastname: str,
        email: str,
        firebase_uid: str | None = None,
        password_hash: str | None = None,
        oauth_provider: str = "local",
        oauth_subject: str | None = None,
        email_verified: bool = False,
    ) -> User:
        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            firebase_uid=firebase_uid,
            password_hash=password_hash,
            oauth_provider=oauth_provider,
            oauth_subject=oauth_subject,
            email_verified=email_verified,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def email_exists(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    async def update_fields(self, user: User, **fields: Any) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user
