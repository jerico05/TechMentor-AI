"""Auth service — sync Firebase-authenticated users to the local database.

Login, register, OAuth and password reset are handled by Firebase Auth on the
client. The backend verifies ID tokens and maintains a local `User` record for
profiles, RAG context, etc.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.firebase import enrich_claims_email, map_firebase_provider
from app.core.logging import get_logger
from app.repositories.user_repository import UserRepository
from app.schemas.auth import SessionSync, UserPublic

logger = get_logger(__name__)


class AuthService:
    """Firebase-backed auth orchestration."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def sync_user(
        self,
        firebase_claims: dict,
        profile: SessionSync | None = None,
    ) -> UserPublic:
        """Create or update a local user from verified Firebase claims."""
        firebase_claims = enrich_claims_email(firebase_claims)
        uid = firebase_claims.get("uid")
        if not uid:
            raise UnauthorizedError("Token Firebase sans identifiant utilisateur.")

        email = (firebase_claims.get("email") or "").strip().lower()
        email_verified = bool(firebase_claims.get("email_verified", False))
        provider = map_firebase_provider(firebase_claims)
        firstname, lastname = self._resolve_names(firebase_claims, profile)

        existing = await self.user_repo.get_by_firebase_uid(uid)
        if existing:
            updates: dict = {}
            if email and existing.email != email:
                if await self.user_repo.email_taken_by_other(email, existing.id):
                    raise ConflictError("Cet email est déjà utilisé par un autre compte.")
                updates["email"] = email
            if email_verified and not existing.email_verified:
                updates["email_verified"] = True
            if profile and profile.firstname:
                updates["firstname"] = profile.firstname
            if profile and profile.lastname:
                updates["lastname"] = profile.lastname
            if updates:
                await self.user_repo.update_fields(existing, **updates)
                await self.db.commit()
                await self.db.refresh(existing)
            return user_to_public(existing)

        if email:
            by_email = await self.user_repo.get_by_email(email)
            if by_email:
                if by_email.firebase_uid and by_email.firebase_uid != uid:
                    raise ConflictError("Cet email est déjà lié à un autre compte Firebase.")
                await self.user_repo.update_fields(
                    by_email,
                    firebase_uid=uid,
                    oauth_provider=provider,
                    oauth_subject=uid,
                    email_verified=by_email.email_verified or email_verified,
                    firstname=profile.firstname if profile and profile.firstname else by_email.firstname,
                    lastname=profile.lastname if profile and profile.lastname else by_email.lastname,
                )
                await self.db.commit()
                await self.db.refresh(by_email)
                logger.info("auth.user_linked", user_id=by_email.id, firebase_uid=uid)
                return user_to_public(by_email)

        if not email:
            # Last resort for OAuth providers that hide email (GitHub private).
            email = f"{uid}@oauth.techmentor.local"
            email_verified = False
            logger.warning("auth.email_placeholder", uid=uid, provider=provider)

        user = await self.user_repo.create_user(
            firstname=firstname,
            lastname=lastname,
            email=email,
            firebase_uid=uid,
            oauth_provider=provider,
            oauth_subject=uid,
            email_verified=email_verified,
        )
        await self.db.commit()
        await self.db.refresh(user)
        logger.info("auth.user_created", user_id=user.id, firebase_uid=uid, provider=provider)
        return user_to_public(user)

    async def get_or_sync_user(
        self,
        firebase_claims: dict,
        profile: SessionSync | None = None,
    ) -> UserPublic:
        """Return the local user, creating one on first sight if possible."""
        uid = firebase_claims.get("uid")
        if not uid:
            raise UnauthorizedError("Token Firebase sans identifiant utilisateur.")

        existing = await self.user_repo.get_by_firebase_uid(uid)
        if existing:
            return user_to_public(existing)

        return await self.sync_user(firebase_claims, profile)

    @staticmethod
    def _resolve_names(
        claims: dict,
        profile: SessionSync | None,
    ) -> tuple[str, str]:
        if profile and profile.firstname and profile.lastname:
            return profile.firstname, profile.lastname

        display = (claims.get("name") or "").strip()
        if display:
            parts = display.split(maxsplit=1)
            return parts[0], parts[1] if len(parts) > 1 else ""

        email = claims.get("email") or ""
        local = email.split("@")[0] if email else "Utilisateur"
        return local, ""


def user_to_public(user) -> UserPublic:  # type: ignore[no-untyped-def]
    """Map an ORM User to the public-safe schema."""
    return UserPublic(
        public_id=user.public_id,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        email_verified=user.email_verified,
        oauth_provider=user.oauth_provider,
        has_password=user.has_password,
    )
