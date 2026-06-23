"""Experience level (entry / intermediaire / senior) — distinct from skill-gap score."""

from __future__ import annotations

LEVEL_ENTRY = "entry"
LEVEL_INTERMEDIAIRE = "intermediaire"
LEVEL_SENIOR = "senior"

# Portfolio project count thresholds
PROJECTS_INTERMEDIAIRE_MIN = 8
PROJECTS_SENIOR_MIN = 15

LEGACY_LEVEL_MAP: dict[str, str] = {
    "debutant": LEVEL_ENTRY,
    "junior": LEVEL_ENTRY,
    "entry": LEVEL_ENTRY,
    "intermediaire": LEVEL_INTERMEDIAIRE,
    "intermediate": LEVEL_INTERMEDIAIRE,
    "mid": LEVEL_INTERMEDIAIRE,
    "avance": LEVEL_SENIOR,
    "advanced": LEVEL_SENIOR,
    "senior": LEVEL_SENIOR,
}

LEVEL_LABELS_FR: dict[str, str] = {
    LEVEL_ENTRY: "Entry level",
    LEVEL_INTERMEDIAIRE: "Intermédiaire",
    LEVEL_SENIOR: "Senior",
}

# Roadmap LLM instructions per experience level
ROADMAP_LEVEL_GUIDANCE: dict[str, str] = {
    LEVEL_ENTRY: """
Niveau ENTRY LEVEL (junior / début de parcours) :
- Mois 1-2 : fondamentaux solides, concepts de base, environnement de dev, petits exercices guidés.
- Pas de sujets avancés (architecture distribuée, MLOps prod, sécurité offensive) avant les bases.
- Actions concrètes et réalisables seul·e avec tutoriels ; 1 mini-projet simple par mois max.
- Vocabulaire pédagogique, rythme progressif, beaucoup de pratique sur les compétences manquantes listées.
""",
    LEVEL_INTERMEDIAIRE: """
Niveau INTERMÉDIAIRE :
- L'étudiant peut construire des projets seul·e ; privilégier approfondissement et bonnes pratiques.
- Projets portfolio de complexité moyenne, tests, documentation, déploiement simple.
- Équilibre entre consolidation des lacunes et montée en responsabilité technique.
""",
    LEVEL_SENIOR: """
Niveau SENIOR :
- Architecture, scalabilité, observabilité, revue de code, mentoring, décisions techniques.
- Projets à fort impact portfolio, open source ou produit viable.
- Moins de rappels basiques ; focus sur excellence et production-ready.
""",
}


def normalize_level(level: str | None) -> str:
    if not level:
        return LEVEL_ENTRY
    return LEGACY_LEVEL_MAP.get(level.lower(), LEVEL_ENTRY)


def level_label_fr(level: str | None) -> str:
    return LEVEL_LABELS_FR.get(normalize_level(level), level or "Entry level")


def level_to_project_difficulty(level: str | None) -> str:
    """Map experience level to project difficulty slug used in fallbacks."""
    mapping = {
        LEVEL_ENTRY: "debutant",
        LEVEL_INTERMEDIAIRE: "intermediaire",
        LEVEL_SENIOR: "avance",
    }
    return mapping[normalize_level(level)]


def compute_experience_level(*, projects_completed: int = 0) -> str:
    """Derive entry / intermediaire / senior from portfolio projects completed.

  - Entry level (junior) : moins de 8 projets
  - Intermédiaire : 8 à 14 projets
  - Senior : 15 projets ou plus

    Skill-gap score is intentionally NOT used here.
    """
    projects = max(0, projects_completed)

    if projects >= PROJECTS_SENIOR_MIN:
        return LEVEL_SENIOR
    if projects >= PROJECTS_INTERMEDIAIRE_MIN:
        return LEVEL_INTERMEDIAIRE
    return LEVEL_ENTRY


def experience_level_reason(
    *,
    level: str,
    projects_completed: int,
    academic_level: str | None = None,
) -> str:
    normalized = normalize_level(level)
    label = level_label_fr(normalized)
    _ = academic_level
    if projects_completed == 0:
        return (
            f"Niveau {label} (junior) : aucun projet portfolio validé. "
            f"Intermédiaire à partir de {PROJECTS_INTERMEDIAIRE_MIN} projets, "
            f"senior à partir de {PROJECTS_SENIOR_MIN}. "
            "Marquez vos projets réalisés sur la page Projets."
        )
    if projects_completed < PROJECTS_INTERMEDIAIRE_MIN:
        remaining = PROJECTS_INTERMEDIAIRE_MIN - projects_completed
        return (
            f"Niveau {label} (junior) : {projects_completed} projet(s) validé(s). "
            f"Encore {remaining} pour atteindre Intermédiaire ({PROJECTS_INTERMEDIAIRE_MIN}+)."
        )
    if projects_completed < PROJECTS_SENIOR_MIN:
        remaining = PROJECTS_SENIOR_MIN - projects_completed
        return (
            f"Niveau {label} : {projects_completed} projet(s) validé(s). "
            f"Encore {remaining} pour atteindre Senior ({PROJECTS_SENIOR_MIN}+)."
        )
    return (
        f"Niveau {label} : {projects_completed} projet(s) validé(s) "
        f"(seuil senior : {PROJECTS_SENIOR_MIN}+)."
    )
