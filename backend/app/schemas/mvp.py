"""MVP API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

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
    created_at: datetime
    projects_completed: int = 0
    level_reason: str | None = None


class RoadmapGenerateRequest(BaseModel):
    career_path_id: int | None = None
    duration_months: Literal[3, 6, 12] | None = None


class RoadmapSuggestionOut(BaseModel):
    suggested_months: Literal[3, 6, 12]
    level: str | None = None
    missing_skills_count: int
    reason: str


class RoadmapOut(ORMModel):
    id: int
    career_path_id: int
    content: dict
    status: str
    created_at: datetime


class ProjectDataSourceOut(BaseModel):
    name: str
    url: str
    note: str = ""


class RecommendedProjectOut(BaseModel):
    title: str
    tagline: str
    description: str
    track: str = "dev"
    difficulty: str
    skills_practiced: list[str] = Field(default_factory=list)
    estimated_weeks: int = 3
    impact: str | None = None
    stack: list[str] = Field(default_factory=list)
    data_sources: list[ProjectDataSourceOut] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)


class ProjectRecommendationOut(BaseModel):
    level: str
    score: int
    missing_skills: list[str]
    career_name: str = ""
    career_slug: str = ""
    projects: list[RecommendedProjectOut]


class ProjectCompleteRequest(BaseModel):
    title: str
    career_slug: str | None = None


class ProjectCompletionsOut(BaseModel):
    completed: list[str]


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: dict[str, int]


class QuizQuestionOut(BaseModel):
    id: str
    question: str
    options: list[str]


class QuizGenerateResponse(BaseModel):
    quiz_id: str
    questions: list[QuizQuestionOut]


class QuizAttemptOut(ORMModel):
    id: int
    score: int
    total_questions: int
    feedback: str | None
    created_at: datetime


class QuizSubmitResponse(BaseModel):
    attempt: QuizAttemptOut
    previous_score: int
    new_score: int
    new_level: str
    roadmap_id: int
    feedback: str


class GitHubAnalyzeRequest(BaseModel):
    github_url: str | None = None


class LinkedInAnalyzeRequest(BaseModel):
    linkedin_url: str | None = None
    profile_text: str | None = Field(default=None, max_length=8000)


class LinkedInAnalysisOut(ORMModel):
    id: int
    profile_url: str
    headline: str | None
    summary: str | None
    experiences: list | None
    education: list | None
    skills: list | None
    status: str


class PortfolioProjectOut(ORMModel):
    id: int
    url: str
    title: str
    summary: str | None
    stack: list[str] | None
    source: str
    status: str
    created_at: datetime


class PortfolioProjectAddRequest(BaseModel):
    url: str = Field(min_length=8, max_length=1000)


class PortfolioProjectsOut(BaseModel):
    projects: list[PortfolioProjectOut]
    portfolio_url: str | None = None
    total_completed: int = 0
    projects_discovered: int = 0
    projects_added: int = 0


class PortfolioUrlRequest(BaseModel):
    portfolio_url: str | None = None
    extract_projects: bool = True
