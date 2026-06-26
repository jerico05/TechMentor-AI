"""LinkedIn profile analysis for mentor context."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.models.linkedin_analysis import LinkedInAnalysis
from app.models.skill import Skill
from app.repositories.student_profile_repository import StudentProfileRepository
from app.utils.linkedin_extract import extract_linkedin_profile
from app.utils.llm_helpers import extract_skills_from_text
from app.utils.skill_sync import sync_detected_skills

logger = get_logger(__name__)


class LinkedInService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = StudentProfileRepository(db)

    async def get_for_user(self, user_id: int) -> LinkedInAnalysis | None:
        result = await self.db.execute(select(LinkedInAnalysis).where(LinkedInAnalysis.user_id == user_id))
        return result.scalar_one_or_none()

    async def analyze_for_user(
        self,
        user_id: int,
        linkedin_url: str | None = None,
        profile_text: str | None = None,
        pdf_bytes: bytes | None = None,
    ) -> LinkedInAnalysis:
        profile = await self.profile_repo.get_for_user(user_id)
        url = linkedin_url or (profile.linkedin_url if profile else None)
        if not url:
            raise ValidationError("URL LinkedIn requise.")

        existing = await self.get_for_user(user_id)
        if existing:
            analysis = existing
            analysis.status = "processing"
            analysis.profile_url = url
        else:
            analysis = LinkedInAnalysis(user_id=user_id, profile_url=url, status="processing")
            self.db.add(analysis)

        await self.profile_repo.upsert_for_user(user_id, {"linkedin_url": url})
        await self.db.commit()
        await self.db.refresh(analysis)

        try:
            data = await extract_linkedin_profile(url, profile_text, pdf_bytes)
            analysis.profile_url = data["profile_url"]
            analysis.headline = data.get("headline")
            analysis.summary = data.get("summary")
            analysis.experiences = data.get("experiences") or []
            analysis.education = data.get("education") or []
            analysis.skills = data.get("skills") or []
            analysis.raw_text = data.get("raw_text")
            analysis.status = "completed"

            blob = " ".join(
                filter(
                    None,
                    [
                        data.get("headline"),
                        data.get("summary"),
                        " ".join(data.get("skills") or []),
                    ],
                )
            )
            await self._sync_skills(user_id, blob)
            await self.db.commit()
            await self.db.refresh(analysis)
            logger.info("linkedin.completed", user_id=user_id)
            return analysis
        except ValidationError as exc:
            analysis.status = "failed"
            await self.db.commit()
            await self.db.refresh(analysis)
            raise exc
        except Exception as exc:
            analysis.status = "failed"
            await self.db.commit()
            await self.db.refresh(analysis)
            logger.exception("linkedin.failed", user_id=user_id, error=str(exc))
            raise ValidationError("Analyse LinkedIn impossible.") from exc

    async def _sync_skills(self, user_id: int, text: str) -> None:
        if not text.strip():
            return
        rows = await self.db.execute(select(Skill.name))
        known = [r[0] for r in rows.all()]
        detected = await extract_skills_from_text(text, known)
        if detected:
            await sync_detected_skills(
                self.db,
                user_id,
                detected,
                source="linkedin",
                confidence=80,
            )
