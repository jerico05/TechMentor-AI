"""Tests for portfolio site link discovery."""

from unittest.mock import AsyncMock, patch

import pytest

from app.utils.portfolio_site_extract import (
    _discover_urls_in_spa_bundles,
    _is_likely_project_url,
    discover_project_urls,
)
from app.utils.url_extract import extract_hrefs, extract_linkedin_slug


def test_extract_hrefs_resolves_relative_links():
    html = """
    <html><body>
      <a href="/projects/my-app">App</a>
      <a href="https://github.com/jane/demo">GitHub</a>
    </body></html>
    """
    links = extract_hrefs(html, "https://portfolio.dev")
    assert "https://portfolio.dev/projects/my-app" in links
    assert "https://github.com/jane/demo" in links


def test_is_likely_project_url_github():
    assert _is_likely_project_url("https://github.com/jane/demo", "portfolio.dev")
    assert _is_likely_project_url("https://portfolio.dev/projects/my-app", "portfolio.dev")


def test_is_likely_project_url_external_vercel_demo():
    assert _is_likely_project_url("https://pitch-ia.vercel.app", "tresoralade.vercel.app")


def test_extract_linkedin_slug_supports_encoded_chars():
    assert extract_linkedin_slug("https://fr.linkedin.com/in/jean-dupont_123/") == "jean-dupont_123"


@pytest.mark.asyncio
async def test_discover_urls_in_spa_bundles():
    html = """
    <html><head>
      <script type="module" src="/assets/index-abc.js"></script>
    </head><body><div id="root"></div></body></html>
    """
    bundle = 'const x="https://github.com/jane/demo";\nconst y="https://demo-app.vercel.app";'

    with patch(
        "app.utils.portfolio_site_extract.fetch_page_html",
        new=AsyncMock(return_value=bundle),
    ):
        urls = await _discover_urls_in_spa_bundles(html, "https://portfolio.dev", "portfolio.dev")

    assert "https://github.com/jane/demo" in urls
    assert "https://demo-app.vercel.app" in urls


@pytest.mark.asyncio
async def test_discover_project_urls_uses_spa_fallback():
    spa_html = '<html><script src="/assets/app.js"></script><body><div id="root"></div></body></html>'
    bundle = "https://github.com/jane/awesome-project"

    async def fake_fetch(url: str) -> str:
        if url.endswith("app.js"):
            return bundle
        return spa_html

    with patch("app.utils.portfolio_site_extract.fetch_page_html", side_effect=fake_fetch):
        urls = await discover_project_urls("https://portfolio.dev")

    assert "https://github.com/jane/awesome-project" in urls
