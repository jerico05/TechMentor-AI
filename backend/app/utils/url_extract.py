"""URL parsing and lightweight HTML text extraction."""

from __future__ import annotations

import html as html_module
import re

import httpx

from app.core.exceptions import ValidationError


def normalize_url(url: str) -> str:
    cleaned = url.strip()
    if not cleaned:
        raise ValidationError("URL requise.")
    if not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"
    return cleaned.rstrip("/")


def extract_linkedin_slug(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"linkedin\.com/in/([A-Za-z0-9_-]+)", url.strip(), re.I)
    return match.group(1) if match else None


def parse_github_repo_url(url: str) -> tuple[str, str] | None:
    match = re.search(r"github\.com/([A-Za-z0-9_-]+)/([^/?#]+)", url.strip(), re.I)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2)
    if repo.lower() in {"repos", "followers", "following"}:
        return None
    return owner, repo.removesuffix(".git")


def html_to_text(raw: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_module.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


async def fetch_page_text(url: str, *, max_chars: int = 12000) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; TechMentorBot/1.0; +https://tech-mentor-ai.vercel.app)"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return html_to_text(response.text)[:max_chars]
