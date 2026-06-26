"""Tests for portfolio site link discovery."""

from app.utils.portfolio_site_extract import _is_likely_project_url
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


def test_extract_linkedin_slug_supports_encoded_chars():
    assert extract_linkedin_slug("https://fr.linkedin.com/in/jean-dupont_123/") == "jean-dupont_123"
