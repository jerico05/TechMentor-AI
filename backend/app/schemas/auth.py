"""Auth-related schemas (Firebase session sync)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class SessionSync(BaseModel):
    """Optional profile fields sent after Firebase sign-up (email/password)."""

    firstname: str | None = Field(default=None, min_length=1, max_length=80)
    lastname: str | None = Field(default=None, min_length=1, max_length=80)


class UserPublic(ORMModel):
    """What we expose publicly about a user."""

    public_id: str
    firstname: str
    lastname: str
    email: EmailStr
    email_verified: bool
    oauth_provider: Literal["local", "google", "github"]
    has_password: bool
