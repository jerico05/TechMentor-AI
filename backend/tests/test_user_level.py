"""Tests for experience level computation."""

from app.utils.user_level import (
    PROJECTS_INTERMEDIAIRE_MIN,
    PROJECTS_SENIOR_MIN,
    compute_experience_level,
    normalize_level,
)


def test_entry_below_three_projects():
    assert compute_experience_level(projects_completed=0) == "entry"
    assert compute_experience_level(projects_completed=2) == "entry"


def test_intermediaire_from_three_projects():
    assert compute_experience_level(projects_completed=PROJECTS_INTERMEDIAIRE_MIN) == "intermediaire"
    assert compute_experience_level(projects_completed=7) == "intermediaire"


def test_senior_from_eight_projects():
    assert compute_experience_level(projects_completed=PROJECTS_SENIOR_MIN) == "senior"
    assert compute_experience_level(projects_completed=20) == "senior"


def test_legacy_level_normalized():
    assert normalize_level("debutant") == "entry"
    assert normalize_level("avance") == "senior"
