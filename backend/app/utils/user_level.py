"""Experience level (entry / intermediaire / senior) - distinct from skill-gap score."""

from __future__ import annotations

LEVEL_ENTRY = "entry"
LEVEL_INTERMEDIAIRE = "intermediaire"
LEVEL_SENIOR = "senior"

# Criteria from professional level table
YEARS_INTERMEDIAIRE_MIN = 2.0
YEARS_SENIOR_MIN = 5.0
PROJECTS_INTERMEDIAIRE_MIN = 5
PROJECTS_SENIOR_MIN = 10

LEVEL_ORDER = {
    LEVEL_ENTRY: 0,
    LEVEL_INTERMEDIAIRE: 1,
    LEVEL_SENIOR: 2,
}

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
    LEVEL_ENTRY: "Débutant (Junior)",
    LEVEL_INTERMEDIAIRE: "Intermédiaire",
    LEVEL_SENIOR: "Senior",
}

# Roadmap LLM instructions per experience level
ROADMAP_LEVEL_GUIDANCE: dict[str, str] = {
    LEVEL_ENTRY: """
Niveau DEBUTANT (junior / 0 a 2 ans d'experience) :
- Mois 1-2 : fondamentaux solides, concepts de base, environnement de dev, petits exercices guides.
- Pas de sujets avances (architecture distribuee, MLOps prod, securite offensive) avant les bases.
- Actions concretes et realisables seul·e avec tutoriels ; 1 mini-projet simple par mois max.
- Vocabulaire pedagogique, rythme progressif, beaucoup de pratique sur les competences manquantes listees.
""",
    LEVEL_INTERMEDIAIRE: """
Niveau INTERMEDIAIRE (2 a 5 ans d'experience) :
- L'etudiant peut construire des projets seul·e ; privilegier approfondissement et bonnes pratiques.
- Projets portfolio de complexite moyenne, tests, documentation, deploiement simple.
- Equilibre entre consolidation des lacunes et montee en responsabilite technique.
""",
    LEVEL_SENIOR: """
Niveau SENIOR (5+ ans d'experience) :
- Architecture, scalabilite, observabilite, revue de code, mentoring, decisions techniques.
- Projets a fort impact portfolio, open source ou produit viable.
- Moins de rappels basiques ; focus sur excellence et production-ready.
""",
}


def normalize_level(level: str | None) -> str:
    if not level:
        return LEVEL_ENTRY
    return LEGACY_LEVEL_MAP.get(level.lower(), LEVEL_ENTRY)


def level_label_fr(level: str | None) -> str:
    return LEVEL_LABELS_FR.get(normalize_level(level), level or "Débutant (Junior)")


def level_to_project_difficulty(level: str | None) -> str:
    """Map experience level to project difficulty slug used in fallbacks."""
    mapping = {
        LEVEL_ENTRY: "debutant",
        LEVEL_INTERMEDIAIRE: "intermediaire",
        LEVEL_SENIOR: "avance",
    }
    return mapping[normalize_level(level)]


def _level_from_years(years: float) -> str:
    if years >= YEARS_SENIOR_MIN:
        return LEVEL_SENIOR
    if years >= YEARS_INTERMEDIAIRE_MIN:
        return LEVEL_INTERMEDIAIRE
    return LEVEL_ENTRY


def _level_from_projects(projects_completed: int) -> str:
    projects = max(0, projects_completed)
    if projects >= PROJECTS_SENIOR_MIN:
        return LEVEL_SENIOR
    if projects >= PROJECTS_INTERMEDIAIRE_MIN:
        return LEVEL_INTERMEDIAIRE
    return LEVEL_ENTRY


def _max_level(*levels: str) -> str:
    return max(levels, key=lambda slug: LEVEL_ORDER[normalize_level(slug)])


def compute_experience_level(
    *,
    projects_completed: int = 0,
    experience_years: float | None = None,
) -> str:
    """Derive entry / intermediaire / senior from LinkedIn years and portfolio projects.

    Table criteria:
    - Debutant : 0-2 ans, 1-5 projets
    - Intermediaire : 2-5 ans, 5-10+ projets
    - Senior : 5-8+ ans, 10-20+ projets

    When both signals are available, the higher level is kept.
    """
    level_projects = _level_from_projects(projects_completed)
    if experience_years is None:
        return level_projects
    level_years = _level_from_years(max(0.0, experience_years))
    return _max_level(level_projects, level_years)


def experience_level_reason(
    *,
    level: str,
    projects_completed: int,
    experience_years: float | None = None,
    academic_level: str | None = None,
) -> str:
    normalized = normalize_level(level)
    label = level_label_fr(normalized)
    _ = academic_level

    years_part = ""
    if experience_years is not None and experience_years > 0:
        years_part = f"{experience_years} an(s) d'experience LinkedIn"

    projects_part = f"{projects_completed} projet(s) portfolio valide(s)"

    if experience_years is not None and experience_years > 0:
        return (
            f"Niveau {label} : {years_part}, {projects_part}. "
            f"Criteres : debutant (< {YEARS_INTERMEDIAIRE_MIN} ans ou < {PROJECTS_INTERMEDIAIRE_MIN} projets), "
            f"intermediaire ({YEARS_INTERMEDIAIRE_MIN}-{YEARS_SENIOR_MIN} ans ou {PROJECTS_INTERMEDIAIRE_MIN}+ projets), "
            f"senior ({YEARS_SENIOR_MIN}+ ans ou {PROJECTS_SENIOR_MIN}+ projets)."
        )

    if projects_completed == 0:
        return (
            f"Niveau {label} (junior) : aucun projet portfolio valide. "
            f"Analysez votre LinkedIn pour compter vos annees d'experience, "
            f"ou validez des projets dans Parametres > Portfolio."
        )
    if projects_completed < PROJECTS_INTERMEDIAIRE_MIN:
        remaining = PROJECTS_INTERMEDIAIRE_MIN - projects_completed
        return (
            f"Niveau {label} (junior) : {projects_part}. "
            f"Encore {remaining} pour atteindre Intermediaire ({PROJECTS_INTERMEDIAIRE_MIN}+)."
        )
    if projects_completed < PROJECTS_SENIOR_MIN:
        remaining = PROJECTS_SENIOR_MIN - projects_completed
        return (
            f"Niveau {label} : {projects_part}. "
            f"Encore {remaining} pour atteindre Senior ({PROJECTS_SENIOR_MIN}+)."
        )
    return (
        f"Niveau {label} : {projects_part} "
        f"(seuil senior : {PROJECTS_SENIOR_MIN}+)."
    )
