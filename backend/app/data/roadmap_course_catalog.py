"""Catalogue de formations avec URLs stables et verifiees manuellement."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogCourse:
    title: str
    platform: str
    url: str
    type: str
    skills: tuple[str, ...]
    careers: tuple[str, ...] = ()


# URLs stables (pages officielles, parcours reconnus). Ne pas inventer de liens profonds.
COURSE_CATALOG: tuple[CatalogCourse, ...] = (
    CatalogCourse(
        title="Scientific Computing with Python",
        platform="freeCodeCamp",
        url="https://www.freecodecamp.org/learn/scientific-computing-with-python/",
        type="gratuit",
        skills=("python", "programmation", "algorithmique"),
        careers=("backend-developer", "data-scientist", "data-engineer", "fullstack-developer"),
    ),
    CatalogCourse(
        title="Tutoriel Python officiel",
        platform="Python",
        url="https://docs.python.org/3/tutorial/",
        type="gratuit",
        skills=("python",),
        careers=("backend-developer", "data-scientist", "data-engineer"),
    ),
    CatalogCourse(
        title="Java Programming and Software Engineering",
        platform="Coursera",
        url="https://www.coursera.org/specializations/java-programming",
        type="freemium",
        skills=("java", "programmation"),
        careers=("backend-developer", "fullstack-developer"),
    ),
    CatalogCourse(
        title="Spring Boot Guides",
        platform="Spring",
        url="https://spring.io/guides",
        type="gratuit",
        skills=("spring", "spring boot", "java", "api", "rest"),
        careers=("backend-developer", "fullstack-developer"),
    ),
    CatalogCourse(
        title="FastAPI Tutorial",
        platform="FastAPI",
        url="https://fastapi.tiangolo.com/tutorial/",
        type="gratuit",
        skills=("fastapi", "python", "api", "rest"),
        careers=("backend-developer", "fullstack-developer"),
    ),
    CatalogCourse(
        title="SQLBolt - Interactive SQL",
        platform="SQLBolt",
        url="https://sqlbolt.com/",
        type="gratuit",
        skills=("sql", "base de donnees", "postgresql", "mysql"),
        careers=("backend-developer", "data-scientist", "data-engineer"),
    ),
    CatalogCourse(
        title="PostgreSQL Tutorial",
        platform="PostgreSQL",
        url="https://www.postgresql.org/docs/current/tutorial.html",
        type="gratuit",
        skills=("postgresql", "sql", "base de donnees"),
        careers=("backend-developer", "data-engineer"),
    ),
    CatalogCourse(
        title="Docker Get Started",
        platform="Docker",
        url="https://docs.docker.com/get-started/",
        type="gratuit",
        skills=("docker", "conteneur", "devops"),
        careers=("devops-engineer", "backend-developer", "data-engineer", "sre-engineer"),
    ),
    CatalogCourse(
        title="Learn Git Branching",
        platform="Learn Git Branching",
        url="https://learngitbranching.js.org/",
        type="gratuit",
        skills=("git", "github", "versioning"),
    ),
    CatalogCourse(
        title="Introduction to GitHub",
        platform="GitHub Skills",
        url="https://github.com/skills/introduction-to-github",
        type="gratuit",
        skills=("git", "github"),
    ),
    CatalogCourse(
        title="Kaggle Learn",
        platform="Kaggle",
        url="https://www.kaggle.com/learn",
        type="gratuit",
        skills=("data science", "machine learning", "pandas", "python"),
        careers=("data-scientist", "ml-engineer", "ai-engineer"),
    ),
    CatalogCourse(
        title="Scikit-learn Tutorial",
        platform="scikit-learn",
        url="https://scikit-learn.org/stable/tutorial/index.html",
        type="gratuit",
        skills=("machine learning", "scikit-learn", "python"),
        careers=("data-scientist", "ml-engineer"),
    ),
    CatalogCourse(
        title="Machine Learning Crash Course",
        platform="Google",
        url="https://developers.google.com/machine-learning/crash-course",
        type="gratuit",
        skills=("machine learning", "tensorflow", "deep learning"),
        careers=("data-scientist", "ml-engineer", "ai-engineer"),
    ),
    CatalogCourse(
        title="Responsive Web Design",
        platform="freeCodeCamp",
        url="https://www.freecodecamp.org/learn/2022/responsive-web-design/",
        type="gratuit",
        skills=("html", "css", "frontend", "web"),
        careers=("frontend-developer", "fullstack-developer", "ux-ui-designer"),
    ),
    CatalogCourse(
        title="React Documentation",
        platform="React",
        url="https://react.dev/learn",
        type="gratuit",
        skills=("react", "javascript", "frontend"),
        careers=("frontend-developer", "fullstack-developer"),
    ),
    CatalogCourse(
        title="The Odin Project - Full Stack",
        platform="The Odin Project",
        url="https://www.theodinproject.com/paths/full-stack-javascript",
        type="gratuit",
        skills=("javascript", "nodejs", "fullstack", "web"),
        careers=("fullstack-developer", "frontend-developer"),
    ),
    CatalogCourse(
        title="Kubernetes Basics",
        platform="Kubernetes",
        url="https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        type="gratuit",
        skills=("kubernetes", "k8s", "devops", "cloud"),
        careers=("devops-engineer", "sre-engineer", "cloud-architect"),
    ),
    CatalogCourse(
        title="AWS Skill Builder",
        platform="AWS",
        url="https://explore.skillbuilder.aws/learn",
        type="freemium",
        skills=("aws", "cloud", "devops"),
        careers=("cloud-architect", "devops-engineer", "sre-engineer"),
    ),
    CatalogCourse(
        title="Microsoft Azure Fundamentals",
        platform="Microsoft Learn",
        url="https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/",
        type="gratuit",
        skills=("azure", "cloud"),
        careers=("cloud-architect", "devops-engineer"),
    ),
    CatalogCourse(
        title="TryHackMe - Cyber Security",
        platform="TryHackMe",
        url="https://tryhackme.com/",
        type="freemium",
        skills=("cybersecurite", "securite", "pentest", "reseau"),
        careers=("cybersecurity-engineer",),
    ),
    CatalogCourse(
        title="ISTQB Foundation Level",
        platform="Guru99",
        url="https://www.guru99.com/software-testing.html",
        type="gratuit",
        skills=("test", "qa", "qualite", "testing"),
        careers=("qa-engineer",),
    ),
    CatalogCourse(
        title="LangChain Documentation",
        platform="LangChain",
        url="https://python.langchain.com/docs/tutorials/",
        type="gratuit",
        skills=("langchain", "llm", "rag", "prompt"),
        careers=("ai-engineer", "prompt-engineer", "ml-engineer"),
    ),
    CatalogCourse(
        title="Prompt Engineering Guide",
        platform="DAIR.AI",
        url="https://www.promptingguide.ai/",
        type="gratuit",
        skills=("prompt", "llm", "genai"),
        careers=("prompt-engineer", "ai-engineer"),
    ),
    CatalogCourse(
        title="Flutter Codelabs",
        platform="Google",
        url="https://docs.flutter.dev/codelabs",
        type="gratuit",
        skills=("flutter", "dart", "mobile"),
        careers=("mobile-developer",),
    ),
    CatalogCourse(
        title="Figma Learn",
        platform="Figma",
        url="https://www.figma.com/resource-library/",
        type="gratuit",
        skills=("figma", "ux", "ui", "design"),
        careers=("ux-ui-designer", "product-manager-tech"),
    ),
    # OpenClassrooms
    CatalogCourse(
        title="Apprenez les bases du langage Python",
        platform="OpenClassrooms",
        url="https://openclassrooms.com/fr/courses/7168876-apprenez-les-bases-du-langage-python",
        type="gratuit",
        skills=("python", "programmation"),
        careers=("backend-developer", "data-scientist", "data-engineer"),
    ),
    CatalogCourse(
        title="Parcours Developpeur web",
        platform="OpenClassrooms",
        url="https://openclassrooms.com/fr/paths/554-developpeur-web",
        type="freemium",
        skills=("html", "css", "javascript", "frontend", "web"),
        careers=("frontend-developer", "fullstack-developer"),
    ),
    CatalogCourse(
        title="Administrez vos bases de donnees avec SQL",
        platform="OpenClassrooms",
        url="https://openclassrooms.com/fr/courses/6573571-administrez-vos-bases-de-donnees-avec-sql",
        type="gratuit",
        skills=("sql", "base de donnees", "postgresql"),
        careers=("backend-developer", "data-engineer", "data-scientist"),
    ),
    CatalogCourse(
        title="Parcours Data Analyst",
        platform="OpenClassrooms",
        url="https://openclassrooms.com/fr/paths/793-data-analyst",
        type="freemium",
        skills=("data", "analyse", "python", "sql"),
        careers=("data-scientist", "data-engineer"),
    ),
    CatalogCourse(
        title="Parcours DevOps",
        platform="OpenClassrooms",
        url="https://openclassrooms.com/fr/paths/877-devops",
        type="freemium",
        skills=("devops", "docker", "ci/cd", "cloud"),
        careers=("devops-engineer", "sre-engineer"),
    ),
    # Cisco Networking Academy
    CatalogCourse(
        title="Python Essentials 1",
        platform="Cisco Networking Academy",
        url="https://www.netacad.com/courses/python-essentials-1",
        type="gratuit",
        skills=("python", "programmation"),
        careers=("backend-developer", "cybersecurity-engineer", "devops-engineer"),
    ),
    CatalogCourse(
        title="Introduction to Cybersecurity",
        platform="Cisco Networking Academy",
        url="https://www.netacad.com/courses/introduction-to-cybersecurity",
        type="gratuit",
        skills=("cybersecurite", "securite", "reseau"),
        careers=("cybersecurity-engineer",),
    ),
    CatalogCourse(
        title="CCNA Introduction to Networks",
        platform="Cisco Networking Academy",
        url="https://www.netacad.com/courses/networking-basics",
        type="gratuit",
        skills=("reseau", "networking", "tcp/ip"),
        careers=("cybersecurity-engineer", "devops-engineer", "sre-engineer"),
    ),
    # Udemy (cours gratuits / pages stables)
    CatalogCourse(
        title="Catalogue de cours gratuits Udemy",
        platform="Udemy",
        url="https://www.udemy.com/courses/free/",
        type="gratuit",
        skills=("programmation", "web", "python", "javascript"),
    ),
    CatalogCourse(
        title="Java Tutorial for Complete Beginners",
        platform="Udemy",
        url="https://www.udemy.com/course/java-tutorial/",
        type="gratuit",
        skills=("java", "programmation"),
        careers=("backend-developer", "fullstack-developer"),
    ),
    # edX / Harvard
    CatalogCourse(
        title="CS50 Introduction to Computer Science",
        platform="edX",
        url="https://www.edx.org/learn/computer-science/harvard-university-cs50-s-introduction-to-computer-science",
        type="freemium",
        skills=("programmation", "algorithmique", "c", "python"),
    ),
    # MDN
    CatalogCourse(
        title="Apprendre le developpement web",
        platform="MDN",
        url="https://developer.mozilla.org/fr/docs/Learn",
        type="gratuit",
        skills=("html", "css", "javascript", "frontend", "web"),
        careers=("frontend-developer", "fullstack-developer"),
    ),
    # Node.js
    CatalogCourse(
        title="Node.js Learn",
        platform="Node.js",
        url="https://nodejs.org/en/learn",
        type="gratuit",
        skills=("nodejs", "javascript", "backend"),
        careers=("backend-developer", "fullstack-developer"),
    ),
    # Apache Spark
    CatalogCourse(
        title="Spark Documentation",
        platform="Apache Spark",
        url="https://spark.apache.org/docs/latest/",
        type="gratuit",
        skills=("spark", "big data", "data engineer"),
        careers=("data-engineer",),
    ),
    # Terraform
    CatalogCourse(
        title="Terraform Tutorials",
        platform="HashiCorp",
        url="https://developer.hashicorp.com/terraform/tutorials",
        type="gratuit",
        skills=("terraform", "iac", "devops", "cloud"),
        careers=("devops-engineer", "cloud-architect", "sre-engineer"),
    ),
    # Product / Agile
    CatalogCourse(
        title="Agile Scrum Foundation",
        platform="OpenClassrooms",
        url="https://openclassrooms.com/fr/courses/4296701-decouvrez-les-methodes-agiles",
        type="gratuit",
        skills=("agile", "scrum", "product", "gestion de projet"),
        careers=("product-manager-tech",),
    ),
)


def _normalize(text: str) -> str:
    return text.lower().strip()


def _month_keywords(month: dict) -> set[str]:
    parts: list[str] = []
    for key in ("title", "summary"):
        parts.append(str(month.get(key) or ""))
    for skill in month.get("skills") or []:
        parts.append(str(skill))
    for action in month.get("actions") or []:
        parts.append(str(action))
    blob = _normalize(" ".join(parts))
    return {blob} | {_normalize(s) for s in parts if s}


def _score_course(course: CatalogCourse, keywords: set[str], career_slug: str) -> int:
    score = 0
    career_slug = _normalize(career_slug)
    if course.careers and career_slug in {_normalize(c) for c in course.careers}:
        score += 3
    for skill in course.skills:
        skill_n = _normalize(skill)
        for kw in keywords:
            if skill_n in kw or kw in skill_n:
                score += 2
                break
    return score


def pick_courses_for_month(
    month: dict,
    career_slug: str,
    *,
    limit: int = 2,
    exclude_urls: set[str] | None = None,
) -> list[dict]:
    """Retourne les meilleurs cours du catalogue pour un mois donne."""
    exclude = {_normalize(u) for u in (exclude_urls or set())}
    keywords = _month_keywords(month)
    ranked: list[tuple[int, CatalogCourse]] = []
    for course in COURSE_CATALOG:
        if _normalize(course.url) in exclude:
            continue
        score = _score_course(course, keywords, career_slug)
        if score > 0:
            ranked.append((score, course))
    ranked.sort(key=lambda x: (-x[0], x[1].title))
    if not ranked:
        for course in COURSE_CATALOG:
            if course.careers and career_slug in {_normalize(c) for c in course.careers}:
                ranked.append((1, course))
        ranked.sort(key=lambda x: x[1].title)
    picked: list[dict] = []
    for _, course in ranked:
        if len(picked) >= limit:
            break
        picked.append(
            {
                "title": course.title,
                "platform": course.platform,
                "url": course.url,
                "type": course.type,
                "note": "Ressource verifiee recommandee pour ce mois.",
            }
        )
    return picked


def format_catalog_for_prompt(career_slug: str, missing_skills: list[str]) -> str:
    """Liste courte de sources verifiees a injecter dans le prompt LLM."""
    fake_month = {
        "title": " ".join(missing_skills[:6]),
        "skills": missing_skills[:8],
        "actions": [],
    }
    courses = pick_courses_for_month(fake_month, career_slug, limit=12)
    if not courses:
        courses = [
            {
                "title": c.title,
                "platform": c.platform,
                "url": c.url,
                "type": c.type,
            }
            for c in COURSE_CATALOG[:8]
        ]
    lines = ["Sources verifiees (utilise UNIQUEMENT ces URLs si tu proposes un cours, sans les modifier) :"]
    for c in courses:
        lines.append(f'- {c["title"]} ({c["platform"]}) : {c["url"]} [{c["type"]}]')
    return "\n".join(lines)
