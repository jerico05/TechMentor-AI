"""Per-career project guidance for LLM prompts and fallbacks."""

from __future__ import annotations

# track drives UI badge + high-level project shape
CAREER_GUIDANCE: dict[str, dict] = {
    "ai-engineer": {
        "track": "ai",
        "prompt": """
Métier INGÉNIEUR IA — chaque projet doit refléter la stack GenAI moderne :
- RAG (Retrieval-Augmented Generation), embeddings, chunking, reranking.
- pgvector + PostgreSQL OU Qdrant/Chroma pour la base vectorielle.
- FastAPI ou LangChain / LlamaIndex pour l'orchestration.
- LLM (Mistral, OpenAI API, Ollama local) avec évaluation des réponses.
- data_sources : corpus documentaires réels (PDF techniques, docs open source, Wikipedia dumps,
  Hugging Face datasets textuels) avec URLs.
- impact : valeur produit (assistant interne, support client, copilote documentation).
- deliverables : API RAG, index vectoriel, métriques (faithfulness, latency), README architecture.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "DocMind — assistant RAG sur documentation technique",
                    "tagline": "Posez des questions à votre doc : pgvector + LLM en production",
                    "description": "Ingérez une base de docs (Markdown, PDF), chunking intelligent, embeddings via sentence-transformers, stockage pgvector dans PostgreSQL et API FastAPI avec streaming SSE. Ajoutez reranking et citations des sources.",
                    "track": "ai",
                    "difficulty": "avance",
                    "skills_practiced": ["RAG", "LLMs", "pgvector", "FastAPI"],
                    "estimated_weeks": 5,
                    "impact": "Projet phare en entretien IA : montre que vous savez livrer un RAG fiable, pas juste un chatbot.",
                    "stack": ["Python", "FastAPI", "PostgreSQL", "pgvector", "LangChain", "Mistral API"],
                    "data_sources": [
                        {
                            "name": "Hugging Face — databricks-dolly-15k",
                            "url": "https://huggingface.co/datasets/databricks/databricks-dolly-15k",
                            "note": "Corpus Q&A pour évaluer la qualité du RAG",
                        },
                        {
                            "name": "LangChain documentation (GitHub)",
                            "url": "https://github.com/langchain-ai/langchain/tree/master/docs",
                            "note": "Docs réelles à indexer pour le prototype",
                        },
                    ],
                    "deliverables": [
                        "Pipeline d'ingestion + index pgvector",
                        "API /chat/stream avec citations",
                        "Script d'évaluation RAG",
                        "Schéma d'architecture",
                    ],
                },
            ],
        },
    },
    "prompt-engineer": {
        "track": "ai",
        "prompt": """
Métier PROMPT ENGINEER — projets centrés GenAI appliquée :
- Optimisation de prompts, few-shot, chain-of-thought, évaluation systématique.
- RAG avec pgvector ou base vectorielle, tests A/B de prompts.
- Frameworks : LangChain, LlamaIndex, promptfoo ou équivalent.
- data_sources : datasets de QA, benchmarks (MT-Bench style), docs métier.
- deliverables : librairie de prompts versionnés, scores d'évaluation, rapport comparatif.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "PromptLab — benchmark et optimisation de prompts RAG",
                    "tagline": "Mesurez, comparez et améliorez vos prompts sur un vrai corpus",
                    "description": "Construisez un pipeline qui teste 10 variantes de prompts sur un jeu de questions, stocke les résultats dans PostgreSQL et visualisez precision@k et latence. Intégrez pgvector pour le retrieval.",
                    "track": "ai",
                    "difficulty": "avance",
                    "skills_practiced": ["RAG", "LLMs", "Prompt Engineering", "Évaluation"],
                    "estimated_weeks": 4,
                    "impact": "Démontre une approche ingénieur sur la GenAI, très recherchée en entreprise.",
                    "stack": ["Python", "LangChain", "PostgreSQL", "pgvector", "Streamlit"],
                    "data_sources": [
                        {
                            "name": "Hugging Face — truthful_qa",
                            "url": "https://huggingface.co/datasets/truthful_qa",
                            "note": "Benchmark pour tester la fidélité des réponses",
                        }
                    ],
                    "deliverables": ["Suite de prompts versionnés", "Dashboard de scores", "Rapport des meilleures configs"],
                },
            ],
        },
    },
    "ml-engineer": {
        "track": "ml",
        "prompt": """
Métier ML ENGINEER — industrialisation et déploiement :
- Serving de modèles (FastAPI, BentoML, TorchServe), MLflow, monitoring drift.
- Pipelines CI/CD pour entraînement et déploiement, Docker, Kubernetes si niveau avancé.
- data_sources : datasets ML classiques (Kaggle, UCI) pour le cas d'usage.
- impact : fiabilité production, observabilité, reproductibilité.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "MLServe — plateforme de déploiement de modèles",
                    "tagline": "De l'entraînement au endpoint monitoré en une pipeline",
                    "description": "Entraînez un modèle tabulaire ou NLP, versionnez avec MLflow, déployez via FastAPI containerisé et ajoutez monitoring Prometheus des prédictions et drift.",
                    "track": "ml",
                    "difficulty": "avance",
                    "skills_practiced": ["MLOps", "Docker", "Machine Learning", "Monitoring"],
                    "estimated_weeks": 6,
                    "impact": "Exactement le type de projet attendu d'un ML Engineer en production.",
                    "stack": ["Python", "MLflow", "FastAPI", "Docker", "Prometheus", "Scikit-learn"],
                    "data_sources": [
                        {
                            "name": "Kaggle — IEEE-CIS Fraud Detection",
                            "url": "https://www.kaggle.com/c/ieee-fraud-detection/data",
                            "note": "Dataset riche pour pipeline ML industriel",
                        }
                    ],
                    "deliverables": ["Pipeline MLflow", "API containerisée", "Dashboard Grafana", "Runbook incident"],
                },
            ],
        },
    },
    "data-scientist": {
        "track": "data",
        "prompt": """
Métier DATA SCIENTIST — analyse, modélisation, storytelling :
- Chaque projet inclut data_sources réelles (Kaggle, data.gouv.fr, Hugging Face, UCI).
- Pipeline : EDA, feature engineering, modèle, interprétabilité (SHAP), visualisation.
- deliverables : notebook reproductible, rapport métier, dashboard optionnel.
""",
        "fallbacks": {},
    },
    "data-engineer": {
        "track": "data",
        "prompt": """
Métier DATA ENGINEER — pipelines et infrastructure données :
- ETL/ELT, Airflow ou Dagster, Spark si pertinent, warehousing (PostgreSQL, BigQuery-like).
- data_sources : APIs ouvertes, fichiers CSV massifs, streams (OpenAQ, data.gouv.fr).
- impact : fiabilité, fraîcheur des données, alerting.
""",
        "fallbacks": {},
    },
    "backend-developer": {
        "track": "backend",
        "prompt": """
Métier BACKEND DEVELOPER — APIs robustes et services métier :
- REST ou GraphQL, auth JWT/OAuth, PostgreSQL, cache Redis, tests d'intégration.
- Patterns : clean architecture, pagination, rate limiting, observabilité.
- impact : produit scalable, API documentée OpenAPI, prête pour la prod.
- Pas de data_sources sauf si le projet en nécessite (liste vide sinon).
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "EventHub API — gestion d'événements à grande échelle",
                    "tagline": "API Spring Boot ou FastAPI avec auth, cache et files d'attente",
                    "description": "Créez une API de réservation d'événements : authentification, PostgreSQL, Redis pour le cache, RabbitMQ pour les notifications async et tests d'intégration complets.",
                    "track": "backend",
                    "difficulty": "avance",
                    "skills_practiced": ["Spring Boot", "SQL", "Redis", "Docker"],
                    "estimated_weeks": 5,
                    "impact": "Montre une vraie culture backend production-ready.",
                    "stack": ["Java", "Spring Boot", "PostgreSQL", "Redis", "Docker"],
                    "data_sources": [],
                    "deliverables": ["API OpenAPI", "Tests intégration", "Docker Compose", "CI pipeline"],
                },
            ],
        },
    },
    "frontend-developer": {
        "track": "frontend",
        "prompt": """
Métier FRONTEND DEVELOPER — UI moderne et performante :
- React/Next.js, TypeScript strict, accessibilité WCAG, animations soignées.
- State management, tests (Vitest, Playwright), performance (Lighthouse > 90).
- impact : portfolio visuel fort, UX soignée, responsive mobile-first.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "PulseUI — design system et app showcase",
                    "tagline": "Un design system documenté + app démo qui en fait la vitrine",
                    "description": "Construisez un design system (tokens, composants Storybook), une app dashboard consommatrice et des tests e2e Playwright. Optimisez pour Lighthouse et accessibilité clavier.",
                    "track": "frontend",
                    "difficulty": "avance",
                    "skills_practiced": ["React", "TypeScript", "CSS", "Testing"],
                    "estimated_weeks": 5,
                    "impact": "Portfolio frontend premium : recruteurs jugent en 10 secondes — celui-ci accroche.",
                    "stack": ["Next.js", "TypeScript", "Tailwind CSS", "Storybook", "Playwright"],
                    "data_sources": [],
                    "deliverables": ["Design system Storybook", "App déployée", "Rapport Lighthouse", "Tests e2e"],
                },
            ],
        },
    },
    "fullstack-developer": {
        "track": "fullstack",
        "prompt": """
Métier FULLSTACK DEVELOPER — produit bout-en-bout :
- Front React/Next.js + API (Node ou FastAPI), auth complète, BDD relationnelle.
- Déploiement Docker, CI/CD basique, README soigné.
- impact : produit utilisable en démo live, valeur métier claire.
""",
        "fallbacks": {},
    },
    "mobile-developer": {
        "track": "mobile",
        "prompt": """
Métier DÉVELOPPEUR MOBILE — apps iOS/Android ou cross-platform :
- React Native ou Flutter, intégration API REST, stockage local, notifications push.
- UX mobile native (gestures, offline-first si pertinent), tests sur device.
- impact : app déployable (TestFlight / Play Console internal), démo vidéo.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "FitTrack — coach fitness cross-platform",
                    "tagline": "App React Native avec sync offline et notifications",
                    "description": "Créez une app de suivi d'entraînement : auth Firebase, API REST, cache offline AsyncStorage, notifications push et UI fluide avec animations Reanimated.",
                    "track": "mobile",
                    "difficulty": "avance",
                    "skills_practiced": ["React Native", "Firebase", "REST APIs", "Testing"],
                    "estimated_weeks": 6,
                    "impact": "Une app mobile complète vaut mieux que dix tutos — montrez-la en entretien.",
                    "stack": ["React Native", "TypeScript", "Firebase", "Expo"],
                    "data_sources": [],
                    "deliverables": ["App iOS/Android", "Backend API", "Vidéo démo", "README setup"],
                },
            ],
        },
    },
    "devops-engineer": {
        "track": "devops",
        "prompt": """
Métier DEVOPS ENGINEER — automatisation et fiabilité :
- CI/CD (GitHub Actions, GitLab CI), Docker, Kubernetes, Terraform ou Pulumi.
- Infrastructure as Code, secrets management, pipelines multi-environnements.
- impact : réduction du time-to-deploy, rollback automatique, monitoring.
- data_sources : généralement vide ; focus infra et outillage.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "GitOps K8s — déploiement zéro-downtime",
                    "tagline": "Pipeline complet Terraform + K8s + ArgoCD",
                    "description": "Provisionnez un cluster (kind/minikube), déployez une app via Helm, configurez ArgoCD pour le GitOps et GitHub Actions pour CI. Ajoutez rollback et smoke tests post-deploy.",
                    "track": "devops",
                    "difficulty": "avance",
                    "skills_practiced": ["Kubernetes", "CI/CD", "Terraform", "Docker"],
                    "estimated_weeks": 5,
                    "impact": "Projet DevOps concret que les SRE/DevOps lead reconnaissent immédiatement.",
                    "stack": ["Terraform", "Kubernetes", "ArgoCD", "GitHub Actions", "Helm"],
                    "data_sources": [],
                    "deliverables": ["Repo infra IaC", "Pipeline CI/CD", "Doc runbook", "Diagramme architecture"],
                },
            ],
        },
    },
    "cloud-architect": {
        "track": "cloud",
        "prompt": """
Métier ARCHITECTE CLOUD — architecture scalable et sécurisée :
- AWS/GCP/Azure : VPC, load balancers, auto-scaling, CDN, IAM least-privilege.
- Terraform modules réutilisables, haute dispo multi-AZ, estimation des coûts.
- impact : architecture documentée (diagrammes), sécurité et résilience justifiées.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "CloudScale — architecture 3-tiers résiliente sur AWS",
                    "tagline": "Terraform + ALB + ECS + RDS Multi-AZ",
                    "description": "Concevez et déployez une archi 3-tiers sur AWS avec Terraform : VPC, ALB, ECS Fargate, RDS PostgreSQL Multi-AZ, S3 static hosting et CloudWatch alarms.",
                    "track": "cloud",
                    "difficulty": "avance",
                    "skills_practiced": ["AWS", "Terraform", "Networking", "Security"],
                    "estimated_weeks": 6,
                    "impact": "Case study d'architecte : diagrammes + code IaC + justification des choix.",
                    "stack": ["AWS", "Terraform", "ECS", "RDS", "CloudWatch"],
                    "data_sources": [],
                    "deliverables": ["Modules Terraform", "Diagrammes C4", "Estimation coûts", "Checklist sécurité"],
                },
            ],
        },
    },
    "sre-engineer": {
        "track": "devops",
        "prompt": """
Métier SRE — observabilité, SLOs et fiabilité :
- Prometheus, Grafana, OpenTelemetry, alerting PagerDuty-style.
- SLO/SLI, error budgets, chaos engineering léger, runbooks.
- impact : réduction MTTR, dashboards actionnables, postmortems blamesless.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "ObserveStack — plateforme d'observabilité complète",
                    "tagline": "Métriques, logs, traces et SLOs sur une app démo",
                    "description": "Instrumentez une API avec OpenTelemetry, collectez via Prometheus et Loki, visualisez dans Grafana et définissez des SLOs avec alertes. Simulez une panne et rédigez un postmortem.",
                    "track": "devops",
                    "difficulty": "avance",
                    "skills_practiced": ["Monitoring", "Kubernetes", "Python", "CI/CD"],
                    "estimated_weeks": 5,
                    "impact": "Les équipes SRE cherchent exactement ce profil orienté fiabilité mesurable.",
                    "stack": ["Prometheus", "Grafana", "OpenTelemetry", "Docker", "FastAPI"],
                    "data_sources": [],
                    "deliverables": ["Dashboards Grafana", "SLO definitions", "Runbook", "Postmortem exemple"],
                },
            ],
        },
    },
    "cybersecurity-engineer": {
        "track": "security",
        "prompt": """
Métier CYBERSÉCURITÉ — défense et audit :
- Pentest lab (DVWA, WebGoat), analyse de vulnérabilités OWASP Top 10.
- SIEM léger, durcissement Linux, scripts Python d'audit.
- data_sources : CVE databases, logs synthétiques, datasets réseau (CICIDS, etc.).
- impact : rapport d'audit professionnel, preuves de correction.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "SecureScan — scanner de vulnérabilités web automatisé",
                    "tagline": "Détectez OWASP Top 10 et générez un rapport PDF",
                    "description": "Développez un scanner qui teste une app vulnérable (DVWA) : injection SQL, XSS, headers sécurité. Produisez un rapport avec CVSS et recommandations de correction.",
                    "track": "security",
                    "difficulty": "avance",
                    "skills_practiced": ["Penetration Testing", "Python", "Security", "Linux"],
                    "estimated_weeks": 5,
                    "impact": "Portfolio cybersécurité crédible avec livrable rapport, pas juste des CTF.",
                    "stack": ["Python", "Docker", "DVWA", "Nmap", "ReportLab"],
                    "data_sources": [
                        {
                            "name": "OWASP Juice Shop",
                            "url": "https://owasp.org/www-project-juice-shop/",
                            "note": "Application volontairement vulnérable pour tests",
                        },
                        {
                            "name": "NVD — CVE Database",
                            "url": "https://nvd.nist.gov/",
                            "note": "Référence CVE pour scorer les vulnérabilités",
                        },
                    ],
                    "deliverables": ["Scanner automatisé", "Rapport PDF", "Guide de remédiation", "Lab Docker"],
                },
            ],
        },
    },
    "qa-engineer": {
        "track": "qa",
        "prompt": """
Métier QA / TEST — qualité et automatisation :
- Tests e2e (Cypress, Playwright), API testing, CI intégration tests.
- Stratégie de tests (pyramide), coverage, tests de charge légers (k6).
- impact : réduction des bugs en prod, pipeline qualité bloquant.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "QualityGate — framework de tests e2e + CI",
                    "tagline": "Bloquez les merges si les tests critiques échouent",
                    "description": "Sur une app open source, écrivez 30+ tests Playwright, tests API Postman/Newman, intégrez dans GitHub Actions et publiez un rapport Allure.",
                    "track": "qa",
                    "difficulty": "avance",
                    "skills_practiced": ["Testing", "Cypress", "CI/CD", "SQL"],
                    "estimated_weeks": 4,
                    "impact": "Montre que vous pensez qualité comme un ingénieur, pas comme un exécutant de scripts.",
                    "stack": ["Playwright", "GitHub Actions", "Allure", "Postman", "Docker"],
                    "data_sources": [],
                    "deliverables": ["Suite tests e2e", "Pipeline CI", "Rapport Allure", "Matrice de couverture"],
                },
            ],
        },
    },
    "product-manager-tech": {
        "track": "product",
        "prompt": """
Métier PRODUCT MANAGER TECH — vision produit et livrables stratégiques :
- PAS de code lourd : PRD, roadmap, user stories, métriques North Star, wireframes.
- data_sources : données marché (App Annie, statistiques publiques, enquêtes).
- impact : problème utilisateur validé, business case, priorisation RICE/ICE.
- deliverables : PRD, roadmap trimestrielle, prototype Figma, dashboard métriques SQL.
""",
        "fallbacks": {
            "avance": [
                {
                    "title": "LaunchPad — PRD et roadmap d'un SaaS B2B",
                    "tagline": "De l'idée au plan produit validé par des données",
                    "description": "Identifiez un problème B2B, interviewez 5 utilisateurs potentiels, rédigez un PRD complet, construisez une roadmap 6 mois et un dashboard SQL de métriques fictives mais réalistes.",
                    "track": "product",
                    "difficulty": "avance",
                    "skills_practiced": ["Roadmapping", "Analytics", "UX", "Agile"],
                    "estimated_weeks": 4,
                    "impact": "Portfolio PM crédible : recruteurs lisent le PRD avant tout.",
                    "stack": ["Notion", "Figma", "SQL", "Google Sheets"],
                    "data_sources": [
                        {
                            "name": "data.gouv.fr — Statistiques entreprises",
                            "url": "https://www.data.gouv.fr/",
                            "note": "Données pour valider le marché adressable",
                        }
                    ],
                    "deliverables": ["PRD 10 pages", "Roadmap priorisée", "Wireframes Figma", "Dashboard métriques"],
                },
            ],
        },
    },
    "ux-ui-designer": {
        "track": "design",
        "prompt": """
Métier UX/UI DESIGNER — expérience et interfaces :
- Case studies complets : recherche, wireframes, design system, prototype haute fidélité.
- Tests utilisateurs (5 sessions min), accessibilité couleurs/contrastes.
- impact : résultats mesurables (réduction friction, NPS simulé).
""",
        "fallbacks": {},
    },
}

DEFAULT_GUIDANCE = {
    "track": "dev",
    "prompt": """
Propose des projets alignés sur le métier cible, avec stack moderne du domaine.
Chaque projet doit avoir un impact portfolio clair et des livrables concrets.
Inclure data_sources avec URLs réelles si le métier manipule des données (data, IA, sécurité, produit).
""",
    "fallbacks": {},
}


def get_career_guidance(slug: str) -> dict:
    return CAREER_GUIDANCE.get(slug, DEFAULT_GUIDANCE)
