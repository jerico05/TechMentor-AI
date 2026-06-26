"""User portfolio projects - add by link, extract metadata, drive experience level."""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.user_portfolio_project import UserPortfolioProject
from app.repositories.student_profile_repository import StudentProfileRepository
from app.services.analysis_service import AnalysisService
from app.utils.portfolio_site_extract import discover_project_urls
from app.utils.project_extract import extract_project_from_url
from app.utils.url_extract import normalize_url

logger = get_logger(__name__)


class PortfolioProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.profile_repo = StudentProfileRepository(db)
        self.analysis = AnalysisService(db)

    async def list_for_user(self, user_id: int) -> list[UserPortfolioProject]:
        rows = await self.db.scalars(
            select(UserPortfolioProject)
            .where(UserPortfolioProject.user_id == user_id)
            .order_by(UserPortfolioProject.created_at.desc())
        )
        return list(rows.all())

    async def count_completed(self, user_id: int) -> int:
        result = await self.db.scalar(
            select(func.count())
            .select_from(UserPortfolioProject)
            .where(
                UserPortfolioProject.user_id == user_id,
                UserPortfolioProject.status == "completed",
            )
        )
        return int(result or 0)

    async def add_project(self, user_id: int, url: str) -> UserPortfolioProject:
        normalized = normalize_url(url)
        existing = await self.db.scalar(
            select(UserPortfolioProject).where(
                UserPortfolioProject.user_id == user_id,
                UserPortfolioProject.url == normalized,
            )
        )
        if existing:
            if existing.status == "failed":
                return await self._process_project(existing)
            raise ValidationError("Ce projet est déjà enregistré.")

        project = UserPortfolioProject(
            user_id=user_id,
            url=normalized,
            title="Extraction en cours...",
            status="processing",
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return await self._process_project(project)

    async def _process_project(self, project: UserPortfolioProject) -> UserPortfolioProject:
        try:
            data = await extract_project_from_url(project.url)
            project.url = data["url"]
            project.title = data["title"]
            project.summary = data.get("summary")
            project.stack = data.get("stack") or []
            project.source = data.get("source") or "web"
            project.status = "completed"
            await self.db.commit()
            await self.db.refresh(project)
            await self.analysis.refresh_experience_level(project.user_id)
            logger.info("portfolio.project.completed", user_id=project.user_id, title=project.title)
            return project
        except Exception as exc:
            project.status = "failed"
            project.title = project.url.rstrip("/").split("/")[-1][:255] or "Projet"
            await self.db.commit()
            await self.db.refresh(project)
            if isinstance(exc, ValidationError):
                raise exc
            logger.warning("portfolio.project.failed", user_id=project.user_id, error=str(exc))
            raise ValidationError("Extraction du projet impossible. Vérifiez le lien.") from exc

    async def delete_project(self, user_id: int, project_id: int) -> list[UserPortfolioProject]:
        project = await self.db.get(UserPortfolioProject, project_id)
        if not project or project.user_id != user_id:
            raise NotFoundError("Projet introuvable.")
        await self.db.delete(project)
        await self.db.commit()
        await self.analysis.refresh_experience_level(user_id)
        return await self.list_for_user(user_id)

    async def save_portfolio_url(
        self,
        user_id: int,
        portfolio_url: str | None,
        *,
        extract_projects: bool = True,
    ) -> tuple[int, int]:
        """Save portfolio site URL and optionally discover project links."""
        url = normalize_url(portfolio_url) if portfolio_url else None
        await self.profile_repo.upsert_for_user(user_id, {"portfolio_url": url})

        discovered = 0
        added = 0
        if not url or not extract_projects:
            return discovered, added

        try:
            project_urls = await discover_project_urls(url)
        except ValidationError:
            raise
        except Exception as exc:
            logger.warning("portfolio.site.extract_failed", user_id=user_id, error=str(exc))
            raise ValidationError(
                "Impossible d'analyser ce site portfolio. Vérifiez l'URL ou ajoutez vos projets un par un."
            ) from exc

        discovered = len(project_urls)
        for project_url in project_urls:
            try:
                await self.add_project(user_id, project_url)
                added += 1
            except ValidationError as exc:
                if "déjà enregistré" in str(exc).lower():
                    continue
                logger.warning(
                    "portfolio.site.project_skip",
                    user_id=user_id,
                    url=project_url,
                    error=str(exc),
                )

        if discovered > 0 and added == 0:
            logger.info(
                "portfolio.site.all_existing",
                user_id=user_id,
                discovered=discovered,
            )

        return discovered, added
