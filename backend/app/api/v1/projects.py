"""Project recommendations (Module 12)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.core.exceptions import ValidationError
from app.schemas.mvp import ProjectCompleteRequest, ProjectCompletionsOut, ProjectRecommendationOut
from app.services.project_service import ProjectService

router = APIRouter()


def get_project_service(db: DBSession) -> ProjectService:
    return ProjectService(db)


def _validate_title(title: str) -> str:
    cleaned = title.strip()
    if not cleaned:
        raise ValidationError("Le titre du projet est requis.")
    return cleaned


@router.get("/recommendations", response_model=ProjectRecommendationOut, summary="Recommended projects")
async def get_recommendations(
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRecommendationOut:
    data = await service.recommend(current.id)
    return ProjectRecommendationOut.model_validate(data)


@router.get("/completions", response_model=ProjectCompletionsOut, summary="Completed portfolio projects")
async def list_completions(
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectCompletionsOut:
    completed = await service.list_completions(current.id)
    return ProjectCompletionsOut(completed=completed)


@router.post("/complete", response_model=ProjectCompletionsOut, summary="Mark project as completed")
async def complete_project(
    payload: ProjectCompleteRequest,
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectCompletionsOut:
    completed = await service.mark_complete(
        current.id, _validate_title(payload.title), payload.career_slug
    )
    return ProjectCompletionsOut(completed=completed)


@router.delete("/complete", response_model=ProjectCompletionsOut, summary="Unmark completed project")
async def uncomplete_project(
    payload: ProjectCompleteRequest,
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectCompletionsOut:
    completed = await service.mark_incomplete(current.id, _validate_title(payload.title))
    return ProjectCompletionsOut(completed=completed)
