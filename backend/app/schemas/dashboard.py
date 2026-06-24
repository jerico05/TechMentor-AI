"""Aggregated dashboard payload (one round-trip for the home page)."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.mentor import ChatSessionOut
from app.schemas.mvp import AnalysisOut, CVFileOut, GitHubAnalysisOut, QuizAttemptOut, RoadmapOut
from app.schemas.student_profile import StudentProfileOut


class DashboardSummaryOut(BaseModel):
    profile: StudentProfileOut | None = None
    analysis: AnalysisOut | None = None
    cv: CVFileOut | None = None
    github: GitHubAnalysisOut | None = None
    roadmap: RoadmapOut | None = None
    mentor_sessions: list[ChatSessionOut] = []
    quiz_history: list[QuizAttemptOut] = []
