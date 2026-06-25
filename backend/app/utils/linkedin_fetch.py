"""Fetch LinkedIn profile content from PDF or public HTML metadata."""

from __future__ import annotations

import json
import re

import httpx

from app.utils.cv_parser import extract_text_from_bytes
from app.utils.url_extract import html_to_text

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
