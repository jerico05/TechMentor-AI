"""Tests for roadmap duration suggestion."""

from app.utils.roadmap_duration import suggest_roadmap_duration


def test_suggest_many_missing_always_twelve():
    assert suggest_roadmap_duration("senior", 10) == 12


def test_suggest_entry_long_path():
    assert suggest_roadmap_duration("entry", 7) == 12
    assert suggest_roadmap_duration("debutant", 3) == 6


def test_suggest_intermediaire():
    assert suggest_roadmap_duration("intermediaire", 5) == 6
    assert suggest_roadmap_duration("intermediaire", 2) == 3


def test_suggest_senior_short_path():
    assert suggest_roadmap_duration("senior", 2) == 3
    assert suggest_roadmap_duration("avance", 6) == 6
