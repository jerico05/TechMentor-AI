"""Load dashboard data in parallel (single HTTP request from the client)."""

from __future__ import annotations

import asyncio

from app.api.v1.analysis import _to_analysis_out
from app.database.session import AsyncSessionLocal
from app.schemas.dashboard import DashboardSummaryOut
from app.schemas.mentor import ChatSessionOut
from app.schemas.mvp import CVFileOut, GitHubAnalysisOut, QuizAttemptOut, RoadmapOut
from app.schemas.student_profile import StudentProfileOut
from app.services.analysis_service import AnalysisService
from app.services.cv_service import CVService
from app.services.github_service import GitHubService
from app.services.mentor_service import MentorService
from app.services.profile_service import ProfileService
from app.services.quiz_service import QuizService
from app.services.roadmap_service import RoadmapService


class DashboardService:
    @staticmethod
    async def summary_for_user(user_id: int) -> DashboardSummaryOut:
        async def load_profile() -> StudentProfileOut | None:
            async with AsyncSessionLocal() as db:
                profile = await ProfileService(db).get_for_user(user_id)
                return StudentProfileOut.model_validate(profile) if profile else None

        async def load_analysis():
            async with AsyncSessionLocal() as db:
                service = AnalysisService(db)
                record = await service.get_latest(user_id)
                return await _to_analysis_out(service, record) if record else None

        async def load_cv() -> CVFileOut | None:
            async with AsyncSessionLocal() as db:
                cv = await CVService(db).get_latest(user_id)
                return CVFileOut.model_validate(cv) if cv else None

        async def load_github() -> GitHubAnalysisOut | None:
            async with AsyncSessionLocal() as db:
                row = await GitHubService(db).get_for_user(user_id)
                return GitHubAnalysisOut.model_validate(row) if row else None

        async def load_roadmap() -> RoadmapOut | None:
            async with AsyncSessionLocal() as db:
                row = await RoadmapService(db).get_active(user_id)
                return RoadmapOut.model_validate(row) if row else None

        async def load_sessions() -> list[ChatSessionOut]:
            async with AsyncSessionLocal() as db:
                sessions = await MentorService(db).list_sessions(user_id)
                return [
                    ChatSessionOut(
                        id=s.id,
                        title=s.title,
                        created_at=s.created_at.isoformat() if s.created_at else "",
                    )
                    for s in sessions
                ]

        async def load_quiz() -> list[QuizAttemptOut]:
            async with AsyncSessionLocal() as db:
                attempts = await QuizService(db).get_history(user_id)
                return [QuizAttemptOut.model_validate(a) for a in attempts]

        (
            profile,
            analysis,
            cv,
            github,
            roadmap,
            mentor_sessions,
            quiz_history,
        ) = await asyncio.gather(
            load_profile(),
            load_analysis(),
            load_cv(),
            load_github(),
            load_roadmap(),
            load_sessions(),
            load_quiz(),
        )

        return DashboardSummaryOut(
            profile=profile,
            analysis=analysis,
            cv=cv,
            github=github,
            roadmap=roadmap,
            mentor_sessions=mentor_sessions,
            quiz_history=quiz_history,
        )
