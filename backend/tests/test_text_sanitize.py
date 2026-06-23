"""Tests for plain-text sanitization of mentor replies."""

from app.utils.text_sanitize import sanitize_mentor_reply


def test_sanitize_removes_bold_and_headings() -> None:
    raw = "## Titre\n1. **Compréhension** : stats et algèbre."
    assert sanitize_mentor_reply(raw) == "Titre\n1. Compréhension : stats et algèbre."


def test_sanitize_removes_stray_markers() -> None:
    assert sanitize_mentor_reply("**Point** et *italique*") == "Point et italique"
