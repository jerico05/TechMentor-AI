#!/usr/bin/env bash
# Copie firebase-service-account.json vers EC2 via SCP (hors GitHub).
#
# Usage :
#   export EC2_HOST=ubuntu@1.2.3.4
#   export EC2_KEY=~/.ssh/techmentor.pem   # optionnel
#   bash deploy/ec2/upload-firebase.sh
#
# Puis sur EC2, lancer avec le fichier :
#   docker compose -f docker-compose.prod.yml -f docker-compose.prod.firebase-file.yml up -d
#
# Alternative sans fichier : mettre FIREBASE_CREDENTIALS_JSON dans backend/.env
#   jq -c . backend/firebase-service-account.json
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="${1:-$ROOT/backend/firebase-service-account.json}"
EC2_HOST="${EC2_HOST:?Definir EC2_HOST=ubuntu@IP_EC2}"
REMOTE_DIR="${REMOTE_DIR:-~/TechMentor-AI/backend}"

if [[ ! -f "$SRC" ]]; then
  echo "Fichier introuvable: $SRC"
  exit 1
fi

SCP_OPTS=(-o StrictHostKeyChecking=accept-new)
if [[ -n "${EC2_KEY:-}" ]]; then
  SCP_OPTS+=(-i "$EC2_KEY")
fi

echo ">> Envoi vers ${EC2_HOST}:${REMOTE_DIR}/firebase-service-account.json"
ssh "${SCP_OPTS[@]}" "$EC2_HOST" "mkdir -p ${REMOTE_DIR}"
scp "${SCP_OPTS[@]}" "$SRC" "${EC2_HOST}:${REMOTE_DIR}/firebase-service-account.json"
ssh "${SCP_OPTS[@]}" "$EC2_HOST" "chmod 600 ${REMOTE_DIR}/firebase-service-account.json"

echo ">> OK. Sur EC2 :"
echo "   cd TechMentor-AI"
echo "   docker compose -f docker-compose.prod.yml -f docker-compose.prod.firebase-file.yml up -d --build"
