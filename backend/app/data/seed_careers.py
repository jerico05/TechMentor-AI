"""Seed career paths and skills catalog."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.skill import CareerPath, CareerPathSkill, Skill

logger = get_logger(__name__)

CATALOG: list[dict] = [
    {
        "slug": "ai-engineer",
        "name": "Ingénieur IA",
        "description": "Conception de systèmes IA, LLM et agents intelligents.",
        "skills": [
            ("Python", "language", 20),
            ("Machine Learning", "domain", 20),
            ("LLMs", "domain", 20),
            ("MLOps", "devops", 15),
            ("Docker", "devops", 10),
            ("Git", "tool", 15),
        ],
    },
    {
        "slug": "ml-engineer",
        "name": "ML Engineer",
        "description": "Déploiement et industrialisation de modèles en production.",
        "skills": [
            ("Python", "language", 20),
            ("Machine Learning", "domain", 25),
            ("MLOps", "devops", 20),
            ("Kubernetes", "devops", 15),
            ("SQL", "database", 10),
            ("Git", "tool", 10),
        ],
    },
    {
        "slug": "prompt-engineer",
        "name": "Prompt Engineer",
        "description": "Optimisation de prompts, RAG et applications GenAI.",
        "skills": [
            ("LLMs", "domain", 25),
            ("Python", "language", 20),
            ("NLP", "domain", 20),
            ("RAG", "domain", 20),
            ("Git", "tool", 15),
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
        "slug": "frontend-developer",
        "name": "Frontend Developer",
        "description": "Interfaces web modernes, accessibles et performantes.",
        "skills": [
            ("TypeScript", "language", 20),
            ("React", "framework", 25),
            ("CSS", "frontend", 15),
            ("Git", "tool", 15),
            ("Testing", "tool", 10),
            ("Figma", "design", 15),
        ],
    },
    {
        "slug": "fullstack-developer",
        "name": "Fullstack Developer",
        "description": "Développement bout-en-bout, du front au back.",
        "skills": [
            ("TypeScript", "language", 20),
            ("React", "framework", 20),
            ("Node.js", "runtime", 15),
            ("SQL", "database", 15),
            ("Docker", "devops", 15),
            ("Git", "tool", 15),
        ],
    },
    {
        "slug": "mobile-developer",
        "name": "Développeur Mobile",
        "description": "Applications iOS, Android et cross-platform.",
        "skills": [
            ("React Native", "framework", 20),
            ("TypeScript", "language", 15),
            ("REST APIs", "domain", 15),
            ("Git", "tool", 15),
            ("Firebase", "platform", 15),
            ("Testing", "tool", 20),
        ],
    },
    {
        "slug": "devops-engineer",
        "name": "DevOps Engineer",
        "description": "CI/CD, automatisation et fiabilité des déploiements.",
        "skills": [
            ("Docker", "devops", 20),
            ("Kubernetes", "devops", 20),
            ("CI/CD", "devops", 20),
            ("Linux", "os", 15),
            ("Terraform", "iac", 15),
            ("Git", "tool", 10),
        ],
    },
    {
        "slug": "cloud-architect",
        "name": "Architecte Cloud",
        "description": "Architecture cloud scalable, sécurisée et résiliente.",
        "skills": [
            ("AWS", "cloud", 25),
            ("Terraform", "iac", 20),
            ("Kubernetes", "devops", 15),
            ("Networking", "domain", 15),
            ("Security", "domain", 15),
            ("Docker", "devops", 10),
        ],
    },
    {
        "slug": "sre-engineer",
        "name": "Site Reliability Engineer",
        "description": "Observabilité, performance et haute disponibilité.",
        "skills": [
            ("Kubernetes", "devops", 20),
            ("Monitoring", "devops", 20),
            ("Linux", "os", 15),
            ("Python", "language", 15),
            ("CI/CD", "devops", 15),
            ("Docker", "devops", 15),
        ],
    },
    {
        "slug": "cybersecurity-engineer",
        "name": "Ingénieur Cybersécurité",
        "description": "Protection des systèmes, audits et réponse aux incidents.",
        "skills": [
            ("Security", "domain", 25),
            ("Linux", "os", 15),
            ("Networking", "domain", 15),
            ("Python", "language", 15),
            ("Penetration Testing", "domain", 15),
            ("Git", "tool", 15),
        ],
    },
    {
        "slug": "qa-engineer",
        "name": "Ingénieur QA",
        "description": "Tests automatisés, qualité logicielle et assurance produit.",
        "skills": [
            ("Testing", "tool", 25),
            ("Cypress", "framework", 15),
            ("CI/CD", "devops", 15),
            ("SQL", "database", 15),
            ("Git", "tool", 15),
            ("Python", "language", 15),
        ],
    },
    {
        "slug": "product-manager-tech",
        "name": "Product Manager Tech",
        "description": "Vision produit, roadmap et coordination équipes tech.",
        "skills": [
            ("Agile", "methodology", 20),
            ("Analytics", "domain", 20),
            ("SQL", "database", 15),
            ("UX", "design", 15),
            ("Roadmapping", "domain", 15),
            ("Git", "tool", 15),
        ],
    },
    {
        "slug": "ux-ui-designer",
        "name": "Designer UX/UI",
        "description": "Expérience utilisateur, interfaces et design systems.",
        "skills": [
            ("Figma", "design", 25),
            ("Design Systems", "design", 20),
            ("Prototyping", "design", 15),
            ("HTML", "frontend", 10),
            ("CSS", "frontend", 15),
            ("User Research", "design", 15),
        ],
    },
]

async def seed_career_catalog(db: AsyncSession) -> None:
    logger.info("seed.careers.start")

    skill_cache: dict[str, Skill] = {}
    existing_skills = await db.scalars(select(Skill))
    for skill in existing_skills:
        skill_cache[skill.name] = skill

    added = 0
    for entry in CATALOG:
        career = await db.scalar(select(CareerPath).where(CareerPath.slug == entry["slug"]))
        if career:
            continue

        career = CareerPath(slug=entry["slug"], name=entry["name"], description=entry["description"])
        db.add(career)
        await db.flush()
        added += 1

        for name, category, weight in entry["skills"]:
            if name not in skill_cache:
                skill = Skill(name=name, category=category, weight=weight)
                db.add(skill)
                await db.flush()
                skill_cache[name] = skill
            else:
                skill = skill_cache[name]

            db.add(CareerPathSkill(career_path_id=career.id, skill_id=skill.id))

    if added:
        await db.commit()
        logger.info("seed.careers.done", added=added, total=len(CATALOG))
    else:
        logger.info("seed.careers.up_to_date", total=len(CATALOG))
