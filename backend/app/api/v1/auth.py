"""Authentication endpoints (Firebase-backed).

The client authenticates via Firebase Auth and sends the ID token as
`Authorization: Bearer <firebase_id_token>`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, status

from app.core.deps import CurrentUser, DBSession, _extract_bearer
from app.core.firebase import enrich_claims_email, verify_firebase_token
from app.schemas.auth import SessionSync, UserPublic
from app.services.auth_service import AuthService, user_to_public

router = APIRouter()


def get_auth_service(db: DBSession) -> AuthService:
    return AuthService(db)


@router.post(
    "/session",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
    summary="Sync Firebase session to local user",
)
async def sync_session(
    payload: SessionSync | None = None,
    authorization: str | None = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    """Create or update the local user after Firebase sign-in/sign-up."""
    token = _extract_bearer(authorization)
    claims = enrich_claims_email(verify_firebase_token(token))
    return await auth_service.sync_user(claims, payload)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get the current authenticated user",
)
async def get_me(current: CurrentUser) -> UserPublic:
    return user_to_public(current)
