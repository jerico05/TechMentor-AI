"""Tests for roadmap course catalog."""

from app.data.roadmap_course_catalog import format_catalog_for_prompt, pick_courses_for_month


def test_pick_courses_matches_python_skills():
    month = {"title": "Bases Python", "skills": ["Python", "algorithmique"], "actions": []}
    courses = pick_courses_for_month(month, "backend-developer", limit=2)
    assert len(courses) >= 1
    assert any("python" in c["url"].lower() or "freecodecamp" in c["url"].lower() for c in courses)


def test_format_catalog_for_prompt_lists_urls():
    text = format_catalog_for_prompt("data-scientist", ["Python", "Machine Learning"])
    assert "Sources verifiees" in text
    assert "https://" in text
