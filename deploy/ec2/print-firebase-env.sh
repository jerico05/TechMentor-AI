#!/usr/bin/env bash
# Affiche FIREBASE_CREDENTIALS_JSON=... sur une ligne pour backend/.env (EC2).
# Usage : bash deploy/ec2/print-firebase-env.sh >> backend/.env
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="${1:-$ROOT/backend/firebase-service-account.json}"

if [[ ! -f "$SRC" ]]; then
  echo "Fichier introuvable: $SRC" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq requis: sudo apt install jq" >&2
  exit 1
fi

COMPACT="$(jq -c . "$SRC")"
echo "FIREBASE_CREDENTIALS_PATH="
echo "FIREBASE_CREDENTIALS_JSON=${COMPACT}"
