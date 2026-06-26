"""Skill gap analysis (Module 8-9)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.models.analysis import AnalysisHistory
from app.schemas.mvp import AnalysisOut, AnalysisRunRequest
from app.services.analysis_service import AnalysisService
from app.utils.user_level import experience_level_reason, normalize_level

router = APIRouter()


def get_analysis_service(db: DBSession) -> AnalysisService:
    return AnalysisService(db)


async def _to_analysis_out(service: AnalysisService, record: AnalysisHistory) -> AnalysisOut:
    ctx = await service._experience_context(record.user_id)
    projects_completed = ctx["projects_completed"]
    experience_years = ctx.get("experience_years")
    profile_academic = ctx.get("academic_level")
    level = normalize_level(record.level)
    return AnalysisOut(
        id=record.id,
        career_path_id=record.career_path_id,
        score=record.score,
        level=level,
        owned_skills=record.owned_skills,
        missing_skills=record.missing_skills,
        created_at=record.created_at,
        projects_completed=projects_completed,
        experience_years=experience_years,
        level_reason=experience_level_reason(
            level=level,
            projects_completed=projects_completed,
            experience_years=experience_years,
            academic_level=profile_academic,
        ),
    )


@router.post("/run", response_model=AnalysisOut, summary="Run skill gap analysis")
async def run_analysis(
    payload: AnalysisRunRequest,
    current: CurrentUser,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisOut:
    record = await service.run_analysis(current.id, payload.career_path_id)
    return await _to_analysis_out(service, record)


@router.get("/me", response_model=AnalysisOut | None, summary="Latest analysis")
async def get_latest_analysis(
    current: CurrentUser,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisOut | None:
    record = await service.get_latest(current.id)
    return await _to_analysis_out(service, record) if record else None


@router.get("/history", response_model=list[AnalysisOut], summary="Analysis history")
async def get_analysis_history(
    current: CurrentUser,
    service: AnalysisService = Depends(get_analysis_service),
) -> list[AnalysisOut]:
    records = await service.get_history(current.id)
    return [await _to_analysis_out(service, r) for r in records]
