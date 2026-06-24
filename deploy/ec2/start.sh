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

if [[ ! -f backend/firebase-service-account.json ]]; then
  echo "Erreur: backend/firebase-service-account.json manquant."
  exit 1
fi

echo ">> Build et demarrage (production)..."
docker compose -f docker-compose.prod.yml up -d --build

echo ">> Attente sante API..."
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${BACKEND_PORT:-8000}/health/ready" >/dev/null 2>&1; then
    echo ">> Backend pret."
    curl -s "http://127.0.0.1:${BACKEND_PORT:-8000}/health/ready" | head -c 400
    echo
    exit 0
  fi
  sleep 2
done

echo ">> Le backend ne repond pas encore. Logs:"
docker compose -f docker-compose.prod.yml logs --tail=80 backend
exit 1
