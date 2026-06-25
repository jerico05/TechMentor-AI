"""Extract project metadata from a URL (GitHub repo or generic web page)."""

from __future__ import annotations

import json
import re

import httpx

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.services.llm_client import get_llm_client
from app.utils.url_extract import fetch_page_text, normalize_url, parse_github_repo_url

logger = get_logger(__name__)


async def _fetch_github_repo(owner: str, repo: str) -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_api_token:
        headers["Authorization"] = f"Bearer {settings.github_api_token}"

    async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
        response = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
        if response.status_code == 404:
            raise ValidationError(f"Dépôt GitHub introuvable : {owner}/{repo}")
        response.raise_for_status()
        return response.json()


async def _extract_with_llm(url: str, page_text: str) -> dict:
    if not settings.mistral_api_key or settings.mistral_api_key == "change-me":
        title = url.rstrip("/").split("/")[-1] or "Projet"
        return {"title": title, "summary": page_text[:400] or None, "stack": []}

    prompt = f"""Analyse ce projet portfolio à partir de son URL et du texte extrait.
Réponds UNIQUEMENT en JSON valide :
{{
  "title": "titre court du projet",
  "summary": "2 phrases max sur l'objectif et les résultats",
  "stack": ["techno1", "techno2"]
}}

URL: {url}
Texte:
{page_text[:5000]}"""

    client = get_llm_client()
    completion = await client.chat.completions.create(
        model=settings.mistral_default_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600,
    )
    raw = completion.choices[0].message.content or "{}"
    match = re.search(r"\{.*\}", raw, re.S)
    data = json.loads(match.group() if match else raw)
    return {
        "title": str(data.get("title") or "Projet").strip()[:255],
        "summary": (str(data.get("summary")).strip()[:2000] if data.get("summary") else None),
        "stack": [str(s).strip() for s in (data.get("stack") or []) if str(s).strip()][:12],
    }


async def extract_project_from_url(url: str) -> dict:
    """Return title, summary, stack, source for a project URL."""
    normalized = normalize_url(url)
    gh = parse_github_repo_url(normalized)
    if gh:
        owner, repo = gh
        repo_data = await _fetch_github_repo(owner, repo)
        lang = repo_data.get("language")
        topics = repo_data.get("topics") or []
        stack = [t for t in ([lang] if lang else []) + topics if t]
        return {
            "url": normalized,
            "title": str(repo_data.get("name") or repo).strip()[:255],
            "summary": (str(repo_data.get("description") or "").strip()[:2000] or None),
            "stack": stack,
            "source": "github",
        }

    try:
        page_text = await fetch_page_text(normalized)
    except httpx.HTTPError as exc:
        raise ValidationError(f"Impossible d'accéder à cette URL : {exc}") from exc

    if len(page_text) < 40:
        raise ValidationError(
            "Contenu insuffisant sur cette page. Essayez un lien direct vers le projet "
            "(repo GitHub, demo, case study)."
        )

    parsed = await _extract_with_llm(normalized, page_text)
    return {
        "url": normalized,
        "title": parsed["title"],
        "summary": parsed["summary"],
        "stack": parsed["stack"],
        "source": "web",
    }
