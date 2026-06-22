"""CV upload & skill extraction service."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.models.cv_file import CVFile
from app.models.skill import Skill, UserSkill


class CVService:
    ALLOWED = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upload(self, user_id: int, file: UploadFile) -> CVFile:
        if file.content_type not in self.ALLOWED:
            raise ValidationError("Format accepté : PDF ou DOCX uniquement.")

        data = await file.read()
        max_bytes = settings.max_cv_size_mb * 1024 * 1024
        if len(data) > max_bytes:
            raise ValidationError(f"Fichier trop volumineux (max {settings.max_cv_size_mb} Mo).")

        ext = ".pdf" if file.content_type == "application/pdf" else ".docx"
        filename = f"{user_id}_{uuid.uuid4().hex}{ext}"
        path = settings.upload_path / filename
        path.write_bytes(data)

        cv = CVFile(
            user_id=user_id,
            original_filename=file.filename or filename,
            stored_path=str(path),
            mime_type=file.content_type or "application/octet-stream",
            status="processing",
        )
        self.db.add(cv)
        await self.db.commit()
        await self.db.refresh(cv)

        try:
            from app.workers.tasks.cv_tasks import parse_cv_task

            parse_cv_task.delay(cv.id)
        except Exception:
            from app.utils.cv_parser import extract_text_from_file

            try:
                text = extract_text_from_file(path, cv.mime_type)
                cv.extracted_text = text
                cv.status = "parsed"
                await self._sync_skills(user_id, text)
                await self.db.commit()
            except Exception:
                cv.status = "failed"
                await self.db.commit()

        return cv

    async def get_latest(self, user_id: int) -> CVFile | None:
        result = await self.db.execute(
            select(CVFile).where(CVFile.user_id == user_id).order_by(CVFile.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def _sync_skills(self, user_id: int, text: str) -> None:
        skills = (await self.db.execute(select(Skill))).scalars().all()
        names = [s.name for s in skills]
        from app.utils.llm_helpers import extract_skills_from_text

        detected = await extract_skills_from_text(text, names)
        name_to_id = {s.name.lower(): s.id for s in skills}

        for name in detected:
            skill_id = name_to_id.get(name.lower())
            if not skill_id:
                continue
            existing = await self.db.execute(
                select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
            )
            if existing.scalar_one_or_none():
                continue
            self.db.add(UserSkill(user_id=user_id, skill_id=skill_id, source="cv", confidence=85))
