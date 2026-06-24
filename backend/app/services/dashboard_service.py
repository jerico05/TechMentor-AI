"""Load dashboard data in parallel (single HTTP request from the client)."""

from __future__ import annotations

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
        """Single DB session - one pooled connection, fewer Neon round-trips."""
        async with AsyncSessionLocal() as db:
            profile_svc = ProfileService(db)
            analysis_svc = AnalysisService(db)
            cv_svc = CVService(db)
            github_svc = GitHubService(db)
            roadmap_svc = RoadmapService(db)
            mentor_svc = MentorService(db)
            quiz_svc = QuizService(db)

            profile_row = await profile_svc.get_for_user(user_id)
            analysis_record = await analysis_svc.get_latest(user_id)
            cv_row = await cv_svc.get_latest(user_id)
            github_row = await github_svc.get_for_user(user_id)
            roadmap_row = await roadmap_svc.get_active(user_id)
            sessions = await mentor_svc.list_sessions(user_id)
            quiz_attempts = await quiz_svc.get_history(user_id)

            profile = StudentProfileOut.model_validate(profile_row) if profile_row else None
            analysis = await _to_analysis_out(analysis_svc, analysis_record) if analysis_record else None
            cv = CVFileOut.model_validate(cv_row) if cv_row else None
            github = GitHubAnalysisOut.model_validate(github_row) if github_row else None
            roadmap = RoadmapOut.model_validate(roadmap_row) if roadmap_row else None
            mentor_sessions = [
                ChatSessionOut(
                    id=s.id,
                    title=s.title,
                    created_at=s.created_at.isoformat() if s.created_at else "",
                )
                for s in sessions
            ]
            quiz_history = [QuizAttemptOut.model_validate(a) for a in quiz_attempts]

        return DashboardSummaryOut(
            profile=profile,
            analysis=analysis,
            cv=cv,
            github=github,
            roadmap=roadmap,
            mentor_sessions=mentor_sessions,
            quiz_history=quiz_history,
        )
