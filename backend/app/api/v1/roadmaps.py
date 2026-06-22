"""Roadmap endpoints (Module 11)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.schemas.mvp import RoadmapGenerateRequest, RoadmapOut
from app.services.roadmap_service import RoadmapService

router = APIRouter()


def get_roadmap_service(db: DBSession) -> RoadmapService:
    return RoadmapService(db)


@router.post("/generate", response_model=RoadmapOut, summary="Generate personalized roadmap")
async def generate_roadmap(
    payload: RoadmapGenerateRequest,
    current: CurrentUser,
    service: RoadmapService = Depends(get_roadmap_service),
) -> RoadmapOut:
    roadmap = await service.generate(current.id, payload.career_path_id)
    return RoadmapOut.model_validate(roadmap)


@router.get("/me", response_model=RoadmapOut | None, summary="Active roadmap")
async def get_active_roadmap(
    current: CurrentUser,
    service: RoadmapService = Depends(get_roadmap_service),
) -> RoadmapOut | None:
    roadmap = await service.get_active(current.id)
    return RoadmapOut.model_validate(roadmap) if roadmap else None


@router.get("/history", response_model=list[RoadmapOut], summary="Roadmap history")
async def list_roadmaps(
    current: CurrentUser,
    service: RoadmapService = Depends(get_roadmap_service),
) -> list[RoadmapOut]:
    roadmaps = await service.list_for_user(current.id)
    return [RoadmapOut.model_validate(r) for r in roadmaps]
