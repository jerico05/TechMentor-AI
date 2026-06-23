"""Careers catalog (Module 6)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from app.core.deps import DBSession
from app.core.exceptions import NotFoundError
from app.schemas.mvp import CareerPathOut, SkillOut
from app.services.analysis_service import AnalysisService

router = APIRouter()


def get_analysis_service(db: DBSession) -> AnalysisService:
    return AnalysisService(db)


@router.get("", response_model=list[CareerPathOut], summary="List career paths")
async def list_careers(
    response: Response,
    service: AnalysisService = Depends(get_analysis_service),
) -> list[CareerPathOut]:
    from app.core.config import settings

    if settings.is_production:
        response.headers["Cache-Control"] = "public, max-age=3600"
    else:
        response.headers["Cache-Control"] = "no-store"
    careers = await service.list_careers()
    return [
        CareerPathOut(
            id=c.id,
            slug=c.slug,
            name=c.name,
            description=c.description,
            skills=[SkillOut.model_validate(cps.skill) for cps in c.skills],
        )
        for c in careers
    ]


@router.get("/{career_id}", response_model=CareerPathOut, summary="Get career path")
async def get_career(
    career_id: int,
    service: AnalysisService = Depends(get_analysis_service),
) -> CareerPathOut:
    try:
        c = await service.get_career(career_id)
    except NotFoundError:
        raise
    return CareerPathOut(
        id=c.id,
        slug=c.slug,
        name=c.name,
        description=c.description,
        skills=[SkillOut.model_validate(cps.skill) for cps in c.skills],
    )
