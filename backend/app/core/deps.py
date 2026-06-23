"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.firebase import verify_firebase_token_async
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

DBSession = Annotated[AsyncSession, Depends(get_db)]


def _extract_bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Token d'authentification manquant.")
    return authorization.split(" ", 1)[1].strip()


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: DBSession = None,  # type: ignore[assignment]
) -> User:
    """Resolve the user from a verified Firebase ID token."""
    token = _extract_bearer(authorization)
    claims = await verify_firebase_token_async(token)

    uid = claims.get("uid")
    if not uid:
        raise UnauthorizedError("Token Firebase sans identifiant utilisateur.")

    repo = UserRepository(db)
    user = await repo.get_by_firebase_uid(uid)
    if not user:
        auth_service = AuthService(db)
        await auth_service.get_or_sync_user(claims)
        user = await repo.get_by_firebase_uid(uid)

    if not user or not user.is_active:
        raise UnauthorizedError("Utilisateur introuvable ou inactif.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
