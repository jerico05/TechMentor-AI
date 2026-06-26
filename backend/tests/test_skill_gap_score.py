"""Tests for strict skill-gap scoring."""

from app.models.skill import Skill
from app.utils.skill_gap_score import SkillEvidence, compute_strict_skill_gap_score


def _required() -> dict[str, Skill]:
    return {
        "Python": Skill(name="Python", category="language", weight=25),
        "SQL": Skill(name="SQL", category="database", weight=20),
        "Docker": Skill(name="Docker", category="devops", weight=15),
        "Git": Skill(name="Git", category="tool", weight=10),
    }


def test_zero_when_no_validated_skills():
    score, owned, missing = compute_strict_skill_gap_score(_required(), {})
    assert score == 0
    assert owned == []
    assert len(missing) == 4


def test_linkedin_only_scores_lower_than_cv():
    required = _required()
    linkedin = {
        name: SkillEvidence(confidence=80, source="linkedin")
        for name in required
    }
    cv = {name: SkillEvidence(confidence=85, source="cv") for name in required}

    linkedin_score, _, _ = compute_strict_skill_gap_score(required, linkedin)
    cv_score, _, _ = compute_strict_skill_gap_score(required, cv)

    assert linkedin_score < cv_score
    assert linkedin_score <= 75


def test_partial_coverage_is_strict():
    required = _required()
    evidence = {
        "Python": SkillEvidence(confidence=85, source="cv"),
        "Git": SkillEvidence(confidence=85, source="cv"),
    }
    score, owned, missing = compute_strict_skill_gap_score(required, evidence)

    assert owned == ["Python", "Git"]
    assert "SQL" in missing
    assert score < 35


def test_low_confidence_skills_do_not_count():
    required = _required()
    evidence = {
        "Python": SkillEvidence(confidence=60, source="cv"),
        "SQL": SkillEvidence(confidence=85, source="cv"),
    }
    score, owned, missing = compute_strict_skill_gap_score(required, evidence)

    assert owned == ["SQL"]
    assert "Python" in missing
    assert score < 30
