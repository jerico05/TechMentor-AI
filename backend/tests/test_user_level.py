"""Tests for experience level computation."""

from app.utils.linkedin_experience import compute_total_experience_years
from app.utils.user_level import (
    PROJECTS_INTERMEDIAIRE_MIN,
    PROJECTS_SENIOR_MIN,
    YEARS_INTERMEDIAIRE_MIN,
    YEARS_SENIOR_MIN,
    compute_experience_level,
    normalize_level,
)


def test_entry_below_five_projects_without_linkedin():
    assert compute_experience_level(projects_completed=0) == "entry"
    assert compute_experience_level(projects_completed=4) == "entry"


def test_intermediaire_from_five_projects():
    assert compute_experience_level(projects_completed=PROJECTS_INTERMEDIAIRE_MIN) == "intermediaire"
    assert compute_experience_level(projects_completed=9) == "intermediaire"


def test_senior_from_ten_projects():
    assert compute_experience_level(projects_completed=PROJECTS_SENIOR_MIN) == "senior"
    assert compute_experience_level(projects_completed=20) == "senior"


def test_level_from_linkedin_years():
    assert compute_experience_level(projects_completed=0, experience_years=0.5) == "entry"
    assert compute_experience_level(projects_completed=0, experience_years=YEARS_INTERMEDIAIRE_MIN) == "intermediaire"
    assert compute_experience_level(projects_completed=0, experience_years=YEARS_SENIOR_MIN) == "senior"


def test_level_uses_higher_signal():
    assert compute_experience_level(projects_completed=2, experience_years=6) == "senior"
    assert compute_experience_level(projects_completed=12, experience_years=1) == "senior"


def test_legacy_level_normalized():
    assert normalize_level("debutant") == "entry"
    assert normalize_level("avance") == "senior"


def test_compute_total_experience_years_merges_overlaps():
    experiences = [
        {"duration": "Jan 2020 - Dec 2021"},
        {"duration": "Jun 2021 - Present"},
    ]
    total = compute_total_experience_years(experiences)
    assert total >= 5.0


def test_compute_total_experience_years_french_dates():
    experiences = [{"duration": "janv. 2022 - déc. 2023"}]
    total = compute_total_experience_years(experiences)
    assert 1.9 <= total <= 2.1
