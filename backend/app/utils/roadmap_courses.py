"""Sanitize and validate LLM-generated roadmap course recommendations."""

from __future__ import annotations

import asyncio
import re

import httpx

from app.core.logging import get_logger
from app.data.roadmap_course_catalog import pick_courses_for_month

logger = get_logger(__name__)

ALLOWED_COURSE_TYPES = frozenset({"gratuit", "payant", "freemium"})
MAX_COURSES_PER_MONTH = 2
URL_CHECK_TIMEOUT = 8.0
USER_AGENT = "TechMentorAI/1.0 (roadmap link checker)"


def _normalize_course_type(raw: str | None) -> str:
    if not raw:
        return "freemium"
    value = raw.strip().lower()
    if value in ALLOWED_COURSE_TYPES:
        return value
    if "gratuit" in value or "free" in value:
        return "gratuit"
    if "payant" in value or "paid" in value:
        return "payant"
    return "freemium"


def _is_plausible_url(url: str) -> bool:
    return bool(re.match(r"^https?://[^\s]+$", url, re.I))


async def _is_url_reachable(client: httpx.AsyncClient, url: str) -> bool:
    headers = {"User-Agent": USER_AGENT}
    try:
        response = await client.head(url, headers=headers, follow_redirects=True)
        if response.status_code < 400:
            return True
        if response.status_code in {405, 403, 501}:
            response = await client.get(url, headers=headers, follow_redirects=True)
            return response.status_code < 400
        return False
    except Exception:
        try:
            response = await client.get(url, headers=headers, follow_redirects=True)
            return response.status_code < 400
        except Exception:
            return False


def sanitize_roadmap_courses(content: dict) -> dict:
    """Keep at most 2 valid courses per month with required fields."""
    months = content.get("months")
    if not isinstance(months, list):
        return content

    for month in months:
        if not isinstance(month, dict):
            continue
        raw_courses = month.get("courses")
        if not isinstance(raw_courses, list):
            month["courses"] = []
            continue

        cleaned: list[dict] = []
        for item in raw_courses:
            if len(cleaned) >= MAX_COURSES_PER_MONTH:
                break
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            url = str(item.get("url") or "").strip()
            platform = str(item.get("platform") or "Web").strip()
            if not title or not _is_plausible_url(url):
                continue
            cleaned.append(
                {
                    "title": title[:200],
                    "platform": platform[:80],
                    "url": url[:500],
                    "type": _normalize_course_type(item.get("type")),
                    "note": str(item.get("note") or "").strip()[:160],
                }
            )
        month["courses"] = cleaned

    content["months"] = months
    return content


async def validate_and_enrich_roadmap_courses(
    content: dict,
    career_slug: str,
) -> dict:
    """
    Verifie les URLs proposees par le LLM et complete avec le catalogue si besoin.
    """
    months = content.get("months")
    if not isinstance(months, list):
        return content

    used_urls: set[str] = set()
    async with httpx.AsyncClient(timeout=URL_CHECK_TIMEOUT, follow_redirects=True) as client:
        for month in months:
            if not isinstance(month, dict):
                continue

            verified: list[dict] = []
            for course in month.get("courses") or []:
                if not isinstance(course, dict):
                    continue
                url = str(course.get("url") or "").strip()
                if not url or url in used_urls:
                    continue
                if await _is_url_reachable(client, url):
                    verified.append(course)
                    used_urls.add(url)
                    logger.info("roadmap.course.url_ok", url=url[:120])
                else:
                    logger.warning("roadmap.course.url_rejected", url=url[:120])

            if len(verified) < MAX_COURSES_PER_MONTH:
                needed = MAX_COURSES_PER_MONTH - len(verified)
                fallbacks = pick_courses_for_month(
                    month,
                    career_slug,
                    limit=needed,
                    exclude_urls=used_urls,
                )
                for fb in fallbacks:
                    url = fb["url"]
                    if url in used_urls:
                        continue
                    if await _is_url_reachable(client, url):
                        verified.append(fb)
                        used_urls.add(url)
                    if len(verified) >= MAX_COURSES_PER_MONTH:
                        break

            month["courses"] = verified[:MAX_COURSES_PER_MONTH]

    content["months"] = months
    return content


def validate_and_enrich_roadmap_courses_sync(content: dict, career_slug: str) -> dict:
    return asyncio.run(validate_and_enrich_roadmap_courses(content, career_slug))
