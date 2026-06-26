"""Discover project links from a portfolio website."""

from __future__ import annotations

import json
import re
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.services.llm_client import get_llm_client
from app.utils.url_extract import (
    extract_hrefs,
    fetch_page_html,
    html_to_text,
    normalize_url,
    parse_github_repo_url,
)

logger = get_logger(__name__)

_SKIP_DOMAINS = {
    "linkedin.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "tiktok.com",
    "medium.com",
}
_SKIP_PATH_PARTS = (
    "/login",
    "/signin",
    "/signup",
    "/register",
    "/contact",
    "/about",
    "/blog",
    "/privacy",
    "/terms",
    "/cv",
    "/resume",
    "/mentions",
)
_COMMON_PROJECT_PATHS = ("/projects", "/portfolio", "/work", "/projets", "/realisations")


def _host(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def _is_skipped_domain(url: str) -> bool:
    host = _host(url)
    return any(host == domain or host.endswith(f".{domain}") for domain in _SKIP_DOMAINS)


def _is_likely_project_url(url: str, portfolio_host: str) -> bool:
    if _is_skipped_domain(url):
        return False
    lowered = url.lower()
    if any(part in lowered for part in _SKIP_PATH_PARTS):
        return False

    if parse_github_repo_url(url):
        return True

    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.strip("/")

    if host.endswith("github.io") and path:
        return True
    if host.endswith("vercel.app") and path and host != portfolio_host:
        return True
    if host.endswith("netlify.app") and path and host != portfolio_host:
        return True

    if host == portfolio_host and path:
        segments = [s for s in path.split("/") if s]
        if len(segments) >= 1 and segments[0].lower() in {
            "project",
            "projects",
            "portfolio",
            "work",
            "projets",
            "case-study",
            "case-studies",
        }:
            return len(segments) >= 2 or len(path) > 12
        if len(segments) == 1 and len(segments[0]) > 3:
            return segments[0].lower() not in {"home", "index", "about", "contact", "blog"}
    return False


async def _llm_rank_project_urls(
    portfolio_url: str,
    candidates: list[str],
    page_text: str,
    *,
    max_urls: int,
) -> list[str]:
    if not settings.mistral_api_key or settings.mistral_api_key == "change-me":
        return candidates[:max_urls]

    prompt = f"""Tu analyses un site portfolio. Sélectionne uniquement les URLs qui pointent vers des projets réalisés
(dépôts GitHub, demos, case studies), pas la navigation du site.

Réponds UNIQUEMENT avec un JSON array de strings, max {max_urls} URLs, dans l'ordre de pertinence.
Si aucun lien projet, réponds [].

Site: {portfolio_url}
Liens candidats:
{json.dumps(candidates[:40], ensure_ascii=False)}

Extrait page:
{page_text[:3500]}"""

    try:
        client = get_llm_client()
        completion = await client.chat.completions.create(
            model=settings.mistral_default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=800,
        )
        raw = completion.choices[0].message.content or "[]"
        match = re.search(r"\[.*\]", raw, re.S)
        if not match:
            return candidates[:max_urls]
        picked = json.loads(match.group())
        valid = {c.rstrip("/") for c in candidates}
        ordered: list[str] = []
        for item in picked:
            if not isinstance(item, str):
                continue
            normalized = item.strip().rstrip("/")
            if normalized in valid and normalized not in ordered:
                ordered.append(normalized)
        if ordered:
            return ordered[:max_urls]
    except Exception as exc:
        logger.warning("portfolio.llm_rank.failed", error=str(exc))

    return candidates[:max_urls]


async def discover_project_urls(portfolio_url: str, *, max_urls: int = 10) -> list[str]:
    """Return project-like URLs found on a portfolio site."""
    normalized = normalize_url(portfolio_url)
    portfolio_host = _host(normalized)

    pages_to_scan = [normalized]
    for suffix in _COMMON_PROJECT_PATHS:
        pages_to_scan.append(f"{normalized}{suffix}")

    discovered: set[str] = set()
    combined_text_parts: list[str] = []

    for page_url in pages_to_scan:
        try:
            html = await fetch_page_html(page_url)
        except httpx.HTTPError:
            continue

        combined_text_parts.append(html_to_text(html)[:4000])
        for link in extract_hrefs(html, page_url):
            if link.rstrip("/") == normalized.rstrip("/"):
                continue
            if _is_likely_project_url(link, portfolio_host):
                discovered.add(link.rstrip("/"))

    if not discovered:
        raise ValidationError(
            "Aucun projet détecté sur ce site. Ajoutez les liens GitHub ou demo manuellement "
            "dans la section « Lien du projet »."
        )

    candidates = sorted(discovered)
    page_text = "\n".join(combined_text_parts)
    if len(candidates) > max_urls:
        candidates = await _llm_rank_project_urls(
            normalized, candidates, page_text, max_urls=max_urls
        )
    else:
        candidates = await _llm_rank_project_urls(
            normalized, candidates, page_text, max_urls=len(candidates)
        )

    logger.info(
        "portfolio.site.discovered",
        portfolio_url=normalized,
        count=len(candidates),
    )
    return candidates[:max_urls]
