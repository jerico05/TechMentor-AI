"""Tests for LinkedIn HTML metadata extraction."""

from app.utils.linkedin_fetch import extract_linkedin_html_text


def test_extract_linkedin_html_text_from_og_tags():
    html = """
    <html><head>
    <meta property="og:title" content="Jane Doe | LinkedIn" />
    <meta property="og:description" content="Data Scientist chez Acme | Python, ML" />
    </head><body>Join LinkedIn</body></html>
    """
    text = extract_linkedin_html_text(html)
    assert "Jane Doe" in text
    assert "Data Scientist" in text
    assert len(text) >= 40
