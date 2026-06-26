"""Skill gap analysis & scoring."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError, ValidationError
from app.models.analysis import AnalysisHistory
from app.models.linkedin_analysis import LinkedInAnalysis
from app.models.skill import CareerPath, CareerPathSkill, Skill, UserSkill
from app.models.user_portfolio_project import UserPortfolioProject
from app.models.user_project import UserProjectCompletion
from app.repositories.student_profile_repository import StudentProfileRepository
from app.utils.skill_gap_score import SkillEvidence, compute_strict_skill_gap_score
from app.utils.linkedin_extract import _normalize_certification
from app.utils.user_level import compute_experience_level, normalize_level


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

    async def _build_evidence_for_user(self, user_id: int) -> dict[str, SkillEvidence]:
        user_skill_rows = (
            await self.db.execute(
                select(UserSkill).where(UserSkill.user_id == user_id).options(selectinload(UserSkill.skill))
            )
        ).scalars().all()
        return {
            row.skill.name: SkillEvidence(confidence=row.confidence, source=row.source)
            for row in user_skill_rows
        }

    async def compute_career_skill_gap(
        self,
        user_id: int,
        career: CareerPath,
        *,
        extra_evidence: dict[str, SkillEvidence] | None = None,
    ) -> tuple[int, list[str], list[str]]:
        required = {cps.skill.name: cps.skill for cps in career.skills}
        evidence = await self._build_evidence_for_user(user_id)
        if extra_evidence:
            evidence = {**evidence, **extra_evidence}
        return compute_strict_skill_gap_score(required, evidence)

    async def run_analysis(self, user_id: int, career_path_id: int | None = None) -> AnalysisHistory:
        profile = await self.profile_repo.get_for_user(user_id)
        cp_id = career_path_id or (profile.career_path_id if profile else None)
        if not cp_id:
            raise ValidationError("Sélectionnez un métier cible avant l'analyse.")

        career = await self.get_career(cp_id)
        score, owned, missing = await self.compute_career_skill_gap(user_id, career)
        level = await self._compute_level_for_user(user_id)

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

    async def count_completed_projects(self, user_id: int) -> int:
        portfolio_count = await self.db.scalar(
            select(func.count())
            .select_from(UserPortfolioProject)
            .where(
                UserPortfolioProject.user_id == user_id,
                UserPortfolioProject.status == "completed",
            )
        )
        legacy_count = await self.db.scalar(
            select(func.count())
            .select_from(UserProjectCompletion)
            .where(UserProjectCompletion.user_id == user_id)
        )
        return int(portfolio_count or 0) + int(legacy_count or 0)

    async def _experience_context(self, user_id: int) -> dict:
        profile = await self.profile_repo.get_for_user(user_id)
        projects_completed = await self.count_completed_projects(user_id)
        experience_years = await self._linkedin_experience_years(user_id)
        return {
            "projects_completed": projects_completed,
            "experience_years": experience_years,
            "academic_level": profile.academic_level if profile else None,
        }

    async def _linkedin_experience_years(self, user_id: int) -> float | None:
        result = await self.db.execute(
            select(LinkedInAnalysis.total_experience_years).where(
                LinkedInAnalysis.user_id == user_id,
                LinkedInAnalysis.status == "completed",
            )
        )
        value = result.scalar_one_or_none()
        if value is None:
            return None
        return float(value)

    async def get_linkedin_certifications(self, user_id: int) -> list[dict]:
        result = await self.db.execute(
            select(LinkedInAnalysis.certifications).where(
                LinkedInAnalysis.user_id == user_id,
                LinkedInAnalysis.status == "completed",
            )
        )
        certs = result.scalar_one_or_none()
        if not isinstance(certs, list):
            return []
        normalized: list[dict] = []
        for item in certs:
            if not isinstance(item, dict):
                continue
            cleaned = _normalize_certification(item)
            if cleaned:
                normalized.append(cleaned)
        return normalized

    async def _compute_level_for_user(self, user_id: int) -> str:
        ctx = await self._experience_context(user_id)
        return compute_experience_level(
            projects_completed=ctx["projects_completed"],
            experience_years=ctx["experience_years"],
        )

    async def refresh_experience_level(self, user_id: int) -> AnalysisHistory | None:
        """Recompute level after project completion without full skill-gap rerun."""
        latest = await self.get_latest(user_id)
        if latest is None:
            return None
        new_level = await self._compute_level_for_user(user_id)
        if normalize_level(new_level) == normalize_level(latest.level):
            return latest
        record = AnalysisHistory(
            user_id=user_id,
            career_path_id=latest.career_path_id,
            score=latest.score,
            level=new_level,
            owned_skills=list(latest.owned_skills),
            missing_skills=list(latest.missing_skills),
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
