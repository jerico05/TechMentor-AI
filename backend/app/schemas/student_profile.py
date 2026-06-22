"""Student profile schemas (Module 2)."""

from __future__ import annotations

from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field

from app.schemas.common import ORMModel

AcademicLevelStr = Literal["licence1", "licence2", "licence3", "master1", "master2", "other"]


class StudentProfileUpsert(BaseModel):
    """Payload for creating or updating the current user's profile."""

    university: str | None = Field(default=None, max_length=255)
    department: str | None = Field(default=None, max_length=255)
    academic_level: AcademicLevelStr = "licence3"
    career_goal: str | None = Field(default=None, max_length=255)
    career_path_id: int | None = None
    github_url: AnyHttpUrl | None = None
    bio: str | None = Field(default=None, max_length=2000)


class StudentProfileOut(ORMModel):
    id: int
    user_id: int
    university: str | None
    department: str | None
    academic_level: AcademicLevelStr
    career_goal: str | None
    career_path_id: int | None
    github_url: str | None
    bio: str | None
