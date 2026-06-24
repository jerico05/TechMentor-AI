#!/usr/bin/env bash
# Deploy rapide: pas de build EC2, skip pull si images deja en cache.
# Requiert: image GHCR (workflow GitHub) OU image locale techmentor-backend:prod
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec env USE_REGISTRY=1 SKIP_PULL_IF_PRESENT=1 bash "$ROOT/deploy/ec2/start.sh" "$@"
