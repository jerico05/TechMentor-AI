"""Tests for URL extraction helpers."""

from app.utils.url_extract import extract_linkedin_slug, parse_github_repo_url


def test_extract_linkedin_slug():
    assert extract_linkedin_slug("https://www.linkedin.com/in/jane-doe/") == "jane-doe"


def test_parse_github_repo_url():
    assert parse_github_repo_url("https://github.com/org/my-app") == ("org", "my-app")
