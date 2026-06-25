"""Fetch LinkedIn profile content via API, PDF, or HTML metadata."""

from __future__ import annotations

import json
import re

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.cv_parser import extract_text_from_bytes
from app.utils.url_extract import html_to_text, normalize_url

logger = get_logger(__name__)

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def _meta_content(html: str, key: str) -> str | None:
    patterns = [
        rf'<meta[^>]+(?:property|name)="{re.escape(key)}"[^>]+content="([^"]*)"',
        rf'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="{re.escape(key)}"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match and match.group(1).strip():
            return match.group(1).strip()
    return None


def _json_ld_person_text(html: str) -> str:
    chunks: list[str] = []
    for block in re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.I | re.S):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("@type") not in ("Person", "ProfilePage"):
                continue
            for field in ("name", "jobTitle", "description", "worksFor"):
                value = item.get(field)
                if isinstance(value, str):
                    chunks.append(value)
                elif isinstance(value, dict) and value.get("name"):
                    chunks.append(str(value["name"]))
    return "\n".join(chunks)


def extract_linkedin_html_text(html: str) -> str:
    """Combine Open Graph metadata and visible text from a LinkedIn HTML response."""
    parts: list[str] = []
    for key in ("og:title", "og:description", "description", "twitter:title", "twitter:description"):
        if value := _meta_content(html, key):
            if value.lower() not in {p.lower() for p in parts}:
                parts.append(value)

    ld_text = _json_ld_person_text(html)
    if ld_text:
        parts.append(ld_text)

    body_text = html_to_text(html)
    if body_text:
        parts.append(body_text)

    combined = "\n".join(parts)
    combined = re.sub(r"\n{3,}", "\n\n", combined)
    return combined.strip()


def _format_proxycurl_date(value: dict | None) -> str:
    if not value or not isinstance(value, dict):
        return ""
    parts = [str(value.get("month") or ""), str(value.get("year") or "")]
    return "/".join(p for p in parts if p and p != "None")


def _map_proxycurl_payload(data: dict, profile_url: str) -> dict:
    experiences = []
    for exp in data.get("experiences") or []:
        if not isinstance(exp, dict):
            continue
        start = _format_proxycurl_date(exp.get("starts_at"))
        end = _format_proxycurl_date(exp.get("ends_at")) or "présent"
        duration = f"{start} - {end}".strip(" -") if start or end != "présent" else ""
        experiences.append(
            {
                "title": str(exp.get("title") or "").strip(),
                "company": str(exp.get("company") or "").strip(),
                "duration": duration,
                "description": str(exp.get("description") or "").strip()[:500],
            }
        )

    education = []
    for edu in data.get("education") or []:
        if not isinstance(edu, dict):
            continue
        education.append(
            {
                "school": str(edu.get("school") or "").strip(),
                "degree": str(edu.get("degree_name") or edu.get("field_of_study") or "").strip(),
                "duration": _format_proxycurl_date(edu.get("starts_at")),
            }
        )

    skills = [str(s).strip() for s in (data.get("skills") or []) if str(s).strip()][:30]
    headline = str(data.get("headline") or "").strip() or None
    summary = str(data.get("summary") or "").strip() or None
    if not summary and headline:
        summary = headline

    raw_bits = [headline, summary]
    for exp in experiences[:6]:
        raw_bits.append(f"{exp.get('title')} @ {exp.get('company')} ({exp.get('duration')})")
    raw_text = "\n".join(filter(None, raw_bits))[:4000]

    return {
        "profile_url": profile_url,
        "headline": headline[:500] if headline else None,
        "summary": summary[:2000] if summary else None,
        "experiences": experiences[:12],
        "education": education[:8],
        "skills": skills,
        "raw_text": raw_text,
        "source": "proxycurl",
    }


async def fetch_via_proxycurl(profile_url: str) -> dict | None:
    api_key = settings.proxycurl_api_key
    if not api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=35.0) as client:
            response = await client.get(
                "https://nubela.co/proxycurl/api/v2/linkedin",
                params={"linkedin_profile_url": profile_url, "use_cache": "if-present"},
                headers={"Authorization": f"Bearer {api_key}"},
            )
        if response.status_code == 404:
            return None
        if response.status_code == 401:
            logger.warning("linkedin.proxycurl.unauthorized")
            return None
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return None
        mapped = _map_proxycurl_payload(payload, profile_url)
        if mapped.get("experiences") or mapped.get("summary") or mapped.get("skills"):
            logger.info("linkedin.proxycurl.ok", url=profile_url)
            return mapped
    except Exception as exc:
        logger.warning("linkedin.proxycurl.failed", error=str(exc))
    return None


async def fetch_linkedin_html(profile_url: str) -> str:
    async with httpx.AsyncClient(timeout=22.0, follow_redirects=True, headers=_BROWSER_HEADERS) as client:
        response = await client.get(profile_url)
        response.raise_for_status()
        return response.text


def extract_text_from_linkedin_pdf(pdf_bytes: bytes) -> str:
    text = extract_text_from_bytes(pdf_bytes, "application/pdf", suffix=".pdf")
    if len(text.strip()) < 80:
        raise ValueError("Le PDF LinkedIn ne contient pas assez de texte lisible.")
    return text
