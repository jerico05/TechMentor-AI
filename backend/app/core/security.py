"""Security helpers: password hashing (bcrypt) + JWT tokens.

Token kinds:
- access  : short-lived bearer token (Authorization: Bearer ...)
- refresh : long-lived, only accepted on /auth/refresh
- reset   : single-use password reset token
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import UnauthorizedError

# bcrypt is the industry standard; `bcrypt` rounds are managed by passlib.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

TokenKind = Literal["access", "refresh", "reset"]


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    return pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def _create_token(
    subject: str,
    kind: TokenKind,
    *,
    extra: dict[str, Any] | None = None,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": kind,
        "jti": str(uuid.uuid4()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> tuple[str, int]:
    """Return (token, expires_in_seconds)."""
    delta = timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(subject, "access", extra=extra, expires_delta=delta), int(delta.total_seconds())


def create_refresh_token(subject: str) -> str:
    delta = timedelta(days=settings.refresh_token_expire_days)
    return _create_token(subject, "refresh", expires_delta=delta)


def create_password_reset_token(subject: str) -> str:
    delta = timedelta(hours=settings.password_reset_token_expire_hours)
    return _create_token(subject, "reset", expires_delta=delta)


def decode_token(token: str, expected_kind: TokenKind) -> dict[str, Any]:
    """Decode + validate kind. Raises `UnauthorizedError` on any failure."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    if payload.get("type") != expected_kind:
        raise UnauthorizedError("Wrong token type")
    return payload
