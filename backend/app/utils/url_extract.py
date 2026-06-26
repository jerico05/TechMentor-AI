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
    match = re.search(r"linkedin\.com/in/([A-Za-z0-9_%\-]+)", url.strip(), re.I)
    if not match:
        return None
    slug = match.group(1).rstrip("/")
    return slug or None


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


_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; TechMentorBot/1.0; +https://tech-mentor-ai.vercel.app)"
    ),
    "Accept": "text/html,application/xhtml+xml",
}


async def fetch_page_html(url: str) -> str:
    async with httpx.AsyncClient(
        timeout=20.0, follow_redirects=True, headers=_DEFAULT_HEADERS
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def fetch_page_text(url: str, *, max_chars: int = 12000) -> str:
    html = await fetch_page_html(url)
    return html_to_text(html)[:max_chars]


def extract_hrefs(html: str, base_url: str) -> list[str]:
    """Collect absolute http(s) links from HTML."""
    from urllib.parse import urljoin, urlparse

    seen: set[str] = set()
    links: list[str] = []
    for match in re.finditer(r"""href=["']([^"'#]+)["']""", html, re.I):
        raw = match.group(1).strip()
        if not raw or raw.startswith(("mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(base_url, raw).split("#")[0].rstrip("/")
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue
        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)
    return links
