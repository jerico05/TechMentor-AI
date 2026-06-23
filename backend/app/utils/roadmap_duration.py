"""Roadmap duration helpers (3 / 6 / 12 months)."""

from __future__ import annotations

from app.utils.user_level import LEVEL_ENTRY, LEVEL_INTERMEDIAIRE, LEVEL_SENIOR, normalize_level, level_label_fr

ALLOWED_ROADMAP_MONTHS = (3, 6, 12)


def suggest_roadmap_duration(level: str, missing_count: int) -> int:
    """Suggest 3, 6, or 12 months from experience level and skill gap."""
    if missing_count >= 10:
        return 12
    normalized = normalize_level(level)
    if normalized == LEVEL_ENTRY:
        return 12 if missing_count >= 4 else 6
    if normalized == LEVEL_INTERMEDIAIRE:
        return 6 if missing_count >= 4 else 3
    # senior — shorter if few gaps, longer if many
    return 6 if missing_count >= 5 else 3


def normalize_roadmap_duration(months: int | None, level: str, missing_count: int) -> int:
    if months in ALLOWED_ROADMAP_MONTHS:
        return months
    return suggest_roadmap_duration(level, missing_count)


def suggestion_reason(level: str, missing_count: int, months: int) -> str:
    label = level_label_fr(level)
    if missing_count >= 10:
        return f"{missing_count} compétences à acquérir : un parcours de {months} mois est recommandé."
    return (
        f"Niveau d'expérience {label}, {missing_count} compétence{'s' if missing_count != 1 else ''} "
        f"à acquérir pour le métier cible — parcours de {months} mois."
    )
