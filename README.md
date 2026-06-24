# TechMentor AI

Plateforme de mentorat académique et professionnel pour les étudiants en informatique. Analyse de profil, détection des lacunes, roadmap personnalisée et mentor IA contextuel.

[![Status](https://img.shields.io/badge/status-MVP%20complet-green)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Next.js%20%7C%20PostgreSQL%20%7C%20Qdrant-orange)]()

## Sommaire

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Démarrage avec Docker](#démarrage-avec-docker)
- [Démarrage sans Docker](#démarrage-sans-docker)
- [Structure du projet](#structure-du-projet)
- [Variables d'environnement](#variables-denvironnement)
- [Qualité et tests](#qualité-et-tests)
- [Documentation complémentaire](#documentation-complémentaire)
- [Licence](#licence)

## Présentation

TechMentor AI accompagne un étudiant en informatique tout au long de son parcours, de l'analyse de son profil jusqu'à la progression continue via un mentor IA.

Le moteur conversationnel s'appuie sur un LLM compatible OpenAI (Groq, Mistral, etc.) et sur Gemini pour les embeddings vectoriels.

## Fonctionnalités

| Domaine | Description |
|---------|-------------|
| Authentification | Firebase Auth (email, Google, GitHub) |
| Profil étudiant | Université, filière, objectif de carrière |
| CV | Upload PDF/DOCX, extraction automatique des compétences |
| GitHub | Enrichissement du profil technique |
| Analyse | Skill gap analysis et score sur 100 |
| Roadmap | Plan personnalisé mois par mois et projets recommandés |
| Mentor IA | Chat contextuel avec RAG (base de connaissances vectorielle) |
| Évaluation | Quiz, réévaluation du score et mise à jour de la roadmap |
| Historique | Timeline des analyses, roadmaps, conversations et quiz |

## Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (Next.js 14)              │
│     App Router · TanStack Query · Zustand    │
└─────────────────────┬───────────────────────┘
                      │ HTTPS / Firebase ID token
                      ▼
┌─────────────────────────────────────────────┐
│              Backend (FastAPI)               │
│   API REST · services · repositories · RAG   │
└───┬──────────┬──────────┬──────────┬────────┘
    ▼          ▼          ▼          ▼
PostgreSQL   Qdrant     Redis      LLM + Gemini
(métier)    (vecteurs)  (cache,    (chat +
                         broker)    embeddings)
```

Les traitements longs (parsing CV, synchronisation GitHub, indexation RAG) peuvent être délégués à un worker Celery afin de conserver des temps de réponse API courts.

## Stack technique

| Couche | Technologies |
|--------|--------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand |
| Backend | FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2, Celery |
| Base de données | PostgreSQL 16 (Neon ou conteneur Docker) |
| Base vectorielle | Qdrant (`kb_chunks`, 1536 dimensions) |
| Cache / broker | Redis 7 |
| IA | LLM compatible OpenAI (Groq / Mistral) + Gemini (embeddings) |
| Authentification | Firebase Auth (client) + Admin SDK (serveur) |
| Parsing CV | PyMuPDF, pdfplumber, python-docx |
| Conteneurisation | Docker, Docker Compose |

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose v2
- Clés API : LLM (`MISTRAL_API_KEY`) et embeddings (`GEMINI_API_KEY`)
- Projet [Firebase](https://console.firebase.google.com/) avec les providers Email, Google et GitHub activés
- Fichier `firebase-service-account.json` à la racine du dépôt

## Installation

```bash
git clone <repo-url> techmentor-ai
cd techmentor-ai

# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local

# Firebase (racine du projet)
# Placer firebase-service-account.json à la racine
```

Renseigner au minimum dans `backend/.env` :

- `SECRET_KEY`
- `MISTRAL_API_KEY` et `MISTRAL_BASE_URL`
- `GEMINI_API_KEY`
- `FIREBASE_PROJECT_ID`

Renseigner dans `frontend/.env.local` les variables `NEXT_PUBLIC_FIREBASE_*` (voir `frontend/.env.example`).

## Démarrage avec Docker

```bash
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health/ready
```

### Services exposés

| Service | URL / accès |
|---------|-------------|
| Frontend | http://localhost:3000 |
| Backend (Swagger) | http://localhost:8000/docs |
| Qdrant | http://localhost:6333/dashboard |
| PostgreSQL (Docker) | `localhost:15432` (user/db : `techmentor`) |
| Redis | `localhost:6379` |

### Worker Celery (optionnel)

Par défaut, le traitement CV est exécuté de manière synchrone (`CV_USE_CELERY=false`). Pour activer le worker :

```bash
docker compose --profile worker up -d
```

### Base de données

`DATABASE_URL` dans `backend/.env` fait foi. Deux configurations sont possibles :

| Mode | Configuration |
|------|---------------|
| Neon (cloud) | Conserver les URLs `neon.tech` dans `backend/.env` |
| Postgres Docker | `postgresql+asyncpg://techmentor:techmentor@127.0.0.1:15432/techmentor` |

Vérifier la base active :

```bash
curl http://localhost:8000/health/ready
# Champ database_host dans la réponse
```

> **Attention** : `docker compose down -v` supprime les volumes Docker locaux (données Postgres, Qdrant, Redis). Cela n'affecte pas une base Neon distante.

Arrêt des services :

```bash
docker compose down
```

## Démarrage sans Docker

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Démarrer Postgres, Redis et Qdrant (locaux ou via Docker)
docker compose up -d postgres redis qdrant

python -m alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

En développement, le frontend proxifie `/api/*` vers le backend via `BACKEND_URL` (voir `frontend/next.config.mjs`).

## Structure du projet

```
techmentor-ai/
├── backend/                    # API FastAPI
│   ├── alembic/                # Migrations de base de données
│   ├── app/
│   │   ├── api/                # Routeurs (health, v1/*)
│   │   ├── core/               # Config, sécurité, dépendances
│   │   ├── database/           # Moteur async, sessions
│   │   ├── models/             # Modèles SQLAlchemy
│   │   ├── schemas/            # DTOs Pydantic
│   │   ├── repositories/       # Couche d'accès aux données
│   │   ├── services/           # Logique métier et LLM
│   │   ├── rag/                # Ingestion et recherche vectorielle
│   │   └── workers/            # Tâches Celery
│   ├── tests/
│   └── Dockerfile
├── frontend/                   # Application Next.js
│   ├── src/
│   │   ├── app/                # App Router ((auth), (app))
│   │   ├── components/         # UI et layout
│   │   ├── lib/                # Utilitaires et configuration
│   │   ├── services/           # Clients API
│   │   ├── store/              # État client (Zustand)
│   │   └── types/              # Types TypeScript
│   └── Dockerfile.dev
├── deploy/                     # Scripts de déploiement
├── docker-compose.yml          # Stack de développement
├── docker-compose.prod.yml     # Stack de production
└── firebase-service-account.json
```

## Variables d'environnement

| Fichier | Rôle |
|---------|------|
| [`backend/.env.example`](backend/.env.example) | Configuration serveur (DB, Redis, Qdrant, LLM, Firebase) |
| [`frontend/.env.example`](frontend/.env.example) | Configuration client (Firebase, proxy API) |
| [`.env.docker.example`](.env.docker.example) | Variables optionnelles pour Docker Compose |

Ne jamais committer les fichiers `.env` réels. Ils sont exclus par `.gitignore`.

## Qualité et tests

### Backend

```bash
cd backend
ruff check .
ruff format .
pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run type-check
npm run build
```

## Documentation complémentaire

- [Backend](backend/README.md) : structure, commandes et endpoints d'authentification
- [Frontend](frontend/README.md) : structure, scripts et configuration Firebase
- [Plan de développement](plan.MD) : spécifications détaillées du MVP

## Licence

MIT - TechMentor AI.
