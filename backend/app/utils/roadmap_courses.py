"""Sanitize LLM-generated roadmap course recommendations."""

from __future__ import annotations

import re

ALLOWED_COURSE_TYPES = frozenset({"gratuit", "payant", "freemium"})
MAX_COURSES_PER_MONTH = 2


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
