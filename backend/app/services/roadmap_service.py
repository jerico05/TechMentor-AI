"""Roadmap generation via LLM."""

from __future__ import annotations

import json
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.analysis import Roadmap
from app.services.analysis_service import AnalysisService
from app.services.rodium_client import get_rodium_client
from app.rag.retriever import retrieve_for_roadmap

logger = get_logger(__name__)


class RoadmapService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.analysis = AnalysisService(db)

    async def generate(self, user_id: int, career_path_id: int | None = None) -> Roadmap:
        latest = await self.analysis.get_latest(user_id)
        if latest is None:
            latest = await self.analysis.run_analysis(user_id, career_path_id)
        elif career_path_id and career_path_id != latest.career_path_id:
            latest = await self.analysis.run_analysis(user_id, career_path_id)

        career = await self.analysis.get_career(latest.career_path_id)
        rag_context = retrieve_for_roadmap(career.name, latest.missing_skills)
        prompt = f"""Génère une roadmap d'apprentissage personnalisée sur 3 mois pour devenir {career.name}.
Score actuel: {latest.score}/100 (niveau {latest.level}).
Compétences acquises: {', '.join(latest.owned_skills) or 'aucune'}.
Compétences manquantes: {', '.join(latest.missing_skills)}.

{rag_context}

Réponds UNIQUEMENT en JSON avec ce format:
{{
  "months": [
    {{"month": 1, "title": "...", "skills": ["..."], "actions": ["..."]}},
    {{"month": 2, "title": "...", "skills": ["..."], "actions": ["..."]}},
    {{"month": 3, "title": "...", "skills": ["..."], "actions": ["..."]}}
  ],
  "summary": "..."
}}"""

        client = get_rodium_client()
        completion = await client.chat.completions.create(
            model=settings.rodium_default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1200,
        )
        raw = completion.choices[0].message.content or "{}"
        match = re.search(r"\{.*\}", raw, re.S)
        try:
            content = json.loads(match.group() if match else raw)
        except json.JSONDecodeError:
            content = {"months": [], "summary": raw, "raw": True}

        await self.db.execute(
            select(Roadmap).where(Roadmap.user_id == user_id, Roadmap.status == "active")
        )
        existing = (
            await self.db.execute(
                select(Roadmap).where(Roadmap.user_id == user_id, Roadmap.status == "active")
            )
        ).scalar_one_or_none()
        if existing:
            existing.status = "archived"

        roadmap = Roadmap(
            user_id=user_id,
            career_path_id=latest.career_path_id,
            content=content,
            status="active",
        )
        self.db.add(roadmap)
        await self.db.commit()
        await self.db.refresh(roadmap)
        logger.info("roadmap.generated", user_id=user_id, career=career.slug)
        return roadmap

    async def get_active(self, user_id: int) -> Roadmap | None:
        result = await self.db.execute(
            select(Roadmap)
            .where(Roadmap.user_id == user_id, Roadmap.status == "active")
            .order_by(Roadmap.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> list[Roadmap]:
        result = await self.db.execute(
            select(Roadmap).where(Roadmap.user_id == user_id).order_by(Roadmap.created_at.desc())
        )
        return list(result.scalars().all())
