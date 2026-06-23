"""Tests for roadmap course sanitization."""

from app.utils.roadmap_courses import sanitize_roadmap_courses


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
