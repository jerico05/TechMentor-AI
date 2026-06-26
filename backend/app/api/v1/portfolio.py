"""Portfolio projects - add links, extract metadata."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.repositories.student_profile_repository import StudentProfileRepository
from app.schemas.mvp import (
    PortfolioProjectAddRequest,
    PortfolioProjectOut,
    PortfolioProjectsOut,
    PortfolioUrlRequest,
)
from app.services.analysis_service import AnalysisService
from app.services.portfolio_project_service import PortfolioProjectService

router = APIRouter()


def get_portfolio_service(db: DBSession) -> PortfolioProjectService:
    return PortfolioProjectService(db)


async def _portfolio_out(
    db: DBSession,
    user_id: int,
    *,
    projects_discovered: int = 0,
    projects_added: int = 0,
) -> PortfolioProjectsOut:
    service = PortfolioProjectService(db)
    analysis = AnalysisService(db)
    profile_repo = StudentProfileRepository(db)
    profile = await profile_repo.get_for_user(user_id)
    projects = await service.list_for_user(user_id)
    completed = await analysis.count_completed_projects(user_id)
    return PortfolioProjectsOut(
        projects=[PortfolioProjectOut.model_validate(p) for p in projects],
        portfolio_url=profile.portfolio_url if profile else None,
        total_completed=completed,
        projects_discovered=projects_discovered,
        projects_added=projects_added,
    )


@router.get("/projects", response_model=PortfolioProjectsOut, summary="List portfolio projects")
async def list_portfolio_projects(
    current: CurrentUser,
    db: DBSession,
) -> PortfolioProjectsOut:
    return await _portfolio_out(db, current.id)


@router.post("/projects", response_model=PortfolioProjectOut, summary="Add portfolio project by URL")
async def add_portfolio_project(
    payload: PortfolioProjectAddRequest,
    current: CurrentUser,
    service: PortfolioProjectService = Depends(get_portfolio_service),
) -> PortfolioProjectOut:
    project = await service.add_project(current.id, payload.url)
    return PortfolioProjectOut.model_validate(project)


@router.delete("/projects/{project_id}", response_model=PortfolioProjectsOut, summary="Remove portfolio project")
async def delete_portfolio_project(
    project_id: int,
    current: CurrentUser,
    db: DBSession,
    service: PortfolioProjectService = Depends(get_portfolio_service),
) -> PortfolioProjectsOut:
    await service.delete_project(current.id, project_id)
    return await _portfolio_out(db, current.id)


@router.put("/url", response_model=PortfolioProjectsOut, summary="Save portfolio site URL")
async def save_portfolio_url(
    payload: PortfolioUrlRequest,
    current: CurrentUser,
    db: DBSession,
    service: PortfolioProjectService = Depends(get_portfolio_service),
) -> PortfolioProjectsOut:
    discovered, added = await service.save_portfolio_url(
        current.id,
        payload.portfolio_url,
        extract_projects=payload.extract_projects,
    )
    return await _portfolio_out(
        db,
        current.id,
        projects_discovered=discovered,
        projects_added=added,
    )
