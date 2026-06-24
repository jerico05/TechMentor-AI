#!/usr/bin/env bash
# Connexion GHCR sur EC2 (une fois) pour pull l'image backend pre-construite.
# Creer un PAT GitHub : Settings > Developer settings > PAT > read:packages
set -euo pipefail

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Usage: GITHUB_TOKEN=ghp_xxx bash deploy/ec2/login-ghcr.sh"
  echo "  PAT avec scope read:packages (ou rendez le package public sur github.com/users/jerico05/packages)"
  exit 1
fi

echo "$GITHUB_TOKEN" | docker login ghcr.io -u jerico05 --password-stdin
echo ">> Connecte a ghcr.io. Relancez: bash deploy/ec2/start.sh"
