"""Tests for roadmap course sanitization."""

from unittest.mock import AsyncMock, patch

import pytest

from app.utils.roadmap_courses import sanitize_roadmap_courses, validate_and_enrich_roadmap_courses


@pytest.mark.asyncio
async def test_validate_replaces_broken_urls_with_catalog():
    content = {
        "months": [
            {
                "month": 1,
                "title": "Python",
                "skills": ["Python"],
                "courses": [
                    {
                        "title": "Fake course",
                        "platform": "Web",
                        "url": "https://example.invalid/fake-course-404",
                        "type": "gratuit",
                        "note": "test",
                    }
                ],
            }
        ]
    }
    with patch(
        "app.utils.roadmap_courses._is_url_reachable",
        new_callable=AsyncMock,
    ) as mock_reach:
        mock_reach.side_effect = lambda _client, url: "docs.python.org" in url
        result = await validate_and_enrich_roadmap_courses(content, "backend-developer")

    courses = result["months"][0]["courses"]
    assert len(courses) >= 1
    assert all("docs.python.org" in c["url"] or "freecodecamp" in c["url"] for c in courses)


def test_sanitize_keeps_valid_courses_max_two():
    content = {
        "months": [
            {
                "month": 1,
                "title": "Python",
                "courses": [
                    {
                        "title": "Python for Everybody",
                        "platform": "Coursera",
                        "url": "https://www.coursera.org/specializations/python",
                        "type": "freemium",
                        "note": "Bases solides",
                    },
                    {
                        "title": "Extra",
                        "platform": "Udemy",
                        "url": "https://www.udemy.com/course/example",
                        "type": "payant",
                    },
                    {
                        "title": "Third",
                        "platform": "Web",
                        "url": "https://example.com/c",
                        "type": "gratuit",
                    },
                ],
            }
        ]
    }
    result = sanitize_roadmap_courses(content)
    assert len(result["months"][0]["courses"]) == 2


def test_sanitize_drops_invalid_urls():
    content = {
        "months": [
            {
                "month": 1,
                "courses": [
                    {"title": "Bad", "platform": "X", "url": "not-a-url", "type": "gratuit"},
                    {
                        "title": "Good",
                        "platform": "freeCodeCamp",
                        "url": "https://www.freecodecamp.org/learn",
                        "type": "gratuit",
                    },
                ],
            }
        ]
    }
    result = sanitize_roadmap_courses(content)
    assert len(result["months"][0]["courses"]) == 1
    assert result["months"][0]["courses"][0]["platform"] == "freeCodeCamp"
