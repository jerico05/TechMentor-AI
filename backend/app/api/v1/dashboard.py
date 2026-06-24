"""Dashboard aggregate endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.deps import CurrentUser
from app.schemas.dashboard import DashboardSummaryOut
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/me", response_model=DashboardSummaryOut, summary="Dashboard summary (one request)")
async def get_dashboard_summary(current: CurrentUser) -> DashboardSummaryOut:
    return await DashboardService.summary_for_user(current.id)
