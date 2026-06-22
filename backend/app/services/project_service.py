"""Project recommendations based on skill level."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.data.seed_careers import PROJECTS_BY_LEVEL
from app.services.analysis_service import AnalysisService


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.analysis = AnalysisService(db)

    async def recommend(self, user_id: int) -> dict:
        latest = await self.analysis.get_latest(user_id)
        level = latest.level if latest else "debutant"
        projects = PROJECTS_BY_LEVEL.get(level, PROJECTS_BY_LEVEL["debutant"])
        missing = latest.missing_skills if latest else []
        return {
            "level": level,
            "score": latest.score if latest else 0,
            "missing_skills": missing,
            "projects": projects,
        }
