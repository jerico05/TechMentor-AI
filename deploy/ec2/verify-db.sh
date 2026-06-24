#!/usr/bin/env bash
# Affiche quelle base PostgreSQL le backend utilise (sans exposer les secrets).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

BACKEND_PORT="${BACKEND_PORT:-8000}"
if [[ -f backend/.env ]] && grep -qE '^BACKEND_PORT=' backend/.env; then
  BACKEND_PORT="$(grep -E '^BACKEND_PORT=' backend/.env | tail -1 | cut -d= -f2- | tr -d ' \"')"
fi

echo ">> DATABASE_URL dans backend/.env :"
if grep -qE '^DATABASE_URL=' backend/.env 2>/dev/null; then
  db_url="$(grep -E '^DATABASE_URL=' backend/.env | tail -1 | cut -d= -f2- | tr -d ' \"')"
  host="$(echo "$db_url" | sed -E 's|.*@([^/:]+).*|\1|')"
  echo "   hote: $host"
else
  echo "   (absent - le backend derivra postgres Docker, base potentiellement vide)"
fi

echo ""
echo ">> Sante API (port ${BACKEND_PORT}) :"
if curl -fsS "http://127.0.0.1:${BACKEND_PORT}/health/ready" 2>/dev/null; then
  echo ""
else
  echo "   backend inaccessible sur 127.0.0.1:${BACKEND_PORT}"
  exit 1
fi
