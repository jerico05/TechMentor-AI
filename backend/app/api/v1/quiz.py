"""Quiz evaluation (Module 15)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.schemas.mvp import QuizAttemptOut, QuizGenerateResponse, QuizSubmitRequest, QuizSubmitResponse
from app.services.quiz_service import QuizService

router = APIRouter()


def get_quiz_service(db: DBSession) -> QuizService:
    return QuizService(db)


@router.post("/generate", response_model=QuizGenerateResponse, summary="Generate technical quiz")
async def generate_quiz(
    current: CurrentUser,
    service: QuizService = Depends(get_quiz_service),
) -> QuizGenerateResponse:
    result = await service.generate(current.id)
    return QuizGenerateResponse.model_validate(result)


@router.post("/submit", response_model=QuizSubmitResponse, summary="Submit quiz answers")
async def submit_quiz(
    payload: QuizSubmitRequest,
    current: CurrentUser,
    service: QuizService = Depends(get_quiz_service),
) -> QuizSubmitResponse:
    result = await service.submit(current.id, payload.quiz_id, payload.answers)
    return QuizSubmitResponse(
        attempt=QuizAttemptOut.model_validate(result["attempt"]),
        previous_score=result["previous_score"],
        new_score=result["new_score"],
        new_level=result["new_level"],
        roadmap_id=result["roadmap_id"],
        feedback=result["feedback"],
    )


@router.get("/history", response_model=list[QuizAttemptOut], summary="Quiz attempt history")
async def quiz_history(
    current: CurrentUser,
    service: QuizService = Depends(get_quiz_service),
) -> list[QuizAttemptOut]:
    attempts = await service.get_history(current.id)
    return [QuizAttemptOut.model_validate(a) for a in attempts]
