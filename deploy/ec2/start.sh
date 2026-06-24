#!/usr/bin/env bash
# Demarre le backend complet sur EC2 (PostgreSQL, Redis, Qdrant, API, Celery).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ ! -f backend/.env ]]; then
  echo "Erreur: backend/.env manquant."
  echo "  cp backend/.env.production.example backend/.env"
  echo "  puis editez les secrets (SECRET_KEY, POSTGRES_PASSWORD, API keys...)."
  exit 1
fi

has_firebase_file=false
has_firebase_json=false
[[ -f backend/firebase-service-account.json ]] && has_firebase_file=true
grep -qE '^FIREBASE_CREDENTIALS_JSON=.+' backend/.env 2>/dev/null && has_firebase_json=true

if [[ "$has_firebase_file" == false && "$has_firebase_json" == false ]]; then
  echo "Erreur: Firebase non configure."
  echo "  Option A : FIREBASE_CREDENTIALS_JSON dans backend/.env"
  echo "    bash deploy/ec2/print-firebase-env.sh"
  echo "  Option B : fichier sur EC2"
  echo "    bash deploy/ec2/upload-firebase.sh"
  exit 1
fi

# Docker Compose lit ${POSTGRES_PASSWORD} depuis --env-file (profile local-db seulement).
uses_local_postgres=false
if grep -qE '^DATABASE_URL=.*@(postgres|127\.0\.0\.1)' backend/.env 2>/dev/null; then
  uses_local_postgres=true
fi
if grep -qi 'neon' backend/.env 2>/dev/null; then
  uses_local_postgres=false
fi

if [[ "$uses_local_postgres" == true ]]; then
  if ! grep -qE '^POSTGRES_PASSWORD=.+' backend/.env; then
    echo "Erreur: POSTGRES_PASSWORD manquant dans backend/.env"
    echo "  nano backend/.env"
    exit 1
  fi
  export COMPOSE_PROFILES=local-db
else
  export COMPOSE_PROFILES=
  echo ">> Base externe detectee (Neon). Postgres Docker desactive."
fi

COMPOSE_FILES=(-f docker-compose.prod.yml)
if [[ "$has_firebase_file" == true ]]; then
  COMPOSE_FILES+=(-f docker-compose.prod.firebase-file.yml)
fi

COMPOSE=(docker compose --env-file backend/.env "${COMPOSE_FILES[@]}")

# BACKEND_PORT peut etre defini dans backend/.env
if [[ -z "${BACKEND_PORT:-}" ]] && grep -qE '^BACKEND_PORT=' backend/.env; then
  BACKEND_PORT="$(grep -E '^BACKEND_PORT=' backend/.env | tail -1 | cut -d= -f2- | tr -d ' \"')"
fi
BACKEND_PORT="${BACKEND_PORT:-8000}"

echo ">> Build et demarrage (production)..."
"${COMPOSE[@]}" up -d --build

echo ">> Attente sante API (port ${BACKEND_PORT})..."
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${BACKEND_PORT}/health/ready" >/dev/null 2>&1; then
    echo ">> Backend pret."
    curl -s "http://127.0.0.1:${BACKEND_PORT}/health/ready" | head -c 400
    echo
    exit 0
  fi
  sleep 2
done

echo ">> Le backend ne repond pas encore. Etat des conteneurs:"
"${COMPOSE[@]}" ps
echo ">> Logs backend:"
"${COMPOSE[@]}" logs --tail=80 backend
exit 1
