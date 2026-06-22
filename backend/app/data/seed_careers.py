"""Seed career paths and skills catalog."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.skill import CareerPath, CareerPathSkill, Skill

logger = get_logger(__name__)

CATALOG: list[dict] = [
    {
        "slug": "backend-developer",
        "name": "Backend Developer",
        "description": "Développement d'APIs et services côté serveur.",
        "skills": [
            ("Java", "language", 20),
            ("Spring Boot", "framework", 20),
            ("SQL", "database", 20),
            ("Git", "tool", 10),
            ("Docker", "devops", 15),
            ("Python", "language", 15),
        ],
    },
    {
        "slug": "data-scientist",
        "name": "Data Scientist",
        "description": "Analyse de données et modèles de machine learning.",
        "skills": [
            ("Python", "language", 25),
            ("Pandas", "library", 20),
            ("Numpy", "library", 15),
            ("Machine Learning", "domain", 25),
            ("SQL", "database", 15),
        ],
    },
    {
        "slug": "data-engineer",
        "name": "Data Engineer",
        "description": "Pipelines de données et infrastructure analytique.",
        "skills": [
            ("Python", "language", 20),
            ("SQL", "database", 20),
            ("Spark", "bigdata", 20),
            ("Airflow", "orchestration", 15),
            ("Docker", "devops", 15),
            ("Git", "tool", 10),
        ],
    },
]

PROJECTS_BY_LEVEL: dict[str, list[dict]] = {
    "debutant": [
        {"title": "Gestion de bibliothèque", "description": "CRUD simple avec base de données relationnelle."},
        {"title": "Todo App", "description": "Application de tâches avec authentification basique."},
    ],
    "intermediaire": [
        {"title": "API REST complète", "description": "API documentée avec tests et déploiement Docker."},
        {"title": "Dashboard analytique", "description": "Visualisation de données avec filtres et export."},
    ],
    "avance": [
        {"title": "Pipeline ETL", "description": "Ingestion, transformation et chargement de données."},
        {"title": "Système temps réel", "description": "WebSockets ou streaming pour notifications live."},
    ],
}


async def seed_career_catalog(db: AsyncSession) -> None:
    existing = await db.scalar(select(CareerPath.id).limit(1))
    if existing:
        return

    logger.info("seed.careers.start")
    skill_cache: dict[str, Skill] = {}

    for entry in CATALOG:
        career = CareerPath(slug=entry["slug"], name=entry["name"], description=entry["description"])
        db.add(career)
        await db.flush()

        for name, category, weight in entry["skills"]:
            if name not in skill_cache:
                skill = Skill(name=name, category=category, weight=weight)
                db.add(skill)
                await db.flush()
                skill_cache[name] = skill
            else:
                skill = skill_cache[name]

            db.add(CareerPathSkill(career_path_id=career.id, skill_id=skill.id))

    await db.commit()
    logger.info("seed.careers.done", paths=len(CATALOG))
