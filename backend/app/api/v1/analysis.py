"""Skill gap analysis (Module 8–9)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.schemas.mvp import AnalysisOut, AnalysisRunRequest
from app.services.analysis_service import AnalysisService

router = APIRouter()


def get_analysis_service(db: DBSession) -> AnalysisService:
    return AnalysisService(db)


@router.post("/run", response_model=AnalysisOut, summary="Run skill gap analysis")
async def run_analysis(
    payload: AnalysisRunRequest,
    current: CurrentUser,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisOut:
    record = await service.run_analysis(current.id, payload.career_path_id)
    return AnalysisOut.model_validate(record)


@router.get("/me", response_model=AnalysisOut | None, summary="Latest analysis")
async def get_latest_analysis(
    current: CurrentUser,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisOut | None:
    record = await service.get_latest(current.id)
    return AnalysisOut.model_validate(record) if record else None


@router.get("/history", response_model=list[AnalysisOut], summary="Analysis history")
async def get_analysis_history(
    current: CurrentUser,
    service: AnalysisService = Depends(get_analysis_service),
) -> list[AnalysisOut]:
    records = await service.get_history(current.id)
    return [AnalysisOut.model_validate(r) for r in records]
