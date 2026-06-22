"""Skill gap analysis & scoring."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError, ValidationError
from app.models.analysis import AnalysisHistory
from app.models.skill import CareerPath, CareerPathSkill, Skill, UserSkill
from app.repositories.student_profile_repository import StudentProfileRepository


def score_to_level(score: int) -> str:
    if score < 40:
        return "debutant"
    if score < 70:
        return "intermediaire"
    return "avance"


class AnalysisService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = StudentProfileRepository(db)

    async def list_careers(self) -> list[CareerPath]:
        result = await self.db.execute(
            select(CareerPath).options(selectinload(CareerPath.skills).selectinload(CareerPathSkill.skill))
        )
        return list(result.scalars().unique().all())

    async def get_career(self, career_id: int) -> CareerPath:
        career = await self.db.get(CareerPath, career_id)
        if not career:
            raise NotFoundError("Métier introuvable.")
        await self.db.refresh(career, ["skills"])
        return career

    async def run_analysis(self, user_id: int, career_path_id: int | None = None) -> AnalysisHistory:
        profile = await self.profile_repo.get_for_user(user_id)
        cp_id = career_path_id or (profile.career_path_id if profile else None)
        if not cp_id:
            raise ValidationError("Sélectionnez un métier cible avant l'analyse.")

        career = await self.get_career(cp_id)
        required = {cps.skill.name: cps.skill for cps in career.skills}

        user_skill_rows = (
            await self.db.execute(
                select(UserSkill).where(UserSkill.user_id == user_id).options(selectinload(UserSkill.skill))
            )
        ).scalars().all()
        owned_names = {us.skill.name for us in user_skill_rows}

        owned = [name for name in required if name in owned_names]
        missing = [name for name in required if name not in owned_names]

        total_weight = sum(s.weight for s in required.values()) or 1
        earned = sum(required[n].weight for n in owned)
        score = min(100, round(earned / total_weight * 100))
        level = score_to_level(score)

        if profile:
            await self.profile_repo.upsert_for_user(user_id, {"career_path_id": cp_id})

        record = AnalysisHistory(
            user_id=user_id,
            career_path_id=cp_id,
            score=score,
            level=level,
            owned_skills=owned,
            missing_skills=missing,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_latest(self, user_id: int) -> AnalysisHistory | None:
        result = await self.db.execute(
            select(AnalysisHistory)
            .where(AnalysisHistory.user_id == user_id)
            .order_by(AnalysisHistory.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history(self, user_id: int, limit: int = 20) -> list[AnalysisHistory]:
        result = await self.db.execute(
            select(AnalysisHistory)
            .where(AnalysisHistory.user_id == user_id)
            .order_by(AnalysisHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_skills(self, user_id: int) -> list[str]:
        rows = (
            await self.db.execute(
                select(Skill.name)
                .join(UserSkill, UserSkill.skill_id == Skill.id)
                .where(UserSkill.user_id == user_id)
            )
        ).all()
        return [r[0] for r in rows]
