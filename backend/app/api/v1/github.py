"""GitHub analysis endpoints (Module 5)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.schemas.mvp import GitHubAnalysisOut, GitHubAnalyzeRequest
from app.services.github_service import GitHubService

router = APIRouter()


def get_github_service(db: DBSession) -> GitHubService:
    return GitHubService(db)


@router.post("/analyze", response_model=GitHubAnalysisOut, summary="Analyze GitHub profile")
async def analyze_github(
    payload: GitHubAnalyzeRequest,
    current: CurrentUser,
    service: GitHubService = Depends(get_github_service),
) -> GitHubAnalysisOut:
    analysis = await service.analyze_for_user(current.id, payload.github_url)
    return GitHubAnalysisOut.model_validate(analysis)


@router.get("/me", response_model=GitHubAnalysisOut | None, summary="Get GitHub analysis")
async def get_my_github(
    current: CurrentUser,
    service: GitHubService = Depends(get_github_service),
) -> GitHubAnalysisOut | None:
    analysis = await service.get_for_user(current.id)
    return GitHubAnalysisOut.model_validate(analysis) if analysis else None
