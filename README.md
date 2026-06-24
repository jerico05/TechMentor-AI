# TechMentor AI

> Plateforme intelligente de mentorat académique et professionnel pour les
> étudiants en informatique : analyse de profil, détection des lacunes,
> roadmap personnalisée et mentor IA contextuel.

![status](https://img.shields.io/badge/status-MVP%20complet-green)
![license](https://img.shields.io/badge/license-MIT-green)
![stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Next.js%20%7C%20Postgres%20%7C%20Qdrant-orange)

---

## 📑 Sommaire

- [Aperçu](#aperçu)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Démarrage rapide (Docker)](#démarrage-rapide-docker)
- [Démarrage sans Docker](#démarrage-sans-docker)
- [Structure du monorepo](#structure-du-monorepo)
- [Variables d'environnement](#variables-denvironnement)
- [Roadmap de développement](#roadmap-de-développement)
- [Qualité](#qualité)

---

## Aperçu

TechMentor AI accompagne un étudiant en informatique sur l'ensemble de son
parcours :

1. Crée un compte (email/mot de passe ou OAuth Google/GitHub).
2. Complète son profil étudiant (université, filière, objectif carrière).
3. Téléverse son CV (PDF/DOCX) - extraction automatique des compétences.
4. Connecte son GitHub - enrichissement du profil technique.
5. Choisit un métier cible (Backend, Data Scientist, Data Engineer, …).
6. Obtient une **skill gap analysis** + un **score** sur 100.
7. Reçoit une **roadmap personnalisée** mois par mois + des projets recommandés.
8. Échange avec un **mentor IA** contextuel (RAG sur une base de connaissances).
9. Passe des **quiz** d'évaluation et voit son score évoluer.

Le LLM est fourni par [**Mistral**](https://mistral.ai/) (`ministral-3b-latest`)
et les embeddings par [**Gemini**](https://ai.google.dev/) (`gemini-embedding-001`),
via des APIs OpenAI-compatible.

---

## Architecture

```
        ┌─────────────────────────────────────────┐
        │            Frontend (Next.js)            │
        │     App Router · TanStack Query · Zustand │
        └──────────────────┬──────────────────────┘
                           │ HTTPS (JWT Bearer)
                           ▼
        ┌─────────────────────────────────────────┐
        │            FastAPI (ASGI)                 │
        │  routers · services · repositories       │
        │  services/ (LLM) · rag/ (Qdrant + Gemini) │
        └───┬──────────┬──────────┬────────┬───────┘
            ▼          ▼          ▼        ▼
       PostgreSQL   Qdrant     Redis    Mistral
       (métier)    (RAG KB)   (cache,   (LLM) +
                               broker)   Gemini (embeddings)
```

Les tâches longues (parsing CV, fetch GitHub, indexing RAG) sont déléguées à un
worker **Celery** afin de garder les requêtes API rapides.

---

## Stack technique

| Couche | Choix |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript strict, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2, Celery |
| Base métier | PostgreSQL 16 |
| Vector DB | Qdrant (collection `kb_chunks`, 1536d) |
| Cache / broker | Redis 7 |
| LLM / embeddings | Mistral (LLM) + Gemini (embeddings) via SDK `openai` |
| Auth | JWT maison + OAuth Google & GitHub (Authlib) |
| Parsing CV | PyMuPDF, pdfplumber, python-docx |
| Conteneurs | Docker, Docker Compose |

---

## Démarrage rapide (Docker)

> Prérequis : Docker et Docker Compose v2.

```bash
# 1. Cloner puis préparer la configuration backend
git clone <repo-url> techmentor-ai
cd techmentor-ai
cp backend/.env.example backend/.env
#   → éditez au moins : SECRET_KEY, MISTRAL_API_KEY, GEMINI_API_KEY

# 2. Tout lancer
docker compose up -d --build

# 3. Vérifier que tout est sain
docker compose ps
curl http://localhost:8000/health/ready
```

| Service | URL |
|---|---|
| Frontend (Next.js) | <http://localhost:3000> |
| Backend (FastAPI, docs Swagger) | <http://localhost:8000/docs> |
| Qdrant dashboard | <http://localhost:6333/dashboard> |
| PostgreSQL | `localhost:5432` (user/db `techmentor`) |
| Redis | `localhost:6379` |

Arrêt : `docker compose down`.

**Attention base de données :**
- `docker compose down -v` **efface** le volume Postgres Docker local (pas Neon).
- `DATABASE_URL` dans `backend/.env` fait foi : ne pas l'écraser dans docker-compose.
- Local avec Neon : gardez vos URLs `neon.tech` dans `backend/.env`.
- Vérifier la base active : `curl http://localhost:8000/health/ready` (champs `database_host`, `database_users`).

---

## Démarrage sans Docker

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # renseigner SECRET_KEY + Mistral + Gemini

# Démarrez Postgres + Redis + Qdrant (locaux ou via docker compose up postgres redis qdrant)
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev                                          # http://localhost:3000
```

En dev, le frontend proxie `/api/*` vers `http://localhost:8000`.

---

## Structure du monorepo

```
techmentor-ai/
├── backend/                 # API FastAPI
│   ├── alembic/             # migrations (0001: users + student_profiles)
│   ├── app/
│   │   ├── api/             # routers (health + v1/profiles)
│   │   ├── core/            # config, security, deps, logging, exceptions
│   │   ├── database/        # async engine, session, declarative base
│   │   ├── models/          # User, StudentProfile
│   │   ├── schemas/         # Pydantic DTOs
│   │   ├── repositories/    # couche DAO async
│   │   └── main.py          # factory app()
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Next.js 14 App Router
│   ├── src/
│   │   ├── app/             # (auth) + (app) route groups
│   │   ├── components/      # ui/ (shadcn) + layout/
│   │   ├── lib/  services/  store/  types/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Variables d'environnement

- **Backend** : voir [`backend/.env.example`](backend/.env.example).
  Obligatoires au minimum : `SECRET_KEY`, `MISTRAL_API_KEY`, `GEMINI_API_KEY`.
- **Frontend** : voir [`frontend/.env.example`](frontend/.env.example).
  En dev, aucune valeur n'est requise (proxy local).

> ⚠️ Ne committez jamais vos `.env` réels. Ils sont ignorés par `.gitignore`.

---

## Roadmap de développement

| Phase | Contenu | Statut |
|---|---|---|
| **P1 - Infra** | Monorepo, Docker compose, FastAPI + Next.js scaffolds, Alembic | ✅ **Livré** |
| **P2 - Auth & Profil** | Firebase Auth, OAuth Google+GitHub, `student_profiles` | ✅ **Livré** |
| **P3 - Upload & Parsing CV** | Upload PDF/DOCX, extraction LLM (Celery) | ✅ **Livré** |
| **P4 - Référentiel** | Seed `skills` + 3 `career_paths` | ✅ **Livré** |
| **P5 - Gap & Score** | Skill gap analysis + score pondéré + niveau | ✅ **Livré** |
| **P6 - RAG KB** | Qdrant, ingestion roadmaps/certs/ressources statiques | ✅ **Livré** |
| **P7 - Roadmap IA** | Génération LLM mois par mois + reco projets | ✅ **Livré** |
| **P8 - Mentor IA** | Chat SSE streaming contextuel + historique | ✅ **Livré** |
| **P9 - Historique** | Timeline analyses/roadmaps/conversations/quiz | ✅ **Livré** |
| **P10 - Évaluation** | Quiz, réévaluation score, nouvelle roadmap auto | ✅ **Livré** |

---

## Qualité

Commandes locales utiles :

```bash
# Backend
cd backend && ruff check . && ruff format . && pytest

# Frontend
cd frontend && npm run lint && npm run type-check && npm run build
```

---

## Licence

MIT © TechMentor AI.
