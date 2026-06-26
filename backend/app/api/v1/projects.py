"""Project recommendations (Module 12)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DBSession
from app.core.exceptions import ValidationError
from app.schemas.mvp import (
    ProjectCompleteRequest,
    ProjectCompletionsOut,
    ProjectRecommendationOut,
    ProjectSubmitRequest,
    ProjectSubmissionOut,
)
from app.services.analysis_service import AnalysisService
from app.services.project_evaluation_service import ProjectEvaluationService
from app.services.project_service import ProjectService

router = APIRouter()


def get_project_service(db: DBSession) -> ProjectService:
    return ProjectService(db)


def get_evaluation_service(db: DBSession) -> ProjectEvaluationService:
    return ProjectEvaluationService(db)


def _validate_title(title: str) -> str:
    cleaned = title.strip()
    if not cleaned:
        raise ValidationError("Le titre du projet est requis.")
    return cleaned


@router.get("/recommendations", response_model=ProjectRecommendationOut, summary="Recommended projects")
async def get_recommendations(
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRecommendationOut:
    data = await service.recommend(current.id)
    return ProjectRecommendationOut.model_validate(data)


@router.get("/completions", response_model=ProjectCompletionsOut, summary="Completed portfolio projects")
async def list_completions(
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectCompletionsOut:
    completed = await service.list_completions(current.id)
    return ProjectCompletionsOut(completed=completed)


@router.post("/complete", response_model=ProjectCompletionsOut, summary="Mark project as completed")
async def complete_project(
    payload: ProjectCompleteRequest,
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectCompletionsOut:
    completed = await service.mark_complete(
        current.id, _validate_title(payload.title), payload.career_slug
    )
    return ProjectCompletionsOut(completed=completed)


@router.delete("/complete", response_model=ProjectCompletionsOut, summary="Unmark completed project")
async def uncomplete_project(
    payload: ProjectCompleteRequest,
    current: CurrentUser,
    service: ProjectService = Depends(get_project_service),
) -> ProjectCompletionsOut:
    completed = await service.mark_incomplete(current.id, _validate_title(payload.title))
    return ProjectCompletionsOut(completed=completed)


@router.post("/submit", response_model=ProjectSubmissionOut, summary="Submit project proof for evaluation")
async def submit_project_proof(
    payload: ProjectSubmitRequest,
    current: CurrentUser,
    evaluation_service: ProjectEvaluationService = Depends(get_evaluation_service),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectSubmissionOut:
    submission = await evaluation_service.submit(
        user_id=current.id,
        project_title=_validate_title(payload.project_title),
        career_slug=payload.career_slug,
        project_description=payload.project_description,
        skills_practiced=payload.skills_practiced,
        deliverables=payload.deliverables,
        github_url=payload.github_url or None,
        user_description=payload.user_description or None,
    )
    if submission.status == "approved":
        analysis_service = AnalysisService(project_service.db)
        await analysis_service.refresh_experience_level(current.id)
    return ProjectSubmissionOut.model_validate(submission)


@router.get("/submissions", response_model=list[ProjectSubmissionOut], summary="List my project submissions")
async def list_submissions(
    current: CurrentUser,
    evaluation_service: ProjectEvaluationService = Depends(get_evaluation_service),
) -> list[ProjectSubmissionOut]:
    submissions = await evaluation_service.get_submissions(current.id)
    return [ProjectSubmissionOut.model_validate(s) for s in submissions]


@router.get("/submissions/{project_title}", response_model=ProjectSubmissionOut | None, summary="Latest submission for a project")
async def get_project_submission(
    project_title: str,
    current: CurrentUser,
    evaluation_service: ProjectEvaluationService = Depends(get_evaluation_service),
) -> ProjectSubmissionOut | None:
    submission = await evaluation_service.get_latest_for_project(current.id, project_title)
    return ProjectSubmissionOut.model_validate(submission) if submission else None
