"""GitHub public API analysis."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.models.github_analysis import GitHubAnalysis
from app.repositories.student_profile_repository import StudentProfileRepository
from app.utils.cv_parser import extract_github_username


def _dispatch_github_task(user_id: int, username: str, github_url: str | None) -> None:
    try:
        from app.workers.tasks.github_tasks import analyze_github_task

        analyze_github_task.delay(user_id, username, github_url)
    except Exception:
        pass


class GitHubService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = StudentProfileRepository(db)

    async def analyze_for_user(self, user_id: int, github_url: str | None = None) -> GitHubAnalysis:
        profile = await self.profile_repo.get_for_user(user_id)
        url = github_url or (profile.github_url if profile else None)
        username = extract_github_username(url)
        if not username:
            raise ValidationError("URL ou nom d'utilisateur GitHub invalide.")

        existing = await self.db.execute(select(GitHubAnalysis).where(GitHubAnalysis.user_id == user_id))
        analysis = existing.scalar_one_or_none()
        if analysis:
            analysis.username = username
            analysis.status = "processing"
        else:
            analysis = GitHubAnalysis(user_id=user_id, username=username, status="processing")
            self.db.add(analysis)

        if profile and github_url:
            await self.profile_repo.upsert_for_user(user_id, {"github_url": github_url})

        await self.db.commit()
        await self.db.refresh(analysis)

        _dispatch_github_task(user_id, username, github_url)
        return analysis

    async def get_for_user(self, user_id: int) -> GitHubAnalysis | None:
        result = await self.db.execute(select(GitHubAnalysis).where(GitHubAnalysis.user_id == user_id))
        return result.scalar_one_or_none()
