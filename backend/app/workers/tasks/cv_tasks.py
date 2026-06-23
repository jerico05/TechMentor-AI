"""CV parsing Celery task."""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.logging import get_logger
from app.models.cv_file import CVFile
from app.models.skill import Skill, UserSkill
from app.services.cv_service import CVService
from app.workers.celery_app import celery_app
from app.workers.db import get_sync_session

logger = get_logger(__name__)


async def _sync_skills_async(session, user_id: int, text: str) -> None:
    from app.utils.llm_helpers import extract_skills_from_text

    skills = session.execute(select(Skill)).scalars().all()
    names = [s.name for s in skills]
    detected = await extract_skills_from_text(text, names)
    name_to_id = {s.name.lower(): s.id for s in skills}
    for name in detected:
        skill_id = name_to_id.get(name.lower())
        if not skill_id:
            continue
        existing = session.execute(
            select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        ).scalar_one_or_none()
        if existing:
            continue
        session.add(UserSkill(user_id=user_id, skill_id=skill_id, source="cv", confidence=85))


def _process_cv_sync(session, cv: CVFile) -> None:
    text = CVService._extract_text(cv)
    if not text.strip():
        raise ValueError("Aucun texte lisible dans le CV.")
    cv.extracted_text = text
    cv.status = "parsed"
    asyncio.run(_sync_skills_async(session, cv.user_id, text))


@celery_app.task(name="cv.parse", bind=True, max_retries=2)
def parse_cv_task(self, cv_id: int) -> str:
    session = get_sync_session()
    try:
        cv = session.get(CVFile, cv_id)
        if not cv:
            return "not_found"
        try:
            _process_cv_sync(session, cv)
            session.commit()
            logger.info("cv.parsed.celery", cv_id=cv_id)
            return "parsed"
        except Exception as exc:
            session.rollback()
            cv = session.get(CVFile, cv_id)
            if cv:
                cv.status = "failed"
                cv.extracted_text = None
                session.commit()
            logger.exception("cv.parse.celery_failed", cv_id=cv_id, error=str(exc))
            raise self.retry(exc=exc, countdown=5) from exc
    finally:
        session.close()
