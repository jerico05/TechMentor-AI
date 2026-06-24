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


def extract_bearer_token(
    authorization: str | None,
    fallback_authorization: str | None = None,
) -> str:
    for value in (authorization, fallback_authorization):
        if value and value.lower().startswith("bearer "):
            return value.split(" ", 1)[1].strip()
    raise UnauthorizedError("Token d'authentification manquant.")


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    x_forwarded_authorization: Annotated[str | None, Header()] = None,
    db: DBSession = None,  # type: ignore[assignment]
) -> User:
    """Resolve the user from a verified Firebase ID token."""
    token = extract_bearer_token(authorization, x_forwarded_authorization)
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
