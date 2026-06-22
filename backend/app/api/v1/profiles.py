"""Student profile endpoints (Module 2).

The profile is 1-1 with the authenticated user, so we expose `/profiles/me`
(RESTfully, the resource is the user's own profile).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, DBSession
from app.api.deps import get_profile_repository
from app.core.exceptions import NotFoundError
from app.repositories import StudentProfileRepository
from app.schemas.common import MessageResponse
from app.schemas.student_profile import StudentProfileOut, StudentProfileUpsert

router = APIRouter()


@router.get(
    "/me",
    response_model=StudentProfileOut | None,
    summary="Get the current user's profile",
)
async def get_my_profile(
    current: CurrentUser,
    repo: StudentProfileRepository = Depends(get_profile_repository),
) -> StudentProfileOut | None:
    profile = await repo.get_for_user(current.id)
    return StudentProfileOut.model_validate(profile) if profile else None


@router.put(
    "/me",
    response_model=StudentProfileOut,
    status_code=status.HTTP_200_OK,
    summary="Create or update the current user's profile",
)
async def upsert_my_profile(
    payload: StudentProfileUpsert,
    current: CurrentUser,
    repo: StudentProfileRepository = Depends(get_profile_repository),
) -> StudentProfileOut:
    data = payload.model_dump(exclude_unset=True)
    if github := data.get("github_url"):
        data["github_url"] = str(github)
    profile = await repo.upsert_for_user(current.id, data)
    await repo.db.commit()
    return StudentProfileOut.model_validate(profile)


@router.delete(
    "/me",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete the current user's profile",
)
async def delete_my_profile(
    current: CurrentUser,
    repo: StudentProfileRepository = Depends(get_profile_repository),
) -> MessageResponse:
    profile = await repo.get_for_user(current.id)
    if profile is None:
        raise NotFoundError("Profile not found")
    await repo.delete(profile)
    await repo.db.commit()
    return MessageResponse(message="Profile deleted")
