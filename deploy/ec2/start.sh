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

COMPOSE_FILES=(-f docker-compose.prod.yml)
if [[ "$has_firebase_file" == true ]]; then
  COMPOSE_FILES+=(-f docker-compose.prod.firebase-file.yml)
fi

echo ">> Build et demarrage (production)..."
docker compose "${COMPOSE_FILES[@]}" up -d --build

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
docker compose "${COMPOSE_FILES[@]}" logs --tail=80 backend
exit 1
