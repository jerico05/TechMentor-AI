"""Strict skill-gap score for career readiness analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class WeightedSkill(Protocol):
    weight: int

MIN_CONFIDENCE = 70
MIN_CREDIBILITY = 0.55
CRITICAL_SKILL_WEIGHT = 20
STRICT_EXPONENT = 1.45

SOURCE_MULTIPLIERS: dict[str, float] = {
    "cv": 1.0,
    "manual": 0.95,
    "github": 0.85,
    "linkedin": 0.70,
}

DEFAULT_SOURCE_MULTIPLIER = 0.65


@dataclass(frozen=True)
class SkillEvidence:
    confidence: int
    source: str


def skill_credibility(*, confidence: int, source: str) -> float:
    multiplier = SOURCE_MULTIPLIERS.get(source.lower(), DEFAULT_SOURCE_MULTIPLIER)
    return max(0.0, min(1.0, confidence / 100 * multiplier))


def _skill_is_validated(evidence: SkillEvidence | None) -> bool:
    if evidence is None:
        return False
    if evidence.confidence < MIN_CONFIDENCE:
        return False
    return skill_credibility(confidence=evidence.confidence, source=evidence.source) >= MIN_CREDIBILITY


def compute_strict_skill_gap_score(
    required: dict[str, WeightedSkill],
    evidence_by_skill: dict[str, SkillEvidence],
) -> tuple[int, list[str], list[str]]:
    """Return strict score (0-100), validated owned skills, missing skills."""
    if not required:
        return 0, [], []

    total_weight = sum(skill.weight for skill in required.values()) or 1
    validated_owned: list[str] = []
    earned = 0.0

    for name, skill in required.items():
        evidence = evidence_by_skill.get(name)
        if not _skill_is_validated(evidence):
            continue
        cred = skill_credibility(confidence=evidence.confidence, source=evidence.source)
        validated_owned.append(name)
        earned += skill.weight * cred

    missing = [name for name in required if name not in validated_owned]
    weighted_ratio = earned / total_weight
    coverage_ratio = len(validated_owned) / len(required)
    raw = weighted_ratio * 0.45 + coverage_ratio * 0.55

    critical_missing = sum(
        1 for name in missing if required[name].weight >= CRITICAL_SKILL_WEIGHT
    )
    if critical_missing:
        raw *= max(0.35, 1 - 0.1 * critical_missing)

    score = round(min(100, 100 * (max(0.0, raw) ** STRICT_EXPONENT)))
    return score, validated_owned, missing
