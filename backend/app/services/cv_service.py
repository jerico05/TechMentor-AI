"""CV upload & skill extraction service."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.models.cv_file import CVFile
from app.models.skill import Skill
from app.services.cv_storage import read_cv_bytes, save_cv_file
from app.utils.cv_parser import extract_text_from_bytes
from app.utils.skill_sync import sync_detected_skills

logger = get_logger(__name__)


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

        if settings.cv_storage_backend == "cloudinary" and not settings.cloudinary_configured:
            raise ValidationError(
                "CV_STORAGE_BACKEND=cloudinary mais les variables CLOUDINARY_* sont manquantes."
            )

        data = await file.read()
        max_bytes = settings.max_cv_size_mb * 1024 * 1024
        if len(data) > max_bytes:
            raise ValidationError(f"Fichier trop volumineux (max {settings.max_cv_size_mb} Mo).")

        original_filename = file.filename or "cv.pdf"
        mime_type = file.content_type or "application/octet-stream"
        stored_path = save_cv_file(user_id, data, original_filename, mime_type)

        cv = CVFile(
            user_id=user_id,
            original_filename=original_filename,
            stored_path=stored_path,
            mime_type=mime_type,
            status="processing",
        )
        self.db.add(cv)
        await self.db.commit()
        await self.db.refresh(cv)

        if settings.cv_use_celery:
            try:
                from app.workers.tasks.cv_tasks import parse_cv_task

                parse_cv_task.delay(cv.id)
                logger.info("cv.queued", cv_id=cv.id, user_id=user_id)
                return cv
            except Exception as exc:
                logger.warning("cv.celery.enqueue_failed", cv_id=cv.id, error=str(exc))

        return await self.process_cv_record(cv)

    async def get_latest(self, user_id: int) -> CVFile | None:
        result = await self.db.execute(
            select(CVFile).where(CVFile.user_id == user_id).order_by(CVFile.created_at.desc()).limit(1)
        )
        cv = result.scalar_one_or_none()
        if cv is None:
            return None
        if cv.status == "processing" and self._is_stale(cv):
            logger.info("cv.recover_stale", cv_id=cv.id, user_id=user_id)
            return await self.process_cv_record(cv)
        return cv

    async def process_cv_record(self, cv: CVFile) -> CVFile:
        """Extract text from CV and sync detected skills."""
        try:
            text = self._extract_text(cv)
            if not text.strip():
                raise ValueError(
                    "Aucun texte lisible dans le fichier. Essayez un PDF exporté (pas une image scannée)."
                )
            cv.extracted_text = text
            cv.status = "parsed"
            await self._sync_skills(cv.user_id, text)
            await self.db.commit()
            await self.db.refresh(cv)
            logger.info("cv.parsed", cv_id=cv.id, user_id=cv.user_id, chars=len(text))
        except Exception as exc:
            logger.exception("cv.process.failed", cv_id=cv.id, error=str(exc))
            cv.status = "failed"
            cv.extracted_text = None
            await self.db.commit()
            await self.db.refresh(cv)
        return cv

    @staticmethod
    def _is_stale(cv: CVFile) -> bool:
        created = cv.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        age = (datetime.now(UTC) - created).total_seconds()
        return age >= settings.cv_processing_stale_seconds

    @staticmethod
    def _extract_text(cv: CVFile) -> str:
        data = read_cv_bytes(cv.stored_path)
        suffix = f".{cv.original_filename.rsplit('.', 1)[-1]}" if "." in cv.original_filename else None
        return extract_text_from_bytes(data, cv.mime_type, suffix=suffix)

    async def _sync_skills(self, user_id: int, text: str) -> None:
        skills = (await self.db.execute(select(Skill))).scalars().all()
        names = [s.name for s in skills]
        from app.utils.llm_helpers import extract_skills_from_text

        detected = await extract_skills_from_text(text, names)
        await sync_detected_skills(
            self.db,
            user_id,
            detected,
            source="cv",
            confidence=85,
        )
        logger.info("cv.skills_synced", user_id=user_id, count=len(detected))
