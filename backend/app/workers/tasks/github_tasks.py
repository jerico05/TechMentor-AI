"""GitHub analysis Celery task."""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.logging import get_logger
from app.models.github_analysis import GitHubAnalysis
from app.models.skill import Skill, UserSkill
from app.models.student_profile import StudentProfile
from app.services.github_service import fetch_github_profile
from app.utils.llm_helpers import extract_skills_from_text
from app.workers.celery_app import celery_app
from app.workers.db import get_sync_session

logger = get_logger(__name__)


async def _sync_skills(session, user_id: int, text: str) -> None:
    skills = session.execute(select(Skill)).scalars().all()
    names = [s.name for s in skills]
    detected = await extract_skills_from_text(text, names)
    name_to_id = {s.name.lower(): s.id for s in skills}
    for name in detected:
        skill_id = name_to_id.get(name.lower())
        if not skill_id:
            continue
        row = session.execute(
            select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        ).scalar_one_or_none()
        if row:
            if row.source != "cv":
                row.source = "github"
            continue
        session.add(UserSkill(user_id=user_id, skill_id=skill_id, source="github", confidence=75))


@celery_app.task(name="github.analyze", bind=True, max_retries=2)
def analyze_github_task(self, user_id: int, username: str, github_url: str | None = None) -> str:
    session = get_sync_session()
    try:
        analysis = session.execute(
            select(GitHubAnalysis).where(GitHubAnalysis.user_id == user_id)
        ).scalar_one_or_none()
        if not analysis:
            analysis = GitHubAnalysis(user_id=user_id, username=username, status="processing")
            session.add(analysis)
        else:
            analysis.status = "processing"
            analysis.username = username
        session.commit()

        try:
            user_data, repos, languages, technologies = asyncio.run(fetch_github_profile(username))
            analysis.repo_count = len(repos)
            analysis.languages = languages
            analysis.technologies = technologies
            analysis.raw_data = {"user": user_data, "repos": repos[:10]}
            text_blob = f"Languages: {', '.join(languages.keys())}. Topics: {', '.join(technologies)}"
            asyncio.run(_sync_skills(session, user_id, text_blob))
            if github_url:
                profile = session.execute(
                    select(StudentProfile).where(StudentProfile.user_id == user_id)
                ).scalar_one_or_none()
                if profile:
                    profile.github_url = github_url
            analysis.status = "completed"
            session.commit()
            logger.info("github.completed.celery", user_id=user_id, username=username)
            return "completed"
        except Exception as exc:
            session.rollback()
            analysis = session.get(GitHubAnalysis, analysis.id)
            if analysis:
                analysis.status = "failed"
                session.commit()
            logger.exception("github.celery_failed", user_id=user_id, error=str(exc))
            raise self.retry(exc=exc, countdown=10) from exc
    finally:
        session.close()
