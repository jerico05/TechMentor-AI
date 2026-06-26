"""Evaluate project proof-of-work submissions via LLM + GitHub API."""

from __future__ import annotations

import base64
import json
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.models.project_submission import ProjectSubmission
from app.models.user_project import UserProjectCompletion
from app.services.llm_client import get_llm_client
from app.utils.github_api import github_get

logger = get_logger(__name__)

APPROVAL_THRESHOLD = 75  # score minimum pour valider un projet
_GITHUB_REPO_RE = re.compile(
    r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git|/|$)"
)


def _parse_github_repo(url: str) -> tuple[str, str] | None:
    """Return (owner, repo) from a GitHub URL, or None."""
    m = _GITHUB_REPO_RE.search(url)
    if not m:
        return None
    return m.group(1), m.group(2)


async def _fetch_repo_context(github_url: str) -> dict:
    """Fetch repo metadata + README from GitHub API. Returns a dict with what was found."""
    result: dict = {"available": False}
    parsed = _parse_github_repo(github_url)
    if not parsed:
        return result

    owner, repo = parsed
    base = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        # repo metadata
        resp = await github_get(base, timeout=10.0)
        if resp.status_code != 200:
            return result
        data = resp.json()

        result["available"] = True
        result["name"] = data.get("name", "")
        result["description"] = data.get("description") or ""
        result["language"] = data.get("language") or ""
        result["topics"] = data.get("topics") or []
        result["stars"] = data.get("stargazers_count", 0)
        result["forks"] = data.get("forks_count", 0)
        result["open_issues"] = data.get("open_issues_count", 0)
        result["size_kb"] = data.get("size", 0)
        result["default_branch"] = data.get("default_branch", "main")
        result["is_empty"] = data.get("size", 0) == 0
        result["is_fork"] = data.get("fork", False)

        # README
        readme_resp = await github_get(f"{base}/readme", timeout=8.0)
        if readme_resp.status_code == 200:
            readme_data = readme_resp.json()
            encoded = readme_data.get("content", "")
            try:
                decoded = base64.b64decode(encoded).decode("utf-8", errors="replace")
                result["readme"] = decoded[:3000]
            except Exception:
                result["readme"] = ""
        else:
            result["readme"] = ""

        # Languages breakdown
        lang_resp = await github_get(f"{base}/languages", timeout=8.0)
        if lang_resp.status_code == 200:
            result["languages"] = list(lang_resp.json().keys())
        else:
            result["languages"] = [result["language"]] if result["language"] else []

        # Recent commits count (last 30)
        commits_resp = await github_get(
            f"{base}/commits",
            timeout=8.0,
            params={"per_page": 30},
        )
        if commits_resp.status_code == 200:
            result["recent_commits"] = len(commits_resp.json())
        else:
            result["recent_commits"] = 0

    except Exception as exc:
        logger.warning("project_evaluation.github_fetch_failed", url=github_url, error=str(exc))

    return result


def _build_github_block(ctx: dict, github_url: str) -> str:
    """Format the GitHub repo context for the LLM prompt."""
    if not ctx.get("available"):
        return f"- Lien fourni : {github_url} (depot inaccessible ou inexistant)"

    lines = [f"- Depot : {github_url}"]
    if ctx.get("description"):
        lines.append(f"- Description du depot : {ctx['description']}")
    if ctx.get("languages"):
        lines.append(f"- Langages detectes : {', '.join(ctx['languages'])}")
    if ctx.get("topics"):
        lines.append(f"- Topics/tags : {', '.join(ctx['topics'])}")
    lines.append(f"- Taille du depot : {ctx.get('size_kb', 0)} Ko")
    lines.append(f"- Commits recents (30 derniers) : {ctx.get('recent_commits', 0)}")
    if ctx.get("is_empty"):
        lines.append("- ATTENTION : depot vide (aucun fichier pousse)")
    if ctx.get("is_fork"):
        lines.append("- ATTENTION : ce depot est un fork (pas un travail original)")
    if ctx.get("readme"):
        readme_excerpt = ctx["readme"][:1500].strip()
        lines.append(f"- Contenu README (extrait) :\n{readme_excerpt}")
    return "\n".join(lines)


async def _evaluate_with_llm(
    *,
    project_title: str,
    project_description: str,
    skills_practiced: list[str],
    deliverables: list[str],
    github_url: str | None,
    user_description: str | None,
) -> tuple[int, str]:
    """Return (score 0-100, feedback text)."""

    if not github_url and not (user_description and len(user_description.strip()) >= 30):
        return 0, "Aucune preuve fournie. Ajoutez un lien GitHub ou une description de ce que vous avez realise."

    # Fetch real GitHub content when URL provided
    github_block = ""
    repo_ctx: dict = {}
    if github_url:
        repo_ctx = await _fetch_repo_context(github_url)
        github_block = "Contenu reel du depot GitHub :\n" + _build_github_block(repo_ctx, github_url)

    desc_block = ""
    if user_description:
        desc_block = f"Description de l'etudiant :\n{user_description.strip()}"

    proof_block = "\n\n".join(filter(None, [github_block, desc_block]))
    skills_str = ", ".join(skills_practiced) if skills_practiced else "non specifiees"
    deliverables_str = "\n".join(f"- {d}" for d in deliverables) if deliverables else "- non specifies"

    # Rejets immédiats avant le LLM
    if repo_ctx.get("available"):
        if repo_ctx.get("is_empty"):
            return 5, (
                "Depot GitHub vide : aucun fichier n'a ete pousse. "
                "Committez tout votre code, le README et les fichiers de configuration, puis resoumettez."
            )
        if repo_ctx.get("is_fork") and repo_ctx.get("recent_commits", 0) < 5:
            return 10, (
                "Ce depot est un fork sans contributions significatives (moins de 5 commits personnels). "
                "Soumettez votre propre depot avec votre code original."
            )
        if repo_ctx.get("size_kb", 0) < 10 and repo_ctx.get("recent_commits", 0) < 3:
            return 8, (
                "Le depot est quasi-vide (< 10 Ko, moins de 3 commits). "
                "Un projet serieux necessite un code complet, un README et plusieurs commits."
            )
        if not repo_ctx.get("readme"):
            return 20, (
                "Aucun README trouve dans le depot. "
                "Un README est obligatoire : il doit expliquer le projet, comment l'installer et l'utiliser."
            )

    prompt = f"""Tu es un jury technique qui evalue si un etudiant a vraiment realise un projet informatique.
Sois TRES STRICT. Il vaut mieux rejeter un travail insuffisant que valider un travail bacle.
Le seuil de validation est 75/100. En dessous, le projet est refuse et l'etudiant doit refaire.

=== PROJET ATTENDU ===
Titre : {project_title}
Description complete : {project_description}
Competences que l'etudiant devait pratiquer : {skills_str}
Livrables obligatoires :
{deliverables_str}

=== PREUVES SOUMISES ===
{proof_block}

=== GRILLE DE NOTATION STRICTE ===
Reponds UNIQUEMENT en JSON :
{{
  "score": <entier 0-100>,
  "feedback": "<3-4 phrases : points positifs, points manquants, ce qu'il faut faire pour ameliorer>"
}}

BARÈME (applique-le a la lettre) :
- 90-100 : README detaille, tous les livrables presents, langages/stack correspondent exactement,
           code organise en modules/fonctions, au moins 10 commits, description de l'etudiant precise.
- 75-89  : La majorite des livrables sont presents, langages coherents, README correct,
           code fonctionnel meme si perfectible, au moins 5 commits.
- 50-74  : Projet partiellement realise - certains livrables manquent, README minimal,
           ou stack differente de ce qui etait demande sans justification.
- 25-49  : Ebauche incomplete - moins de la moitie des livrables, README absent ou vide,
           ou code non fonctionnel apparent.
- 0-24   : Travail insuffisant - depot presque vide, aucun rapport avec le projet, ou description vague.

REGLES ABSOLUES :
- Si le README ne mentionne pas le sujet du projet → score ≤ 50
- Si les langages detectes ne correspondent pas aux competences attendues → score ≤ 60
- Si moins de 3 commits → score ≤ 30
- Si la description de l'etudiant est vague (moins de 2 lignes concretes) sans GitHub → score ≤ 40
- Ne jamais depasser 85 si un livrable obligatoire est manifestement absent
- Ne jamais arrondir vers le haut par pitie : un travail a 70 reste a 70."""

    if not settings.mistral_api_key or settings.mistral_api_key == "change-me":
        score = 55 if github_url and repo_ctx.get("available") else (30 if github_url else 10)
        feedback = "Evaluation LLM indisponible. Score prudent attribue - configurez MISTRAL_API_KEY pour une vraie evaluation."
        return score, feedback

    try:
        client = get_llm_client()
        completion = await client.chat.completions.create(
            model=settings.mistral_default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.15,
            max_tokens=350,
        )
        raw = completion.choices[0].message.content or "{}"
        match = re.search(r"\{.*\}", raw, re.S)
        if not match:
            raise ValueError("no json in response")
        data = json.loads(match.group())
        score = max(0, min(100, int(data.get("score", 0))))
        feedback = str(data.get("feedback", "")).strip() or "Evaluation terminee."
        return score, feedback
    except Exception as exc:
        logger.warning("project_evaluation.llm_failed", error=str(exc))
        # En cas de panne LLM : score très bas par défaut, refus prudent
        return 0, "Evaluation temporairement indisponible. Reessayez dans quelques minutes."


class ProjectEvaluationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def submit(
        self,
        *,
        user_id: int,
        project_title: str,
        career_slug: str | None,
        project_description: str,
        skills_practiced: list[str],
        deliverables: list[str],
        github_url: str | None,
        user_description: str | None,
    ) -> ProjectSubmission:
        if not github_url and not (user_description and len(user_description.strip()) >= 30):
            raise ValidationError(
                "Fournissez un lien GitHub ou une description d'au moins 30 caracteres expliquant ce que vous avez realise."
            )

        score, feedback = await _evaluate_with_llm(
            project_title=project_title,
            project_description=project_description,
            skills_practiced=skills_practiced,
            deliverables=deliverables,
            github_url=github_url,
            user_description=user_description,
        )

        status = "approved" if score >= APPROVAL_THRESHOLD else "rejected"

        submission = ProjectSubmission(
            user_id=user_id,
            project_title=project_title,
            career_slug=career_slug,
            github_url=github_url,
            description=user_description,
            status=status,
            evaluation_score=score,
            feedback=feedback,
        )
        self.db.add(submission)
        await self.db.flush()

        if status == "approved":
            existing = await self.db.scalar(
                select(UserProjectCompletion).where(
                    UserProjectCompletion.user_id == user_id,
                    UserProjectCompletion.project_title == project_title,
                )
            )
            if not existing:
                self.db.add(
                    UserProjectCompletion(
                        user_id=user_id,
                        project_title=project_title,
                        career_slug=career_slug,
                    )
                )

        await self.db.commit()
        await self.db.refresh(submission)
        logger.info(
            "project_submission.evaluated",
            user_id=user_id,
            title=project_title,
            score=score,
            status=status,
        )
        return submission

    async def get_submissions(self, user_id: int) -> list[ProjectSubmission]:
        rows = await self.db.scalars(
            select(ProjectSubmission)
            .where(ProjectSubmission.user_id == user_id)
            .order_by(ProjectSubmission.created_at.desc())
        )
        return list(rows.all())

    async def get_latest_for_project(
        self, user_id: int, project_title: str
    ) -> ProjectSubmission | None:
        return await self.db.scalar(
            select(ProjectSubmission)
            .where(
                ProjectSubmission.user_id == user_id,
                ProjectSubmission.project_title == project_title,
            )
            .order_by(ProjectSubmission.created_at.desc())
            .limit(1)
        )
