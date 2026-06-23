"""Student profile endpoints (Module 2).

The profile is 1-1 with the authenticated user, so we expose `/profiles/me`
(RESTfully, the resource is the user's own profile).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, DBSession
from app.schemas.common import MessageResponse
from app.schemas.student_profile import StudentProfileOut, StudentProfileUpsert
from app.services.profile_service import ProfileService

router = APIRouter()


def get_profile_service(db: DBSession) -> ProfileService:
    return ProfileService(db)


@router.get(
    "/me",
    response_model=StudentProfileOut | None,
    summary="Get the current user's profile",
)
async def get_my_profile(
    current: CurrentUser,
    service: ProfileService = Depends(get_profile_service),
) -> StudentProfileOut | None:
    profile = await service.get_for_user(current.id)
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
    service: ProfileService = Depends(get_profile_service),
) -> StudentProfileOut:
    data = payload.model_dump(exclude_unset=True)
    if github := data.get("github_url"):
        data["github_url"] = str(github)
    profile = await service.upsert_for_user(current.id, data)
    return StudentProfileOut.model_validate(profile)


@router.delete(
    "/me",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete the current user's profile",
)
async def delete_my_profile(
    current: CurrentUser,
    service: ProfileService = Depends(get_profile_service),
) -> MessageResponse:
    await service.delete_for_user(current.id)
    return MessageResponse(message="Profile deleted")
