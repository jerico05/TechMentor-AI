"""Personalized project recommendations via LLM — per-career guidance."""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field, ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.data.career_project_guidance import get_career_guidance
from app.models.analysis import AnalysisHistory
from app.services.analysis_service import AnalysisService
from app.services.llm_client import get_llm_client
from app.utils.user_level import level_label_fr, level_to_project_difficulty, normalize_level

logger = get_logger(__name__)


class _ProjectDataSourceLLM(BaseModel):
    name: str
    url: str
    note: str = ""


class _RecommendedProjectLLM(BaseModel):
    title: str
    tagline: str
    description: str
    track: str = "dev"
    difficulty: str
    skills_practiced: list[str] = Field(default_factory=list)
    estimated_weeks: int = Field(default=3, ge=1, le=24)
    impact: str | None = None
    stack: list[str] = Field(default_factory=list)
    data_sources: list[_ProjectDataSourceLLM] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)


class _ProjectsLLMResponse(BaseModel):
    projects: list[_RecommendedProjectLLM] = Field(default_factory=list)


def _parse_projects_llm(raw: str) -> list[dict]:
    match = re.search(r"\{.*\}", raw, re.S)
    try:
        data = json.loads(match.group() if match else raw)
        parsed = _ProjectsLLMResponse.model_validate(data)
        return [p.model_dump() for p in parsed.projects]
    except (json.JSONDecodeError, PydanticValidationError) as exc:
        logger.warning("projects.llm.parse_failed", error=str(exc))
        return []


def _build_prompt(
    *,
    career_name: str,
    career_slug: str,
    career_description: str,
    level: str,
    score: int,
    owned_skills: list[str],
    missing_skills: list[str],
    existing_projects: list[str] | None = None,
) -> str:
    guidance = get_career_guidance(career_slug)
    track = guidance.get("track", "dev")
    career_rules = guidance.get("prompt", "").strip()
    focus = ", ".join(missing_skills[:6]) or "compétences fondamentales du métier"
    owned = ", ".join(owned_skills[:8]) or "peu de compétences déclarées"
    description = career_description or "Non renseignée"
    done = ", ".join(existing_projects[:10]) if existing_projects else "aucun projet enregistré"

    return f"""Tu es un mentor carrière tech senior. Propose exactement 3 projets portfolio ultra-spécifiques au métier « {career_name} ».

Profil étudiant :
- Métier visé : {career_name} (slug: {career_slug})
- Description métier : {description}
- Niveau d'expérience : {level_label_fr(level)} — adapter la difficulté des projets à ce niveau (entry = projets guidés, senior = architecture avancée).
- Score de préparation métier : {score}/100 (écart de compétences déclarées, pas le niveau d'expérience).
- Compétences acquises : {owned}
- Compétences à renforcer : {focus}
- Projets déjà réalisés (ne pas reproposer) : {done}
- Catégorie projet (track) : {track}

Règles obligatoires :
- Projets réalistes, motivants, faisables en 2 à 8 semaines.
- Texte en français, sans markdown (pas de *, **, #).
- Chaque projet doit être UNIQUE à ce métier — pas de projets génériques recyclés.
- difficulty : "debutant", "intermediaire" ou "avance" (adapté au niveau {level}).
- impact : OBLIGATOIRE — pourquoi ce projet impressionne un recruteur pour CE métier précis.
- stack : technologies réellement utilisées dans ce métier aujourd'hui.
- deliverables : 3 à 5 livrables concrets et vérifiables.

Consignes spécifiques au métier :
{career_rules}

Sources de données :
- Si le métier touche à la data, l'IA, la sécurité ou le product : inclure au moins 1 data_sources avec URL réelle et accessible.
- Sinon (pur devops, frontend, backend sans data) : data_sources = [] sauf si le projet en a vraiment besoin.

Réponds UNIQUEMENT en JSON valide :
{{
  "projects": [
    {{
      "title": "Titre accrocheur et spécifique au métier",
      "tagline": "Phrase qui donne envie",
      "description": "2 à 4 phrases : objectif, approche technique, apprentissages",
      "track": "{track}",
      "difficulty": "debutant|intermediaire|avance",
      "skills_practiced": ["compétences du métier"],
      "estimated_weeks": 4,
      "impact": "Pourquoi ce projet compte pour un {career_name}",
      "stack": ["outils du métier"],
      "data_sources": [{{"name": "...", "url": "https://...", "note": "..."}}],
      "deliverables": ["...", "..."]
    }}
  ]
}}"""


def _fallback_by_track(track: str, level: str) -> list[dict]:
    if track in {"data", "ml"}:
        return _fallback_data_projects(level, track)
    if track == "design":
        return _fallback_design_projects(level)
    if track == "product":
        return _fallback_product_projects(level)
    if track == "security":
        return _fallback_security_projects(level)
    if track in {"devops", "cloud"}:
        return _fallback_devops_projects(level, track)
    if track == "ai":
        return _fallback_ai_projects(level)
    if track == "qa":
        return _fallback_qa_projects(level)
    if track == "mobile":
        return _fallback_mobile_projects(level)
    if track == "frontend":
        return _fallback_frontend_projects(level)
    if track == "backend":
        return _fallback_backend_projects(level)
    return _fallback_dev_projects(level)


def _fallback_projects(career_slug: str, level: str) -> list[dict]:
    guidance = get_career_guidance(career_slug)
    track = guidance.get("track", "dev")
    fallbacks = guidance.get("fallbacks", {})

    if level in fallbacks and fallbacks[level]:
        projects = [dict(p) for p in fallbacks[level]]
    elif level == "avance" and fallbacks.get("avance"):
        projects = [dict(p) for p in fallbacks["avance"]]
    else:
        projects = _fallback_by_track(track, level)

    for project in projects:
        project.setdefault("track", track)
    return projects


def _fallback_ai_projects(level: str) -> list[dict]:
    if level == "debutant":
        return [
            {
                "title": "Mini-RAG sur vos cours",
                "tagline": "Posez des questions à vos PDF de cours avec embeddings",
                "description": "Indexez 5 à 10 PDF dans Chroma ou pgvector, générez des embeddings et répondez aux questions via un LLM local (Ollama) ou API. Affichez les passages sources.",
                "track": "ai",
                "difficulty": "debutant",
                "skills_practiced": ["RAG", "Python", "Embeddings"],
                "estimated_weeks": 2,
                "impact": "Premier projet RAG concret — base indispensable pour un profil IA.",
                "stack": ["Python", "LangChain", "Chroma", "Ollama"],
                "data_sources": [
                    {
                        "name": "Hugging Face — sentence-transformers models",
                        "url": "https://huggingface.co/sentence-transformers",
                        "note": "Modèles d'embeddings open source",
                    }
                ],
                "deliverables": ["Script d'ingestion", "CLI question/réponse", "README"],
            },
        ]
    return [
        {
            "title": "DocMind — assistant RAG pgvector + FastAPI",
            "tagline": "RAG production-ready avec PostgreSQL et citations",
            "description": "Pipeline complet : chunking, embeddings, pgvector, API FastAPI streaming, évaluation faithfulness sur un benchmark. Architecture documentée.",
            "track": "ai",
            "difficulty": "avance",
            "skills_practiced": ["RAG", "pgvector", "LLMs", "FastAPI", "MLOps"],
            "estimated_weeks": 5,
            "impact": "Le projet que les recruteurs IA demandent : RAG réel, pas un chatbot basique.",
            "stack": ["Python", "FastAPI", "PostgreSQL", "pgvector", "LangChain", "Mistral"],
            "data_sources": [
                {
                    "name": "LangChain docs",
                    "url": "https://github.com/langchain-ai/langchain/tree/master/docs",
                    "note": "Corpus technique pour indexer",
                },
                {
                    "name": "Hugging Face — databricks-dolly-15k",
                    "url": "https://huggingface.co/datasets/databricks/databricks-dolly-15k",
                    "note": "Jeu d'évaluation Q&A",
                },
            ],
            "deliverables": ["API /chat/stream", "Index pgvector", "Métriques RAG", "Diagramme architecture"],
        },
    ]


def _fallback_data_projects(level: str, track: str = "data") -> list[dict]:
    if level == "debutant":
        return [
            {
                "title": "Explorateur du climat français",
                "tagline": "Visualisez des données ouvertes avec Pandas",
                "description": "Téléchargez des données météo, nettoyez-les et créez un dashboard Streamlit des tendances régionales.",
                "track": track,
                "difficulty": "debutant",
                "skills_practiced": ["Python", "Pandas", "Visualisation"],
                "estimated_weeks": 2,
                "impact": "Montre rigueur d'exploration et storytelling data.",
                "stack": ["Python", "Pandas", "Streamlit"],
                "data_sources": [
                    {"name": "data.gouv.fr — Climat", "url": "https://www.data.gouv.fr/fr/search/?q=climat", "note": "Données ouvertes"},
                ],
                "deliverables": ["Notebook EDA", "Dashboard Streamlit"],
            },
        ]
    return [
        {
            "title": "Pipeline ETL qualité de l'air",
            "tagline": "Ingestion, transformation et alerting",
            "description": "Collectez OpenAQ, orchestrez avec Airflow, stockez en PostgreSQL et alertez via Grafana.",
            "track": track,
            "difficulty": "avance",
            "skills_practiced": ["ETL", "SQL", "Airflow", "Docker"],
            "estimated_weeks": 5,
            "impact": "Compétences data engineering directement transférables en entreprise.",
            "stack": ["Python", "Airflow", "PostgreSQL", "Grafana"],
            "data_sources": [{"name": "OpenAQ", "url": "https://openaq.org/", "note": "API qualité de l'air"}],
            "deliverables": ["DAG Airflow", "Dashboard", "Alertes"],
        },
    ]


def _fallback_backend_projects(level: str) -> list[dict]:
    return [
        {
            "title": "API REST événementielle",
            "tagline": "Auth, cache Redis et tests d'intégration",
            "description": "API de réservation avec JWT, PostgreSQL, Redis et documentation OpenAPI complète.",
            "track": "backend",
            "difficulty": level if level in {"debutant", "intermediaire", "avance"} else "intermediaire",
            "skills_practiced": ["Spring Boot", "SQL", "Docker", "Git"],
            "estimated_weeks": 4,
            "impact": "Backend crédible avec patterns production.",
            "stack": ["Java", "Spring Boot", "PostgreSQL", "Redis"],
            "data_sources": [],
            "deliverables": ["API OpenAPI", "Tests intégration", "Docker Compose"],
        },
    ]


def _fallback_frontend_projects(level: str) -> list[dict]:
    return [
        {
            "title": "Dashboard SaaS interactif",
            "tagline": "UI premium avec animations et accessibilité",
            "description": "Dashboard React/Next.js responsive, dark mode, graphiques et score Lighthouse > 90.",
            "track": "frontend",
            "difficulty": level if level in {"debutant", "intermediaire", "avance"} else "intermediaire",
            "skills_practiced": ["React", "TypeScript", "CSS", "Testing"],
            "estimated_weeks": 4,
            "impact": "Portfolio visuel qui se démarque en 10 secondes.",
            "stack": ["Next.js", "TypeScript", "Tailwind CSS", "Recharts"],
            "data_sources": [],
            "deliverables": ["App déployée", "Storybook composants", "Rapport Lighthouse"],
        },
    ]


def _fallback_mobile_projects(level: str) -> list[dict]:
    return [
        {
            "title": "App mobile offline-first",
            "tagline": "React Native avec sync et notifications",
            "description": "App de suivi avec auth, API REST, cache local et push notifications.",
            "track": "mobile",
            "difficulty": level if level in {"debutant", "intermediaire", "avance"} else "intermediaire",
            "skills_practiced": ["React Native", "Firebase", "REST APIs"],
            "estimated_weeks": 5,
            "impact": "Une app complète vaut dix tutos sur un CV mobile.",
            "stack": ["React Native", "Expo", "Firebase", "TypeScript"],
            "data_sources": [],
            "deliverables": ["App TestFlight/Play internal", "Vidéo démo"],
        },
    ]


def _fallback_devops_projects(level: str, track: str) -> list[dict]:
    return [
        {
            "title": "Pipeline GitOps Kubernetes",
            "tagline": "CI/CD + IaC + déploiement automatisé",
            "description": "Terraform, Helm, GitHub Actions et déploiement sur cluster avec rollback automatique.",
            "track": track,
            "difficulty": "avance" if level == "avance" else "intermediaire",
            "skills_practiced": ["Kubernetes", "CI/CD", "Terraform", "Docker"],
            "estimated_weeks": 5,
            "impact": "Projet DevOps/SRE reconnu par les tech leads.",
            "stack": ["Terraform", "Kubernetes", "GitHub Actions", "Helm"],
            "data_sources": [],
            "deliverables": ["Repo IaC", "Pipeline CI/CD", "Runbook"],
        },
    ]


def _fallback_security_projects(level: str) -> list[dict]:
    return [
        {
            "title": "Audit OWASP automatisé",
            "tagline": "Scan de vulnérabilités + rapport professionnel",
            "description": "Testez une app vulnérable (Juice Shop), détectez OWASP Top 10 et produisez un rapport PDF avec remédiations.",
            "track": "security",
            "difficulty": level if level in {"debutant", "intermediaire", "avance"} else "intermediaire",
            "skills_practiced": ["Penetration Testing", "Python", "Security"],
            "estimated_weeks": 4,
            "impact": "Livrable rapport = crédibilité en entretien cybersécurité.",
            "stack": ["Python", "Docker", "OWASP ZAP"],
            "data_sources": [
                {"name": "OWASP Juice Shop", "url": "https://owasp.org/www-project-juice-shop/", "note": "Cible de test"},
            ],
            "deliverables": ["Scanner", "Rapport PDF", "Guide remédiation"],
        },
    ]


def _fallback_qa_projects(level: str) -> list[dict]:
    return [
        {
            "title": "Suite e2e Playwright + CI",
            "tagline": "Qualité bloquante sur chaque merge",
            "description": "30+ tests Playwright, tests API, GitHub Actions et rapport Allure.",
            "track": "qa",
            "difficulty": level if level in {"debutant", "intermediaire", "avance"} else "intermediaire",
            "skills_practiced": ["Testing", "CI/CD", "Cypress"],
            "estimated_weeks": 3,
            "impact": "Montre une culture qualité ingénieur, pas exécutant.",
            "stack": ["Playwright", "GitHub Actions", "Allure"],
            "data_sources": [],
            "deliverables": ["Suite e2e", "Pipeline CI", "Rapport Allure"],
        },
    ]


def _fallback_product_projects(level: str) -> list[dict]:
    return [
        {
            "title": "PRD et roadmap SaaS B2B",
            "tagline": "Du problème utilisateur au plan produit chiffré",
            "description": "Interviews, PRD, roadmap priorisée RICE, wireframes Figma et dashboard métriques SQL.",
            "track": "product",
            "difficulty": level if level in {"debutant", "intermediaire", "avance"} else "intermediaire",
            "skills_practiced": ["Roadmapping", "Analytics", "Agile", "UX"],
            "estimated_weeks": 4,
            "impact": "Portfolio PM : le PRD est lu avant tout en entretien.",
            "stack": ["Notion", "Figma", "SQL"],
            "data_sources": [
                {"name": "data.gouv.fr", "url": "https://www.data.gouv.fr/", "note": "Données marché"},
            ],
            "deliverables": ["PRD", "Roadmap", "Wireframes", "Dashboard métriques"],
        },
    ]


def _fallback_dev_projects(level: str) -> list[dict]:
    if level == "debutant":
        return [
            {
                "title": "TaskFlow — SaaS collaboratif",
                "tagline": "To-do avec auth et partage d'équipe",
                "description": "CRUD, authentification, listes partagées et tests unitaires.",
                "track": "fullstack",
                "difficulty": "debutant",
                "skills_practiced": ["CRUD", "Authentification", "SQL"],
                "estimated_weeks": 3,
                "impact": "Premier produit complet sur le portfolio.",
                "stack": ["React", "Node.js", "PostgreSQL"],
                "data_sources": [],
                "deliverables": ["Repo GitHub", "Démo en ligne"],
            },
        ]
    return [
        {
            "title": "CollabBoard temps réel",
            "tagline": "Tableau blanc collaboratif WebSocket",
            "description": "Canvas infini, curseurs multi-utilisateurs, rooms et export PNG.",
            "track": "fullstack",
            "difficulty": "avance",
            "skills_practiced": ["WebSockets", "React", "Redis"],
            "estimated_weeks": 6,
            "impact": "Projet spectaculaire en démo live.",
            "stack": ["TypeScript", "React", "WebSockets", "Redis", "Docker"],
            "data_sources": [],
            "deliverables": ["Démo multi-users", "Tests e2e", "Vidéo démo"],
        },
    ]


def _fallback_design_projects(level: str) -> list[dict]:
    return [
        {
            "title": "Refonte UX app bancaire",
            "tagline": "Case study complet avec tests utilisateurs",
            "description": "Audit, wireframes, prototype Figma haute fidélité et tests sur 5 utilisateurs.",
            "track": "design",
            "difficulty": level if level in {"debutant", "intermediaire", "avance"} else "intermediaire",
            "skills_practiced": ["Figma", "UX Research", "Prototyping"],
            "estimated_weeks": 3,
            "impact": "Case study design très valorisé en portfolio.",
            "stack": ["Figma", "FigJam", "Maze"],
            "data_sources": [],
            "deliverables": ["Audit", "Prototype", "Rapport tests"],
        },
    ]


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.analysis = AnalysisService(db)

    async def recommend(self, user_id: int) -> dict:
        latest = await self.analysis.get_latest(user_id)
        if not latest:
            raise ValidationError("Lancez d'abord une analyse de compétences pour obtenir des projets adaptés.")

        career = await self.analysis.get_career(latest.career_path_id)
        level = normalize_level(latest.level)
        project_difficulty = level_to_project_difficulty(level)

        projects = await self._generate_with_llm(
            latest, career.name, career.slug, career.description or "", level, user_id
        )
        if not projects:
            logger.info("projects.fallback", user_id=user_id, career=career.slug, level=level)
            projects = _fallback_projects(career.slug, project_difficulty)

        guidance = get_career_guidance(career.slug)
        for project in projects:
            project.setdefault("track", guidance.get("track", "dev"))

        return {
            "level": level,
            "score": latest.score,
            "missing_skills": latest.missing_skills,
            "career_name": career.name,
            "career_slug": career.slug,
            "projects": projects[:3],
        }

    async def list_completions(self, user_id: int) -> list[str]:
        from sqlalchemy import select

        from app.models.user_project import UserProjectCompletion

        rows = await self.db.scalars(
            select(UserProjectCompletion.project_title)
            .where(UserProjectCompletion.user_id == user_id)
            .order_by(UserProjectCompletion.created_at.desc())
        )
        return list(rows.all())

    async def mark_complete(self, user_id: int, title: str, career_slug: str | None = None) -> list[str]:
        from sqlalchemy import select

        from app.models.user_project import UserProjectCompletion

        existing = await self.db.scalar(
            select(UserProjectCompletion).where(
                UserProjectCompletion.user_id == user_id,
                UserProjectCompletion.project_title == title,
            )
        )
        if not existing:
            self.db.add(
                UserProjectCompletion(
                    user_id=user_id,
                    project_title=title,
                    career_slug=career_slug,
                )
            )
            await self.db.commit()
        await self.analysis.refresh_experience_level(user_id)
        return await self.list_completions(user_id)

    async def mark_incomplete(self, user_id: int, title: str) -> list[str]:
        from sqlalchemy import delete

        from app.models.user_project import UserProjectCompletion

        await self.db.execute(
            delete(UserProjectCompletion).where(
                UserProjectCompletion.user_id == user_id,
                UserProjectCompletion.project_title == title,
            )
        )
        await self.db.commit()
        await self.analysis.refresh_experience_level(user_id)
        return await self.list_completions(user_id)

    async def _existing_project_titles(self, user_id: int) -> list[str]:
        from sqlalchemy import select

        from app.models.user_portfolio_project import UserPortfolioProject

        rows = await self.db.scalars(
            select(UserPortfolioProject.title)
            .where(
                UserPortfolioProject.user_id == user_id,
                UserPortfolioProject.status == "completed",
            )
            .order_by(UserPortfolioProject.created_at.desc())
        )
        return list(rows.all())

    async def _generate_with_llm(
        self,
        latest: AnalysisHistory,
        career_name: str,
        career_slug: str,
        career_description: str,
        experience_level: str,
        user_id: int,
    ) -> list[dict]:
        if not settings.mistral_api_key or settings.mistral_api_key == "change-me":
            return []

        existing = await self._existing_project_titles(user_id)
        prompt = _build_prompt(
            career_name=career_name,
            career_slug=career_slug,
            career_description=career_description,
            level=experience_level,
            score=latest.score,
            owned_skills=latest.owned_skills,
            missing_skills=latest.missing_skills,
            existing_projects=existing,
        )

        try:
            client = get_llm_client()
            completion = await client.chat.completions.create(
                model=settings.mistral_default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.75,
                max_tokens=3200,
            )
            raw = completion.choices[0].message.content or "{}"
            projects = _parse_projects_llm(raw)
            if len(projects) < 2:
                return []
            return projects
        except Exception as exc:
            logger.warning("projects.llm.failed", error=str(exc))
            return []
