"""Project recommendations (Module 12)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.schemas.mvp import ProjectRecommendationOut
from app.services.project_service import ProjectService

router = APIRouter()


def get_project_service(db: DBSession) -> ProjectService:
    return ProjectService(db)


@router.get("/recommendations", response_model=ProjectRecommendationOut, summary="Recommended projects")
async def get_recommendations(
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRecommendationOut:
    data = await service.recommend(current.id)
    return ProjectRecommendationOut.model_validate(data)
