"""LinkedIn analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.deps import CurrentUser, DBSession
from app.core.exceptions import ValidationError
from app.schemas.mvp import LinkedInAnalysisOut, LinkedInAnalyzeRequest
from app.services.linkedin_service import LinkedInService

router = APIRouter()

_MAX_PDF_BYTES = 5 * 1024 * 1024


def get_linkedin_service(db: DBSession) -> LinkedInService:
    return LinkedInService(db)


@router.post("/analyze", response_model=LinkedInAnalysisOut, summary="Analyze LinkedIn profile")
async def analyze_linkedin(
    payload: LinkedInAnalyzeRequest,
    current: CurrentUser,
    service: LinkedInService = Depends(get_linkedin_service),
) -> LinkedInAnalysisOut:
    analysis = await service.analyze_for_user(
        current.id,
        payload.linkedin_url,
        payload.profile_text,
    )
    return LinkedInAnalysisOut.model_validate(analysis)


@router.post("/analyze/pdf", response_model=LinkedInAnalysisOut, summary="Analyze LinkedIn PDF export")
async def analyze_linkedin_pdf(
    current: CurrentUser,
    service: LinkedInService = Depends(get_linkedin_service),
    linkedin_url: str = Form(...),
    profile_text: str | None = Form(None),
    pdf_file: UploadFile = File(...),
) -> LinkedInAnalysisOut:
    if pdf_file.content_type not in ("application/pdf", "application/octet-stream"):
        raise ValidationError("Format accepté : PDF uniquement (export LinkedIn).")

    data = await pdf_file.read()
    if len(data) > _MAX_PDF_BYTES:
        raise ValidationError("PDF trop volumineux (max 5 Mo).")
    if len(data) < 100:
        raise ValidationError("Fichier PDF vide ou invalide.")

    analysis = await service.analyze_for_user(
        current.id,
        linkedin_url,
        profile_text,
        pdf_bytes=data,
    )
    return LinkedInAnalysisOut.model_validate(analysis)


@router.get("/me", response_model=LinkedInAnalysisOut | None, summary="Get LinkedIn analysis")
async def get_my_linkedin(
    current: CurrentUser,
    service: LinkedInService = Depends(get_linkedin_service),
) -> LinkedInAnalysisOut | None:
    analysis = await service.get_for_user(current.id)
    return LinkedInAnalysisOut.model_validate(analysis) if analysis else None
