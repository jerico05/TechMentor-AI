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

db_url="$(grep -E '^DATABASE_URL=' backend/.env 2>/dev/null | tail -1 | cut -d= -f2- | tr -d ' \"' || true)"
if [[ -z "$db_url" ]]; then
  echo "Erreur: DATABASE_URL vide dans backend/.env"
  echo "  Sans DATABASE_URL explicite, le backend derive une URL vers postgres Docker (base vide)."
  echo "  Copiez vos URLs Neon depuis votre machine locale."
  exit 1
fi
if [[ "$uses_local_postgres" == false && "$db_url" == *"@postgres:"* ]]; then
  echo "Erreur: DATABASE_URL pointe vers @postgres mais le profile local-db est desactive."
  echo "  Vous risquez de lire une base Docker vide a chaque deploy."
  exit 1
fi
if [[ "$uses_local_postgres" == false ]]; then
  echo ">> DATABASE_URL: hote $(echo "$db_url" | sed -E 's|.*@([^/:]+).*|\1|')"
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

_ts() { date +%H:%M:%S; }

mem_mb="$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo 2>/dev/null || echo 0)"
swap_mb="$(awk '/^SwapTotal:/ {print int($2/1024)}' /proc/meminfo 2>/dev/null || echo 0)"
if [[ "$mem_mb" -gt 0 && "$mem_mb" -lt 2048 && "$swap_mb" -lt 512 ]]; then
  echo ">> Attention: ${mem_mb} Mo RAM, peu ou pas de swap."
  echo "   Le build Docker peut sembler bloque 10-20 min ou echouer (OOM)."
  echo "   Si ca plante: sudo bash deploy/ec2/ensure-swap.sh puis relancez."
fi

export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain
export COMPOSE_PARALLEL_LIMIT="${COMPOSE_PARALLEL_LIMIT:-2}"

echo ">> [$( _ts )] Pull images redis + qdrant..."
"${COMPOSE[@]}" pull redis qdrant

if [[ "${SKIP_BUILD:-0}" == "1" ]]; then
  echo ">> [$( _ts )] SKIP_BUILD=1: pas de rebuild backend."
else
  echo ">> [$( _ts )] Build image backend (5-20 min sur petit EC2, logs ci-dessous)..."
  "${COMPOSE[@]}" build --progress=plain backend
fi

echo ">> [$( _ts )] Demarrage des conteneurs..."
"${COMPOSE[@]}" up -d --no-build

echo ">> [$( _ts )] Attente API (migrations Alembic + uvicorn, jusqu'a 5 min)..."
live=false
for i in $(seq 1 150); do
  if curl -fsS --max-time 5 "http://127.0.0.1:${BACKEND_PORT}/health" >/dev/null 2>&1; then
    live=true
    echo ">> [$( _ts )] API live (/health OK)."
    break
  fi
  if (( i % 15 == 0 )); then
    echo ">>   ... en attente ($((i * 2))s) - etat conteneurs:"
    "${COMPOSE[@]}" ps
  fi
  sleep 2
done

if [[ "$live" != true ]]; then
  echo ">> Le backend ne repond pas. Etat des conteneurs:"
  "${COMPOSE[@]}" ps
  echo ">> Logs backend:"
  "${COMPOSE[@]}" logs --tail=120 backend
  exit 1
fi

echo ">> [$( _ts )] Verification readiness (DB + Redis + Qdrant)..."
if curl -fsS --max-time 15 "http://127.0.0.1:${BACKEND_PORT}/health/ready" | head -c 500; then
  echo
  echo ">> Backend pret."
  exit 0
fi

echo
echo ">> /health OK mais /health/ready lent ou en echec (RAG optionnel)."
echo ">> Verifiez: curl http://127.0.0.1:${BACKEND_PORT}/health/rag"
"${COMPOSE[@]}" ps
exit 0
