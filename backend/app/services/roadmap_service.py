"""Roadmap generation via LLM."""

from __future__ import annotations

import json
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.models.analysis import Roadmap
from app.services.analysis_service import AnalysisService
from app.services.llm_client import get_llm_client
from app.rag.retriever import retrieve_for_roadmap_async
from app.utils.roadmap_courses import sanitize_roadmap_courses
from app.utils.roadmap_duration import (
    normalize_roadmap_duration,
    suggestion_reason,
    suggest_roadmap_duration,
)
from app.utils.user_level import ROADMAP_LEVEL_GUIDANCE, level_label_fr, normalize_level

logger = get_logger(__name__)


def _months_json_template(count: int) -> str:
    course = (
        '{"title": "...", "platform": "...", "url": "https://...", '
        '"type": "gratuit|payant|freemium", "note": "..."}'
    )
    rows = [
        f'    {{"month": {i}, "title": "...", "skills": ["..."], "actions": ["..."], '
        f'"courses": [{course}]}}'
        for i in range(1, count + 1)
    ]
    return "[\n" + ",\n".join(rows) + "\n  ]"


class RoadmapService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.analysis = AnalysisService(db)

    async def suggest_duration(self, user_id: int, career_path_id: int | None = None) -> dict:
        latest = await self.analysis.get_latest(user_id)
        if latest is None:
            return {
                "suggested_months": 6,
                "level": None,
                "missing_skills_count": 0,
                "reason": "Lancez d'abord une analyse skill gap pour une recommandation personnalisée.",
            }
        if career_path_id and career_path_id != latest.career_path_id:
            latest = await self.analysis.run_analysis(user_id, career_path_id)

        missing_count = len(latest.missing_skills)
        months = suggest_roadmap_duration(latest.level, missing_count)
        return {
            "suggested_months": months,
            "level": latest.level,
            "missing_skills_count": missing_count,
            "reason": suggestion_reason(latest.level, missing_count, months),
        }

    async def generate(
        self,
        user_id: int,
        career_path_id: int | None = None,
        duration_months: int | None = None,
    ) -> Roadmap:
        latest = await self.analysis.get_latest(user_id)
        if latest is None:
            latest = await self.analysis.run_analysis(user_id, career_path_id)
        elif career_path_id and career_path_id != latest.career_path_id:
            latest = await self.analysis.run_analysis(user_id, career_path_id)

        career = await self.analysis.get_career(latest.career_path_id)
        missing_count = len(latest.missing_skills)
        months = normalize_roadmap_duration(duration_months, latest.level, missing_count)
        rag_context = await retrieve_for_roadmap_async(career.name, latest.missing_skills)
        level_slug = normalize_level(latest.level)
        level_guidance = ROADMAP_LEVEL_GUIDANCE.get(level_slug, "")
        level_display = level_label_fr(latest.level)
        projects_done = await self.analysis.count_completed_projects(user_id)
        prompt = f"""Génère une roadmap d'apprentissage personnalisée sur {months} mois pour devenir {career.name}.

Profil étudiant :
- Niveau d'expérience : {level_display} ({level_slug}) — ce niveau DOIT fortement influencer le rythme et la profondeur.
- Projets portfolio déjà réalisés et validés : {projects_done}.
- Score de préparation métier (écarts de compétences) : {latest.score}/100 — indique le % de compétences du métier déjà déclarées, PAS le niveau d'expérience.
- Compétences acquises : {', '.join(latest.owned_skills) or 'aucune'}.
- Compétences manquantes à combler : {', '.join(latest.missing_skills) or 'aucune'}.

{level_guidance}

{rag_context}

Réponds UNIQUEMENT en JSON avec ce format:
{{
  "months": {_months_json_template(months)},
  "summary": "..."
}}

Règles :
- Adapte la difficulté au niveau {level_display} : un entry level commence par les bases, un senior va plus vite sur l'essentiel.
- Chaque mois : titre court, 2 à 4 compétences ciblées, 2 actions concrètes réalisables.
- Répartis la progression logiquement du mois 1 au mois {months}.
- Texte en français, sans markdown.

Cours recommandés (OBLIGATOIRE pour chaque mois) :
- Inclure 1 à 2 cours dans "courses" par mois (maximum 2).
- Chaque cours : title, platform (nom du site ou source : Coursera, Udemy, Cisco Networking Academy, freeCodeCamp, OpenClassrooms, edX, YouTube, MDN, documentation officielle, etc. — toute plateforme pertinente sur le web).
- url : lien HTTPS réel vers une page de cours, formation ou ressource pédagogique existante (pas d'URL inventée).
- type : "gratuit", "payant" ou "freemium".
- note : une courte phrase expliquant pourquoi ce cours pour ce mois.
- Varier les plateformes sur la roadmap ; chercher les meilleures ressources du web, pas seulement les MOOC classiques.
- Adapter chaque cours au métier {career.name}, au niveau {level_display} et aux compétences du mois."""

        if not settings.mistral_api_key or settings.mistral_api_key == "change-me":
            raise ValidationError(
                "Génération de roadmap indisponible : configurez MISTRAL_API_KEY dans le backend."
            )

        try:
            client = get_llm_client()
            completion = await client.chat.completions.create(
                model=settings.mistral_default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=min(4500, 700 + months * 320),
            )
            raw = completion.choices[0].message.content or "{}"
        except Exception as exc:
            logger.warning("roadmap.llm.failed", user_id=user_id, error=str(exc))
            raise ValidationError(
                "Impossible de générer la roadmap pour le moment. Réessayez plus tard."
            ) from exc

        match = re.search(r"\{.*\}", raw, re.S)
        try:
            content = json.loads(match.group() if match else raw)
        except json.JSONDecodeError:
            content = {"months": [], "summary": raw, "raw": True}

        if isinstance(content, dict):
            content = sanitize_roadmap_courses(content)

        existing_rows = (
            await self.db.execute(
                select(Roadmap).where(Roadmap.user_id == user_id, Roadmap.status == "active")
            )
        ).scalars().all()
        for existing in existing_rows:
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
