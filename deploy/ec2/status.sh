#!/usr/bin/env bash
# Diagnostic rapide quand le deploy semble bloque.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

COMPOSE_FILES=(-f docker-compose.prod.yml)
[[ -f backend/firebase-service-account.json ]] && COMPOSE_FILES+=(-f docker-compose.prod.firebase-file.yml)
COMPOSE=(docker compose --env-file backend/.env "${COMPOSE_FILES[@]}")

BACKEND_PORT="${BACKEND_PORT:-8000}"
grep -qE '^BACKEND_PORT=' backend/.env 2>/dev/null && \
  BACKEND_PORT="$(grep -E '^BACKEND_PORT=' backend/.env | tail -1 | cut -d= -f2- | tr -d ' \"')"

echo "=== Memoire ==="
free -h 2>/dev/null || true
echo
echo "=== Docker build en cours? ==="
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' 2>/dev/null || true
pgrep -a docker-buildx 2>/dev/null || pgrep -a "docker compose" 2>/dev/null || echo "(aucun process build visible)"
echo
echo "=== Compose ps ==="
"${COMPOSE[@]}" ps 2>/dev/null || true
echo
echo "=== Derniers logs backend ==="
"${COMPOSE[@]}" logs --tail=40 backend 2>/dev/null || true
echo
echo "=== Health local ==="
curl -fsS --max-time 5 "http://127.0.0.1:${BACKEND_PORT}/health" && echo || echo "/health: pas de reponse"
curl -fsS --max-time 10 "http://127.0.0.1:${BACKEND_PORT}/health/ready" && echo || echo "/health/ready: pas de reponse"
