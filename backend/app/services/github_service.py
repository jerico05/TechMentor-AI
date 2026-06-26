"""GitHub public API analysis."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.models.github_analysis import GitHubAnalysis
from app.models.skill import Skill
from app.repositories.student_profile_repository import StudentProfileRepository
from app.utils.cv_parser import extract_github_username
from app.utils.github_api import github_get
from app.utils.llm_helpers import extract_skills_from_text
from app.utils.skill_sync import sync_detected_skills

logger = get_logger(__name__)


async def fetch_github_profile(
    username: str,
) -> tuple[dict, list, dict[str, int], list[str]]:
    user_resp = await github_get(f"https://api.github.com/users/{username}", timeout=25.0)
    if user_resp.status_code == 404:
        raise ValidationError(f"Compte GitHub introuvable : @{username}")
    user_resp.raise_for_status()
    user_data = user_resp.json()

    repos_resp = await github_get(
        f"https://api.github.com/users/{username}/repos",
        timeout=25.0,
        params={"per_page": 30, "sort": "updated"},
    )
    if repos_resp.status_code == 403:
        raise ValidationError(
            "Limite de l'API GitHub atteinte. Réessayez dans quelques minutes "
            "ou configurez GITHUB_API_TOKEN."
        )
    repos_resp.raise_for_status()
    repos = repos_resp.json()

    languages: dict[str, int] = {}
    technologies: set[str] = set()
    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
        for topic in repo.get("topics") or []:
            technologies.add(topic)

    return user_data, repos, languages, sorted(technologies)


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

        if settings.cv_use_celery:
            try:
                from app.workers.tasks.github_tasks import analyze_github_task

                analyze_github_task.delay(user_id, username, github_url)
                logger.info("github.queued", user_id=user_id, username=username)
                return analysis
            except Exception as exc:
                logger.warning("github.celery.enqueue_failed", user_id=user_id, error=str(exc))

        return await self.process_analysis_record(analysis, github_url)

    async def get_for_user(self, user_id: int) -> GitHubAnalysis | None:
        result = await self.db.execute(select(GitHubAnalysis).where(GitHubAnalysis.user_id == user_id))
        analysis = result.scalar_one_or_none()
        if analysis is None:
            return None
        if analysis.status == "processing" and self._is_stale(analysis):
            logger.info("github.recover_stale", user_id=user_id, username=analysis.username)
            profile = await self.profile_repo.get_for_user(user_id)
            url = profile.github_url if profile else None
            return await self.process_analysis_record(analysis, url)
        return analysis

    async def process_analysis_record(
        self,
        analysis: GitHubAnalysis,
        github_url: str | None = None,
    ) -> GitHubAnalysis:
        try:
            user_data, repos, languages, technologies = await fetch_github_profile(analysis.username)
            analysis.repo_count = len(repos)
            analysis.languages = languages
            analysis.technologies = technologies
            analysis.raw_data = {"user": user_data, "repos": repos[:10]}
            text_blob = f"Languages: {', '.join(languages.keys())}. Topics: {', '.join(technologies)}"
            await self._sync_skills(analysis.user_id, text_blob)
            if github_url:
                await self.profile_repo.upsert_for_user(analysis.user_id, {"github_url": github_url})
            analysis.status = "completed"
            await self.db.commit()
            await self.db.refresh(analysis)
            logger.info(
                "github.completed",
                user_id=analysis.user_id,
                username=analysis.username,
                repos=analysis.repo_count,
            )
        except ValidationError as exc:
            analysis.status = "failed"
            await self.db.commit()
            await self.db.refresh(analysis)
            raise exc
        except Exception as exc:
            logger.exception(
                "github.process.failed",
                user_id=analysis.user_id,
                username=analysis.username,
                error=str(exc),
            )
            analysis.status = "failed"
            await self.db.commit()
            await self.db.refresh(analysis)
        return analysis

    async def _sync_skills(self, user_id: int, text: str) -> None:
        skills = (await self.db.execute(select(Skill))).scalars().all()
        names = [s.name for s in skills]
        detected = await extract_skills_from_text(text, names)
        await sync_detected_skills(
            self.db,
            user_id,
            detected,
            source="github",
            confidence=75,
            upgrade_github_source=True,
        )

    @staticmethod
    def _is_stale(analysis: GitHubAnalysis) -> bool:
        created = analysis.updated_at or analysis.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        age = (datetime.now(UTC) - created).total_seconds()
        return age >= settings.github_processing_stale_seconds
