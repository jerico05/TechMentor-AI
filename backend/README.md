# TechMentor AI - Backend

FastAPI application exposing the TechMentor AI API. Async SQLAlchemy 2, Alembic
migrations, Pydantic v2, Celery workers, LangChain, Mistral + Gemini.

## Layout

```
backend/
├── alembic/                 # Migrations
├── app/
│   ├── api/                 # Routers (health + v1/*)
│   ├── core/                # config, security, deps, logging, exceptions
│   ├── database/            # async engine, session, declarative base
│   ├── models/              # SQLAlchemy ORM
│   ├── schemas/             # Pydantic DTOs
│   ├── repositories/        # async data-access layer
│   └── main.py              # app factory
├── docker/                  # Dockerfile context, entrypoint
├── tests/                   # pytest + pytest-asyncio
├── requirements.txt
├── pyproject.toml           # ruff / mypy / pytest config
└── .env.example
```

## Local dev (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit secrets (SECRET_KEY, MISTRAL_API_KEY, GEMINI_API_KEY)

# Migrations (use python -m if `alembic` is not on PATH)
python -m alembic upgrade head

# Port 8001 - évite le conflit si une autre app (ex. AgriInsight) utilise le 8000
python -m uvicorn app.main:app --reload --port 8001
```

API docs: <http://localhost:8000/docs>

## Useful commands

| Task | Command |
|------|---------|
| Run migrations | `alembic upgrade head` |
| Create migration | `alembic revision --autogenerate -m "msg"` |
| Run tests | `pytest` |
| Lint | `ruff check .` |
| Format | `ruff format .` |
| Type-check | `mypy app` |
| Run worker | `celery -A app.workers.celery_app worker -l info` |

## Phase 1 deliverables

This backend scaffold ships:
- ✅ FastAPI app factory with CORS, GZip, structured logging, typed exceptions
- ✅ Health & readiness endpoints (`/health`, `/health/ready`)
- ✅ PostgreSQL async session + Alembic with the `0001` migration (`users`, `student_profiles`)
- ✅ `User` + `StudentProfile` models, repositories, schemas
- ✅ `/api/v1/profiles/me` CRUD endpoints
- ✅ Password hashing (bcrypt) + JWT helpers (access / refresh / reset)
- ✅ Smoke tests (health, config, security)

Phases 2-10 will mount additional routers under `app/api/v1/`.

## Firebase Auth (Phase 2)

Authentication is delegated to **Firebase Auth** on the client. The backend
verifies Firebase ID tokens via the Admin SDK and syncs a local `users` row.

1. Create a Firebase project and enable **Email/Password**, **Google** and **GitHub** providers.
2. Download the service-account JSON → `backend/firebase-service-account.json`.
3. Set `FIREBASE_PROJECT_ID` and `FIREBASE_CREDENTIALS_PATH` in `backend/.env`.
4. Copy `frontend/.env.example` → `frontend/.env.local` and fill `NEXT_PUBLIC_FIREBASE_*`.
5. Run `alembic upgrade head` (migration `0002` adds `firebase_uid`).

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/session` | Sync Firebase user → local DB |
| GET | `/api/v1/auth/me` | Current user profile |
