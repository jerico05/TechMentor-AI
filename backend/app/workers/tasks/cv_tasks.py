"""CV parsing Celery task."""

from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy import select

from app.models.cv_file import CVFile
from app.models.skill import Skill, UserSkill
from app.utils.cv_parser import extract_text_from_file
from app.utils.llm_helpers import extract_skills_from_text
from app.workers.celery_app import celery_app
from app.workers.db import get_sync_session


async def _sync_skills_async(session, user_id: int, text: str) -> None:
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


@celery_app.task(name="cv.parse", bind=True, max_retries=2)
def parse_cv_task(self, cv_id: int) -> str:
    session = get_sync_session()
    try:
        cv = session.get(CVFile, cv_id)
        if not cv:
            return "not_found"
        path = Path(cv.stored_path)
        try:
            text = extract_text_from_file(path, cv.mime_type)
            cv.extracted_text = text
            cv.status = "parsed"
            asyncio.run(_sync_skills_async(session, cv.user_id, text))
        except Exception as exc:
            cv.status = "failed"
            session.commit()
            raise self.retry(exc=exc, countdown=5) from exc
        session.commit()
        return "parsed"
    finally:
        session.close()
