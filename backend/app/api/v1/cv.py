"""CV upload endpoints (Module 3)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.deps import CurrentUser, DBSession
from app.schemas.mvp import CVFileOut
from app.services.cv_service import CVService

router = APIRouter()


def get_cv_service(db: DBSession) -> CVService:
    return CVService(db)


@router.post("/upload", response_model=CVFileOut, summary="Upload CV (PDF/DOCX)")
async def upload_cv(
    current: CurrentUser,
    file: UploadFile = File(...),
    service: CVService = Depends(get_cv_service),
) -> CVFileOut:
    cv = await service.upload(current.id, file)
    return CVFileOut.model_validate(cv)


@router.get("/me", response_model=CVFileOut | None, summary="Get latest CV")
async def get_my_cv(
    current: CurrentUser,
    service: CVService = Depends(get_cv_service),
) -> CVFileOut | None:
    cv = await service.get_latest(current.id)
    return CVFileOut.model_validate(cv) if cv else None
