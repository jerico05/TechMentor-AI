"""MVP API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class SkillOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    category: str
    weight: int


class CareerPathOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None
    skills: list[SkillOut] = Field(default_factory=list)


class CVFileOut(ORMModel):
    id: int
    original_filename: str
    mime_type: str
    status: str
    extracted_text: str | None


class GitHubAnalysisOut(ORMModel):
    id: int
    username: str
    repo_count: int
    languages: dict | None
    technologies: list | None
    status: str


class AnalysisRunRequest(BaseModel):
    career_path_id: int | None = None


class AnalysisOut(ORMModel):
    id: int
    career_path_id: int
    score: int
    level: str
    owned_skills: list[str]
    missing_skills: list[str]


class RoadmapGenerateRequest(BaseModel):
    career_path_id: int | None = None


class RoadmapOut(ORMModel):
    id: int
    career_path_id: int
    content: dict
    status: str


class ProjectRecommendationOut(BaseModel):
    level: str
    score: int
    missing_skills: list[str]
    projects: list[dict]


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: dict[str, int]


class QuizAttemptOut(ORMModel):
    id: int
    score: int
    total_questions: int
    feedback: str | None


class QuizSubmitResponse(BaseModel):
    attempt: QuizAttemptOut
    previous_score: int
    new_score: int
    new_level: str
    roadmap_id: int
    feedback: str


class GitHubAnalyzeRequest(BaseModel):
    github_url: str | None = None
