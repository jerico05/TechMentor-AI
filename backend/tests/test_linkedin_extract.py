"""Tests for LinkedIn placeholder cleanup."""

from app.utils.linkedin_extract import _clean_linkedin_field, _normalize_certification


def test_clean_linkedin_field_removes_french_placeholder():
    assert _clean_linkedin_field("Pas d'information disponible") is None
    assert _clean_linkedin_field("  No information available  ") is None


def test_clean_linkedin_field_keeps_real_values():
    assert _clean_linkedin_field("Coursera") == "Coursera"
    assert _clean_linkedin_field("juin 2024") == "juin 2024"


def test_normalize_certification_strips_placeholder_metadata():
    cert = _normalize_certification(
        {
            "name": "Statistics",
            "issuer": "Pas d'information disponible",
            "date": "Pas d'information disponible",
        }
    )
    assert cert == {"name": "Statistics", "issuer": None, "date": None}


def test_normalize_certification_strips_placeholder_from_name():
    cert = _normalize_certification(
        {
            "name": "Statistics · Pas d'information disponible",
            "issuer": "Coursera",
            "date": None,
        }
    )
    assert cert == {"name": "Statistics", "issuer": "Coursera", "date": None}
